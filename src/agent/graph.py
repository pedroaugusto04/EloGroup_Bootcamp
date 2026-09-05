"""
src/agent/graph.py
Construção e compilação do Grafo LangGraph (Planejamento + Reflexão).
"""

import os
import json
import re
import logging
import time
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

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

logger = logging.getLogger("vertice.inventory_agent")


def get_llm():
    """Obtém o modelo LLM configurado nas variáveis de ambiente ou retorna None se offline."""
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        from langchain_litellm import ChatLiteLLM
        model = os.environ.get("LLM_MODEL", "openai/gemini-3-flash-preview")
        api_base = os.environ.get("OPENAI_API_BASE", "https://chat.eloagents.click/api")
        temperature = float(os.environ.get("LLM_TEMPERATURE", "0.1"))
        request_timeout = int(os.environ.get("LLM_REQUEST_TIMEOUT", "45"))
        return ChatLiteLLM(
            model=model,
            temperature=temperature,
            api_base=api_base,
            request_timeout=request_timeout,
            max_retries=1
        )
    except Exception:
        return None





def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Helper robusto para extração de JSON da resposta do LLM."""
    try:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return json.loads(text)
    except Exception:
        return None


def _validate_critic_payload(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Valida o contrato do parecer; respostas incompletas nunca aprovam o relatório."""
    if not isinstance(data, dict):
        return None

    approved = data.get("approved")
    score = data.get("score")
    feedback = data.get("feedback")
    corrections = data.get("corrections_needed")
    if (
        type(approved) is not bool
        or type(score) is not int
        or not 1 <= score <= 10
        or not isinstance(feedback, str)
        or not feedback.strip()
        or not isinstance(corrections, list)
        or not all(isinstance(item, str) for item in corrections)
    ):
        return None

    return {
        "approved": approved,
        "score": score,
        "feedback": feedback.strip(),
        "corrections_needed": corrections,
    }


# ============================================================================
# NÓS DO GRAFO
# ============================================================================

def planner_node(state: InventoryAgentState) -> Dict[str, Any]:
    """Nó 1: Arquiteto de Planejamento - Decompõe a missão em etapas auditáveis."""
    t0 = time.time()
    logger.info("Iniciando nó [PLANNER] para a missão: %s", state.get("mission", "")[:60])
    plan_steps: List[AgentPlanStep] = []
    
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
            Missão: {state['mission']}
            
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
            draft = response.content
            logger.info("[CONSOLIDATOR] Minuta executiva gerada via LLM com %d caracteres.", len(draft))
        except Exception as e:
            logger.warning("[CONSOLIDATOR] Falha na geração via LLM: %s. Utilizando aviso de indisponibilidade.", e)

    if not draft:
        draft = LLM_UNAVAILABLE_MESSAGE
        logger.info("[CONSOLIDATOR] LLM indisponível. Mensagem padrão de indisponibilidade atribuída.")

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

    # Se o LLM esteve indisponível para gerar o relatório
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
            response = llm.invoke([
                SystemMessage(content=CRITIC_SYSTEM_PROMPT),
                HumanMessage(content=(
                    f"Minuta do Relatório:\n{draft}\n\n"
                    f"Evidências estruturadas para auditoria independente:\n"
                    f"{json.dumps(structured, ensure_ascii=False)}"
                ))
            ])
            data = _validate_critic_payload(_extract_json(str(response.content)))

            # Uma única recuperação para respostas HTTP bem-sucedidas, mas fora do contrato.
            if data is None:
                logger.warning("[CRITIC] Resposta fora do schema; solicitando correção de formato uma vez.")
                repair_response = llm.invoke([
                    SystemMessage(content=CRITIC_SYSTEM_PROMPT),
                    HumanMessage(content=(
                        "A resposta abaixo não cumpriu o contrato. Retorne somente um objeto JSON "
                        "válido seguindo exatamente o schema e o exemplo do sistema, sem Markdown.\n\n"
                        f"Resposta anterior:\n{str(response.content)[:4000]}"
                    )),
                ])
                data = _validate_critic_payload(_extract_json(str(repair_response.content)))
            if data:
                approved = data["approved"]
                feedback = data["feedback"]
                score = data["score"]
                logger.info("[CRITIC] Avaliação LLM: score=%s, approved=%s", score, approved)
            else:
                logger.warning("[CRITIC] Resposta do revisor não contém JSON válido ou schema compatível.")
                return {
                    "critic_approved": False,
                    "critic_reviewed": False,
                    "critic_feedback": "Revisão indisponível: resposta inválida do modelo.",
                    "revision_count": revision_count + 1,
                    "final_report": None,
                }
        except Exception as e:
            logger.warning("[CRITIC] Falha ao invocar LLM no critic_node: %s", e)
            return {
                "critic_approved": False,
                "critic_reviewed": False,
                "critic_feedback": "Revisão indisponível: não foi possível validar o parecer.",
                "revision_count": revision_count + 1,
                "final_report": None,
            }

    if not llm and not violations:
        return {
            "critic_approved": False,
            "critic_reviewed": False,
            "critic_feedback": "Revisão indisponível: modelo de validação não configurado.",
            "revision_count": revision_count + 1,
            "final_report": None,
        }

    elapsed = time.time() - t0
    logger.info("[CRITIC] Auditoria finalizada em %.3fs. Aprovado: %s, Score: %s.", elapsed, approved, score)

    return {
        "critic_approved": approved,
        "critic_reviewed": True,
        "critic_feedback": f"[Nota {score}/10] {feedback}",
        "revision_count": revision_count + 1,
        "final_report": draft if approved else None
    }


# ============================================================================
# CONDICIONAIS E CONSTRUÇÃO DO GRAFO
# ============================================================================

def should_continue_executing(state: InventoryAgentState) -> str:
    """Decide se continua executando etapas do plano ou se consolida o relatório."""
    if state["current_step_index"] < len(state["plan"]):
        return "executor"
    return "consolidator"


def should_reflect_or_finish(state: InventoryAgentState) -> str:
    """Decide se o relatório foi aprovado pelo crítico ou se precisa de revisão."""
    return "finish"


def build_inventory_agent_graph():
    """Compila o StateGraph completo de Planejamento + Reflexão."""
    workflow = StateGraph(InventoryAgentState)

    # Adiciona nós
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("replanner", replanner_node)
    workflow.add_node("consolidator", consolidator_node)
    workflow.add_node("critic", critic_node)

    # Conecta fluxo
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", "replanner")
    workflow.add_conditional_edges(
        "replanner",
        should_continue_executing,
        {
            "executor": "executor",
            "consolidator": "consolidator",
        }
    )
    workflow.add_edge("consolidator", "critic")
    workflow.add_conditional_edges(
        "critic",
        should_reflect_or_finish,
        {"finish": END}
    )

    return workflow.compile()
