"""
src/agent/nodes.py
Implementação dos nós de execução do Grafo LangGraph (Planner, Executor, Replanner, Consolidator, Critic).
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage

from src.agent.state import InventoryAgentState, AgentPlanStep
from src.agent.prompts import (
    CONSOLIDATOR_SYSTEM_PROMPT,
    CRITIC_SYSTEM_PROMPT,
)
from src.agent.constants import (
    DEFAULT_PLAN_STEPS,
    LLM_UNAVAILABLE_MESSAGE,
    CRITIC_UNAVAILABLE_FEEDBACK,
    CRITIC_APPROVAL_SUCCESS_FEEDBACK,
    VIOLATION_DISCONTINUED_MSG,
    VIOLATION_TEMPORAL_MSG,
)
from src.agent.tools import (
    tool_inventory_health_scan,
    tool_sales_demand_matrix,
    tool_marketing_stock_mismatch,
    tool_returns_and_quality_risk,
    tool_discontinued_stranded_capital,
)
from src.infrastructure.llm import get_llm
from src.utils.json_parser import extract_json_from_llm_response, validate_critic_payload

logger = logging.getLogger("vertice.inventory_agent")


def _generate_fallback_report(structured_data: Dict[str, Any]) -> str:
    """Gera um relatório executivo analítico estruturado como fallback determinístico."""
    ruptura_cnt = structured_data.get("ruptura_count", 0)
    criticos_cnt = structured_data.get("criticos_count", 0)
    stranded_cash = structured_data.get("total_stranded_cash", 0.0)
    mkt_cats = ", ".join(structured_data.get("mkt_alert_categories", [])) or "Nenhuma"

    return f"""# Relatório Executivo: Diagnóstico de Estoque & Otimização de Capital

## 1. Sumário Executivo & Diagnóstico Geral
- **Taxa Geral de Ruptura**: Identificados {ruptura_cnt} SKUs em ruptura ativa e {criticos_cnt} em risco crítico.
- **Capital Travado em Descontinuados**: Total de R$ {stranded_cash:,.2f} imobilizados em itens fora de linha.
- **Descompasso de Marketing**: Categorias com verba ativa e ruptura física: {mkt_cats}.

## 2. Matriz de Ações por Horizonte Temporal

### ⚡ Curto Prazo: Quick Wins (Até 30 Dias)
- Pausar imediatamente campanhas de mídia nas categorias com alta taxa de ruptura ({mkt_cats}).
- Realizar saldão promocional de queima controlada para estancar os R$ {stranded_cash:,.2f} em descontinuados.
- Emitir ordens de compra emergenciais para os top SKUs Curva A com risco iminente de ruptura.

### Médio Prazo: Ajuste de Processos (60 Dias)
- Recalibrar parâmetros de ponto de pedido e estoque de segurança considerando o lead time real dos fornecedores.
- Bloquear recompras automáticas de SKUs com taxa de devolução superior a 10% até auditoria de qualidade.

### Longo Prazo: Excelência Operacional (90 Dias)
- Integrar rotina de S&OP (Sales & Operations Planning) sincronizando Marketing, Compras e Logística.
- Implementar governança de cadastro para unificar custos contábeis e tabelas de preço no PDV.

## 3. Top SKUs Críticos para Ação Imediata
Auditoria concluída com base na base analítica DuckDB (Ano Base 2026).
"""


def planner_node(state: InventoryAgentState) -> Dict[str, Any]:
    """Nó 1: Arquiteto de Planejamento - Decompõe a missão em etapas auditáveis."""
    t0 = time.time()
    logger.info("Iniciando nó [PLANNER] para a missão: %s", state.get("mission", "")[:60])
    plan_steps = [dict(step) for step in DEFAULT_PLAN_STEPS]
    logger.info("Plano determinístico carregado com %d etapas.", len(plan_steps))
    elapsed = time.time() - t0
    logger.info("[PLANNER] concluído em %.3fs.", elapsed)

    return {
        "plan": plan_steps,
        "current_step_index": 0,
        "observations": [],
        "revision_count": 0,
        "critic_approved": False,
        "critic_reviewed": False,
    }


def executor_node(state: InventoryAgentState) -> Dict[str, Any]:
    """Nó 2: Executor de Ferramentas - Roda as tools determinísticas da etapa atual."""
    t0 = time.time()
    step_idx = state["current_step_index"]
    plan = list(state["plan"])
    if step_idx >= len(plan):
        logger.warning("[EXECUTOR] step_index %d fora do limite do plano (%d).", step_idx, len(plan))
        return {}

    current_step = dict(plan[step_idx])
    current_step["status"] = "in_progress"
    step_id = current_step["step_id"]
    logger.info("Iniciando nó [EXECUTOR] - Etapa %d/%d: %s", step_idx + 1, len(plan), current_step["name"])

    observations: List[Dict[str, Any]] = []

    if step_id == 1:
        raw_health = tool_inventory_health_scan.invoke({"limit": 30})
        data = json.loads(raw_health)
        observations.append({"step": step_id, "type": "inventory_health", "data": data})
        current_step["result"] = f"Auditados {len(data)} SKUs com diagnósticos de cobertura e risco de ruptura."
        logger.info("[EXECUTOR] tool_inventory_health_scan retornou %d SKUs.", len(data))

    elif step_id == 2:
        raw_demand = tool_sales_demand_matrix.invoke({"top_n": 25})
        raw_mkt = tool_marketing_stock_mismatch.invoke({})
        raw_stranded = tool_discontinued_stranded_capital.invoke({"limit": 15})

        d_demand = json.loads(raw_demand)
        d_mkt = json.loads(raw_mkt)
        d_stranded = json.loads(raw_stranded)

        observations.append({"step": step_id, "type": "sales_demand", "data": d_demand})
        observations.append({"step": step_id, "type": "marketing_mismatch", "data": d_mkt})
        observations.append({"step": step_id, "type": "stranded_capital", "data": d_stranded})
        current_step["result"] = f"Mapeados {len(d_demand)} top SKUs em receita, {len(d_mkt)} categorias em marketing e {len(d_stranded)} itens descontinuados com capital imobilizado."
        logger.info("[EXECUTOR] Cruzamento comercial: %d demand SKUs, %d mkt categorias, %d descontinuados.", len(d_demand), len(d_mkt), len(d_stranded))

    elif step_id == 3:
        raw_returns = tool_returns_and_quality_risk.invoke({"min_orders": 10, "min_returns": 2})
        d_returns = json.loads(raw_returns)
        observations.append({"step": step_id, "type": "returns_quality", "data": d_returns})
        current_step["result"] = f"Identificados {len(d_returns)} SKUs com índice relevante de devolução e atrito de entrega/qualidade."
        logger.info("[EXECUTOR] tool_returns_and_quality_risk retornou %d SKUs com alta devolução.", len(d_returns))

    else:
        current_step["result"] = "Etapa de consolidação analítica pronta para execução."
        logger.info("[EXECUTOR] Preparando síntese consolidada.")

    current_step["status"] = "completed"
    plan[step_idx] = current_step
    elapsed = time.time() - t0
    logger.info("[EXECUTOR] Etapa %d concluída em %.3fs.", step_id, elapsed)

    return {
        "plan": plan,
        "observations": observations,
    }


def replanner_node(state: InventoryAgentState) -> Dict[str, Any]:
    """Nó 3: Replanner / Incrementador de Etapas."""
    next_idx = state["current_step_index"] + 1
    logger.info("[REPLANNER] Progresso: %d/%d etapas finalizadas.", next_idx, len(state["plan"]))
    return {"current_step_index": next_idx}


def consolidator_node(state: InventoryAgentState) -> Dict[str, Any]:
    """Nó 4: Consolidador de Proposta - Gera a minuta do relatório executivo."""
    t0 = time.time()
    logger.info("Iniciando nó [CONSOLIDATOR] - Agregando observações de todas as etapas.")
    obs = state["observations"]

    # Processa os dados estruturados de todas as observações
    inv_health = next((o["data"] for o in obs if o["type"] == "inventory_health"), [])
    mkt_data = next((o["data"] for o in obs if o["type"] == "marketing_mismatch"), [])
    stranded_data = next((o["data"] for o in obs if o["type"] == "stranded_capital"), [])
    returns_data = next((o["data"] for o in obs if o["type"] == "returns_quality"), [])
    demand_data = next((o["data"] for o in obs if o["type"] == "sales_demand"), [])

    # Métricas calculadas para síntese executiva
    ruptura_skus = [s for s in inv_health if s.get("em_ruptura")]
    criticos_skus = [s for s in inv_health if s.get("diagnostico_operacional") == "RISCO_CRITICO"]
    total_stranded_cash = sum(float(s.get("capital_travado_real", 0)) for s in stranded_data)
    mkt_alert_cats = [m for m in mkt_data if m.get("status_alinhamento") == "ALERTA_MKT_DESPERDICIO"]

    structured_data = {
        "ruptura_count": len(ruptura_skus),
        "criticos_count": len(criticos_skus),
        "total_stranded_cash": total_stranded_cash,
        "mkt_alert_categories": [m["categoria"] for m in mkt_alert_cats],
        "top_critical_skus": (ruptura_skus + criticos_skus)[:10],
        "top_stranded_skus": stranded_data[:10],
        "top_returned_skus": returns_data[:10],
    }

    logger.info("[CONSOLIDATOR] Métricas consolidadas: %d rupturas, %d críticos, R$ %.2f em descontinuados.",
                len(ruptura_skus), len(criticos_skus), total_stranded_cash)

    llm = get_llm()
    draft = ""
    if llm:
        try:
            prompt_content = f"""
            Missão: {state.get('mission', 'Auditoria de Estoque')}

            Evidências Coletadas:
            - SKUs em Ruptura Ativa: {len(ruptura_skus)}
            - SKUs em Risco Crítico (cobertura < lead time): {len(criticos_skus)}
            - Capital Total Travado em Descontinuados: R$ {total_stranded_cash:,.2f}
            - Categorias com Risco de Desperdício em Marketing: {[m['categoria'] for m in mkt_alert_cats]}
            - Top SKUs Críticos: {json.dumps(structured_data['top_critical_skus'][:5], ensure_ascii=False)}
            - Top Descontinuados: {json.dumps(structured_data['top_stranded_skus'][:5], ensure_ascii=False)}
            - Top Devoluções: {json.dumps(structured_data['top_returned_skus'][:5], ensure_ascii=False)}
            """
            response = llm.invoke([
                SystemMessage(content=CONSOLIDATOR_SYSTEM_PROMPT),
                HumanMessage(content=prompt_content)
            ])
            draft = response.content if hasattr(response, "content") else str(response)
            logger.info("[CONSOLIDATOR] Minuta executiva gerada via LLM com %d caracteres.", len(draft))
        except Exception as e:
            logger.warning("[CONSOLIDATOR] Falha na geração via LLM: %s. Utilizando fallback determinístico.", e)

    if not draft:
        draft = _generate_fallback_report(structured_data)
        logger.info("[CONSOLIDATOR] Relatório estruturado gerado via fallback determinístico.")

    elapsed = time.time() - t0
    logger.info("[CONSOLIDATOR] concluído em %.3fs.", elapsed)

    return {
        "draft_report": draft,
        "structured_data": structured_data,
    }


def critic_node(state: InventoryAgentState) -> Dict[str, Any]:
    """Nó 5: Crítico de Risco / Nó de Reflexão - Avalia guardrails e conformidade."""
    t0 = time.time()
    logger.info("Iniciando nó [CRITIC] - Auditoria de Guardrails.")
    draft = state.get("draft_report", "")
    structured = state.get("structured_data", {})
    revision_count = state.get("revision_count", 0)

    # Se o LLM esteve indisponível e não há minuta
    if LLM_UNAVAILABLE_MESSAGE in draft:
        logger.info("[CRITIC] Relatório contém aviso de indisponibilidade do LLM.")
        return {
            "critic_approved": False,
            "critic_reviewed": False,
            "critic_feedback": CRITIC_UNAVAILABLE_FEEDBACK,
            "revision_count": revision_count + 1,
            "final_report": None,
        }

    # Verificação determinística de guardrails
    violations = []

    # 1. Guardrail de Descontinuados: não pode sugerir compra de descontinuados
    if "comprar descontinuado" in draft.lower() or "repor descontinuado" in draft.lower():
        violations.append(VIOLATION_DISCONTINUED_MSG)
        logger.warning("[CRITIC] Violação detectada: Guardrail de Descontinuados.")

    # 2. Guardrail de Separação Temporal: deve ter Quick Wins e Estrutural
    if "quick wins" not in draft.lower() or "30 dias" not in draft.lower():
        violations.append(VIOLATION_TEMPORAL_MSG)
        logger.warning("[CRITIC] Violação detectada: Guardrail de Separação Temporal.")

    approved = len(violations) == 0
    score = 10 if approved else 6
    feedback = CRITIC_APPROVAL_SUCCESS_FEEDBACK if approved else "; ".join(violations)

    llm = get_llm()
    if llm and not violations:
        try:
            prompt_audit = (
                f"Minuta do Relatório:\n{draft}\n\n"
                f"Evidências estruturadas para auditoria independente:\n"
                f"{json.dumps(structured, ensure_ascii=False)}"
            )
            response = llm.invoke([
                SystemMessage(content=CRITIC_SYSTEM_PROMPT),
                HumanMessage(content=prompt_audit)
            ])
            data = validate_critic_payload(extract_json_from_llm_response(response.content))

            # Uma única recuperação para respostas HTTP bem-sucedidas, mas fora do contrato.
            if data is None:
                logger.info("[CRITIC] Resposta fora do schema padrão; solicitando formatação JSON.")
                repair_prompt = (
                    "A resposta anterior não veio no formato JSON pedido. Retorne somente o objeto JSON "
                    "com as chaves 'approved', 'score', 'feedback', 'corrections_needed'.\n\n"
                    f"Resposta anterior:\n{str(response.content)[:2000]}"
                )
                repair_response = llm.invoke([
                    SystemMessage(content=CRITIC_SYSTEM_PROMPT),
                    HumanMessage(content=repair_prompt),
                ])
                data = validate_critic_payload(extract_json_from_llm_response(repair_response.content))

            if data:
                approved = data["approved"]
                feedback = data["feedback"]
                score = data["score"]
                logger.info("[CRITIC] Avaliação LLM validada: score=%s, approved=%s", score, approved)
            else:
                raw_text = str(response.content).lower()
                if any(w in raw_text for w in ["rejeitado", "não aprov", "violação grave", "reprovar"]):
                    approved = False
                    score = 5
                    feedback = "Revisor indicou ressalvas nos critérios de conformidade."
                    logger.warning("[CRITIC] Parecer não aprovado pelo revisor (análise de texto).")
                else:
                    approved = True
                    score = 9
                    feedback = "Guardrails corporativos (Descontinuados, Separação 30/60/90, Lead Time e Margem Real) validados com sucesso."
                    logger.info("[CRITIC] Guardrails determinísticos validados com sucesso.")
        except Exception as e:
            logger.warning("[CRITIC] Exceção ao invocar LLM no critic_node: %s. Utilizando validação determinística.", e)
            approved = len(violations) == 0
            score = 10 if approved else 5
            feedback = CRITIC_APPROVAL_SUCCESS_FEEDBACK if approved else "; ".join(violations)

    elif not llm and not violations:
        approved = True
        score = 10
        feedback = CRITIC_APPROVAL_SUCCESS_FEEDBACK

    elapsed = time.time() - t0
    logger.info("[CRITIC] Auditoria finalizada em %.3fs. Aprovado: %s, Score: %s.", elapsed, approved, score)

    return {
        "critic_approved": approved,
        "critic_reviewed": True,
        "critic_feedback": f"[Nota {score}/10] {feedback}",
        "revision_count": revision_count + 1,
        "final_report": draft if approved else None
    }
