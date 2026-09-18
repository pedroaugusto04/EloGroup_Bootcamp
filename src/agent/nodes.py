"""
src/agent/nodes.py
Nós do grafo LangGraph para o copiloto de estoque: orquestração de fatos determinísticos e revisão.
"""

import logging
from typing import Any, Dict, List

import json
from src.agent.constants import DEFAULT_PLAN_STEPS, VIOLATION_DISCONTINUED_MSG
from src.agent.deterministic_checks import run_deterministic_checks
from src.agent.inventory_analytics import build_audit_package
from src.agent.prompts import CONSOLIDATOR_EXECUTIVE_PROMPT, PLANNER_SYSTEM_PROMPT
from src.agent.report_generator import generate_inventory_audit_report
from src.agent.state import InventoryAgentState
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.llm import get_llm
from src.utils.json_parser import extract_json_from_llm_response
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger("vertice.inventory_agent")

# Aliases para retrocompatibilidade com mocks ou testes existentes
_deterministic_checks = run_deterministic_checks
_report = generate_inventory_audit_report


def _build_llm_evidence_summary(package: Dict[str, Any]) -> str:
    """Prepara um resumo conciso e estruturado dos fatos para o LLM raciocinar."""
    summary = package.get("summary", {})
    cap = summary.get("capital", {})
    op = summary.get("operational", {})
    exp = summary.get("lead_time_exposure", {})
    liq = summary.get("liquidation", {})
    central_liq = liq.get("central_scenario", {})
    categories = summary.get("category_summary", [])
    top_suppliers = summary.get("supplier_exposure_summary", [])[:5]
    top_items = package.get("items", [])[:5]

    evidence = {
        "periodo": package.get("meta", {}).get("period_key", "full_history"),
        "dias_observados": package.get("meta", {}).get("days"),
        "capital": {
            "capital_disponivel_coberto": cap.get("capital_disponivel"),
            "capital_descontinuado_imobilizado": cap.get("capital_disponivel_descontinuado"),
            "skus_descontinuados_valorados": cap.get("descontinuados_valorados"),
        },
        "operacional": {
            "rupturas_imediatas": op.get("ruptura_atual"),
            "skus_no_ponto_pedido": op.get("ponto_pedido"),
            "skus_expostos_lead_time": exp.get("skus"),
            "margem_exposta_lead_time": exp.get("margem_potencialmente_exposta"),
            "skus_alta_cobertura": op.get("alta_cobertura"),
            "dias_cobertura_limite": op.get("coverage_threshold_days"),
            "skus_sem_venda_observada": op.get("sem_venda_observada"),
            "capital_excedente_sobre_estoque": op.get("capital_excedente"),
            "unidades_excedentes_sobre_estoque": op.get("unidades_excedentes"),
        },
        "simulacao_desova_descontinuados": {
            "desconto_pct": liq.get("desconto_pct"),
            "sell_through_central_pct": central_liq.get("sell_through_pct"),
            "contribuicao_liquida_estimada": central_liq.get("contribuicao_estimada"),
            "receita_liquida_estimada": central_liq.get("receita_ajustada_devolucoes"),
            "categoria_lider_desova": (liq.get("central_by_category") or [{}])[0],
        },
        "categorias_mais_criticas": [
            {
                "categoria": c.get("categoria"),
                "rupturas": c.get("ruptura_atual"),
                "expostos_lead_time": c.get("exposicao_lead_time"),
                "margem_exposta": c.get("margem_potencialmente_exposta"),
                "alta_cobertura": c.get("alta_cobertura"),
                "capital_excedente": c.get("capital_excedente"),
            }
            for c in categories
        ],
        "top_fornecedores_em_risco": [
            {
                "fornecedor": f.get("fornecedor_id"),
                "skus_expostos": f.get("skus_expostos"),
                "margem_exposta": f.get("margem_potencialmente_exposta"),
            }
            for f in top_suppliers
        ],
        "amostra_skus_criticos": [
            {
                "sku_id": i.get("sku_id"),
                "produto": i.get("nome_produto"),
                "categoria": i.get("categoria"),
                "margem_exposta": i.get("margem_potencialmente_exposta"),
            }
            for i in top_items
        ],
    }
    return json.dumps(evidence, ensure_ascii=False, indent=2)


def planner_node(state: InventoryAgentState) -> Dict[str, Any]:
    """Inicializa o plano canônico estruturado de auditoria executiva (4 pilares metodológicos)."""
    plan = [dict(step) for step in DEFAULT_PLAN_STEPS]
    return {"plan": plan, "current_step_index": 0, "observations": [], "revision_count": 0}


def executor_node(state: InventoryAgentState) -> Dict[str, Any]:
    """Executa a etapa atual do plano de auditoria."""
    index = state["current_step_index"]
    plan = [dict(step) for step in state["plan"]]
    if index >= len(plan):
        return {}
    plan[index]["status"] = "completed"
    plan[index]["result"] = "Etapa preparada para consolidação factual reproduzível."
    return {"plan": plan, "observations": [{"step": plan[index]["step_id"], "status": "completed"}]}


def replanner_node(state: InventoryAgentState) -> Dict[str, Any]:
    """Avança o ponteiro de execução do plano."""
    return {"current_step_index": state["current_step_index"] + 1}


def consolidator_node(state: InventoryAgentState) -> Dict[str, Any]:
    """Consolida o pacote de auditoria e invoca o LLM para analisar os fatos e formular recomendações."""
    package = state.get("factual_package")
    if not package:
        package = build_audit_package(DuckDBRepository(), state.get("period_key", "full_history"))
    checks = run_deterministic_checks(package)
    approved = all(checks.values())

    recommendations: List[dict] = []
    llm_status = "not_used"

    llm = get_llm()
    if llm:
        try:
            evidence_summary = _build_llm_evidence_summary(package)
            prompt = CONSOLIDATOR_EXECUTIVE_PROMPT.format(factual_summary=evidence_summary)
            critic_feedback = state.get("critic_feedback")
            revision_count = int(state.get("revision_count", 0))
            if critic_feedback and revision_count > 0 and not state.get("critic_approved", True):
                prompt += (
                    f"\n\nATENÇÃO (REVISÃO REQUERIDA - TENTATIVA {revision_count + 1}):\n"
                    f"O rascunho anterior foi rejeitado pela auditoria com o seguinte apontamento:\n"
                    f"\"{critic_feedback}\"\n"
                    f"Corrija estritamente essa questão sem violar os guardrails de negócio "
                    f"(nunca sugira compras ou reposição para produtos descontinuados)."
                )
            response = llm.invoke([HumanMessage(content=prompt)])
            response_text = getattr(response, "content", response)
            parsed = extract_json_from_llm_response(response_text)

            if parsed and isinstance(parsed, dict):
                recs = parsed.get("recommendations")
                if isinstance(recs, list) and len(recs) > 0:
                    recommendations = recs
                if parsed.get("executive_summary"):
                    package["agent_executive_summary"] = str(parsed["executive_summary"])
                elif parsed.get("feedback"):
                    package["agent_executive_summary"] = str(parsed["feedback"])
                if parsed.get("next_steps_text"):
                    package["agent_next_steps"] = str(parsed["next_steps_text"])
                llm_status = "completed"
            elif response_text and isinstance(response_text, str) and len(response_text.strip()) > 30:
                package["agent_executive_summary"] = response_text.strip()
                llm_status = "completed"

            # Se o LLM gerou o parecer mas as recomendações vieram vazias,
            # alinha as recomendações às iniciativas prioritárias com evidências factuais
            if not recommendations and package.get("summary", {}).get("decision_matrix"):
                recommendations = [
                    {
                        "horizon": row.get("horizon", "30 dias"),
                        "type": row.get("type", "Quick Win" if "30" in str(row.get("horizon")) else "Estrutural"),
                        "initiative": row.get("initiative", "Iniciativa"),
                        "recommendation": row.get("decision", ""),
                        "evidence": ", ".join(row.get("evidence", [])),
                        "confidence": "Alta",
                        "caveat": row.get("decision_gate", "Validação executiva requerida"),
                        "financial_impact": row.get("financial_value"),
                    }
                    for row in package["summary"]["decision_matrix"]
                ]
        except Exception as exc:
            logger.warning("Falha ao invocar LLM no consolidator_node: %s", exc)
            llm_status = "error"

    report = generate_inventory_audit_report(package, recommendations)

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
    """Aplica guardrails de conteúdo e validação final contra regras de negócio."""
    draft = state.get("draft_report") or ""
    checks = dict(state.get("deterministic_checks") or {})
    forbidden = ("comprar descontinuado", "repor descontinuado", "emitir ordem de compra")
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


__all__ = [
    "get_llm",
    "_deterministic_checks",
    "_report",
    "planner_node",
    "executor_node",
    "replanner_node",
    "consolidator_node",
    "critic_node",
]
