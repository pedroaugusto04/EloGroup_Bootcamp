"""Nós do grafo: fatos determinísticos e complemento opcional do LLM."""

import json
import logging
import re
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from src.agent.constants import DEFAULT_PLAN_STEPS, VIOLATION_DISCONTINUED_MSG
from src.agent.inventory_analytics import build_audit_package
from src.agent.state import InventoryAgentState
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.llm import get_llm
from src.utils.json_parser import extract_json_from_llm_response

logger = logging.getLogger("vertice.inventory_agent")


def _brl(value: Any) -> str:
    if value is None:
        return "não disponível"
    return "R$ " + f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _deterministic_checks(package: dict) -> Dict[str, bool]:
    meta = package["meta"]
    summary = package["summary"]
    capital = summary["capital"]
    exposure = summary["lead_time_exposure"]
    operational = summary["operational"]
    tolerance = 0.02
    checks = {
        "typed_period": meta["period_key"] in {"full_history", "calendar_2023", "last_90d_observed"},
        "financial_source_is_sales": meta["financial_source"] == "vendas",
        "operational_source_is_stock": meta["operational_source"] == "estoque",
        "stock_reconciliation": abs(
            float(capital.get("capital_fisico") or 0)
            - float(capital.get("capital_reservado") or 0)
            - float(capital.get("capital_disponivel") or 0)
        ) <= tolerance,
        "financial_coverage_reconciled": (
            int(capital.get("skus_com_custo_vendas") or 0)
            + int(capital.get("skus_sem_custo_vendas") or 0)
            == int(capital.get("total_skus") or 0)
        ),
        "discontinued_never_replenished": all(
            not item.get("is_descontinuado") for item in package.get("queues", {}).get("investigacao_reposicao", [])
        ),
        "exposure_count_reconciled": int(exposure["skus"]) == int(operational["investigacao_reposicao"]),
        "data_quality_approved": summary["data_quality"]["blocking_errors"] == 0,
        "liquidation_has_four_scenarios": len(summary["liquidation"]["scenarios"]) == 4,
        "lead_time_formulas_reconciled": summary["reconciliation"]["exposure_formulas_valid"],
        "liquidation_formulas_reconciled": summary["reconciliation"]["liquidation_scenarios_proportional"],
    }
    return checks


def _report(package: dict, recommendations: List[dict]) -> str:
    meta, summary = package["meta"], package["summary"]
    cap = summary["capital"]
    op = summary["operational"]
    exp = summary["lead_time_exposure"]
    central = summary["liquidation"]["central_scenario"]
    top = summary.get("top_attention_category") or {}
    lines = [
        "# Copiloto de estoque baseado em tendência histórica de vendas",
        "",
        f"> {summary['methodology_banner']}",
        "",
        "## Síntese factual",
        "",
        f"- Capital físico coberto: **{_brl(cap['capital_fisico'])}**; reservado: **{_brl(cap['capital_reservado'])}**; disponível/liquidável: **{_brl(cap['capital_disponivel'])}**.",
        f"- Cobertura financeira: **{cap['skus_com_custo_vendas']} de {cap['total_skus']} SKUs**; {cap['skus_sem_custo_vendas']} ficaram fora do valuation por ausência de custo válido em Vendas.",
        f"- Posição operacional: **{op['ruptura_atual']} rupturas atuais**, **{op['ponto_pedido']}** saldos positivos no/abaixo do ponto e **{op['sem_venda_observada']}** SKUs sem venda aprovada observada.",
        f"- Exposição no lead time cadastral: **{exp['skus']} SKUs ativos**, com {_brl(exp['receita_ajustada_devolucao'])} de receita e {_brl(exp['margem_potencialmente_exposta'])} de margem potencialmente expostas.",
        f"- Categoria com maior atenção no critério de exposição: **{top.get('categoria', 'não disponível')}**.",
        "",
        "Esses valores de exposição são um cenário secundário de priorização baseado na tendência histórica; não são perda realizada nem previsão atual.",
        "",
        "## Liquidação de descontinuados — cenário central",
        "",
        f"Com 30% de desconto e 50% de sell-through: **{central['unidades_cenario']:,.0f} unidades**, {_brl(central['capital_historico_envolvido'])} de capital histórico envolvido, {_brl(central['receita_antes_devolucoes'])} antes de devoluções, {_brl(central['receita_ajustada_devolucoes'])} após ajuste e {_brl(central['contribuicao_estimada'])} de contribuição estimada.",
        "",
        "A simulação não modela retorno físico. Impostos, comissões, logística reversa e elasticidade de preço não estão disponíveis.",
        "",
        "## Encaminhamentos 30/60/90 dias",
        "",
        "- **30 dias:** investigar os SKUs ativos priorizados por margem exposta; submeter descontinuados à análise de liquidação, sem reposição.",
        "- **60 dias:** revisar pontos de pedido, compras e cadastros dos sinais de alta cobertura; alta cobertura não é diagnóstico definitivo de excesso.",
        "- **90 dias:** formalizar a data de snapshot do estoque e medir lead time realizado antes de automatizar decisões de abastecimento.",
    ]
    if recommendations:
        lines.extend(["", "## Hipóteses complementares do copiloto", ""])
        for rec in recommendations:
            lines.append(
                f"- **{rec['horizon']} — {rec['recommendation']}** Evidência: `{rec['evidence']}`. "
                f"Confiança: {rec['confidence']}. Ressalva: {rec['caveat']}"
            )
    return "\n".join(lines)


def _llm_recommendations(package: dict) -> tuple[List[dict], str]:
    llm = get_llm()
    if not llm:
        return [], "unavailable"
    prompt = {
        "meta": package["meta"],
        "operational": package["summary"]["operational"],
        "lead_time_exposure": package["summary"]["lead_time_exposure"],
        "top_attention_category": package["summary"]["top_attention_category"],
    }
    try:
        response = llm.invoke([
            SystemMessage(content=(
                "Retorne somente JSON no formato {\"recommendations\": [...]}. Cada item deve conter "
                "horizon (30/60/90 dias), recommendation, evidence (caminho do JSON recebido), "
                "confidence (baixa/média/alta) e caveat. Não crie números, ordens ou quantidades de compra."
            )),
            HumanMessage(content=json.dumps(prompt, ensure_ascii=False)),
        ])
        payload = extract_json_from_llm_response(str(response.content)) or {}
        valid = []
        for item in payload.get("recommendations", []):
            if not isinstance(item, dict):
                continue
            required = {"horizon", "recommendation", "evidence", "confidence", "caveat"}
            if (required <= item.keys()
                    and item["confidence"] in {"baixa", "média", "alta"}
                    and str(item["horizon"]).lower() in {"30 dias", "60 dias", "90 dias"}):
                text = str(item["recommendation"]).lower()
                caveat = str(item["caveat"]).lower()
                # Fatos numéricos pertencem ao pacote determinístico, nunca ao texto livre do LLM.
                creates_financial_fact = bool(re.search(r"r\$|\d", text + " " + caveat))
                if (not creates_financial_fact and "ordem de compra" not in text
                        and "comprar descontinuado" not in text and "repor descontinuado" not in text):
                    valid.append({key: str(item[key]) for key in required})
        return valid, "included" if valid else "omitted_invalid_contract"
    except Exception as exc:
        logger.warning("Complemento LLM omitido: %s", exc)
        return [], "unavailable"


def planner_node(state: InventoryAgentState) -> Dict[str, Any]:
    plan = [dict(step) for step in DEFAULT_PLAN_STEPS]
    return {"plan": plan, "current_step_index": 0, "observations": [], "revision_count": 0}


def executor_node(state: InventoryAgentState) -> Dict[str, Any]:
    index = state["current_step_index"]
    plan = [dict(step) for step in state["plan"]]
    if index >= len(plan):
        return {}
    plan[index]["status"] = "completed"
    plan[index]["result"] = "Etapa preparada para consolidação factual reproduzível."
    return {"plan": plan, "observations": [{"step": plan[index]["step_id"], "status": "completed"}]}


def replanner_node(state: InventoryAgentState) -> Dict[str, Any]:
    return {"current_step_index": state["current_step_index"] + 1}


def consolidator_node(state: InventoryAgentState) -> Dict[str, Any]:
    package = build_audit_package(DuckDBRepository(), state.get("period_key", "full_history"))
    recommendations, llm_status = _llm_recommendations(package)
    checks = _deterministic_checks(package)
    approved = all(checks.values())
    report = _report(package, recommendations)
    return {
        "factual_package": package,
        "structured_data": package["summary"],
        "recommendations": recommendations,
        "draft_report": report,
        "deterministic_checks": checks,
        "deterministic_approved": approved,
        "llm_complement_status": llm_status,
    }


def critic_node(state: InventoryAgentState) -> Dict[str, Any]:
    draft = state.get("draft_report") or ""
    checks = dict(state.get("deterministic_checks") or {})
    forbidden = ("comprar descontinuado", "repor descontinuado", "emitir ordem de compra", "lucro cessante")
    content_ok = not any(term in draft.lower() for term in forbidden)
    if not content_ok:
        checks["content_guardrails"] = False
    approved = bool(checks) and all(checks.values()) and content_ok
    feedback = "Checks determinísticos aprovados." if approved else VIOLATION_DISCONTINUED_MSG
    return {
        "critic_approved": approved,
        "critic_reviewed": True,
        "critic_feedback": feedback,
        "deterministic_checks": checks,
        "deterministic_approved": approved,
        "revision_count": int(state.get("revision_count", 0)) + 1,
        "final_report": draft if approved else None,
    }
