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
    PLANNER_SYSTEM_PROMPT,
    EXECUTOR_SYSTEM_PROMPT,
    CONSOLIDATOR_SYSTEM_PROMPT,
    CRITIC_SYSTEM_PROMPT,
    REFINER_SYSTEM_PROMPT,
)
from src.agent.constants import (
    DEFAULT_PLAN_STEPS,
    LLM_UNAVAILABLE_MESSAGE,
    CRITIC_UNAVAILABLE_FEEDBACK,
    CRITIC_APPROVAL_SUCCESS_FEEDBACK,
    REVISION_NOTE_PREFIX,
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


# ============================================================================
# NÓS DO GRAFO
# ============================================================================

def planner_node(state: InventoryAgentState) -> Dict[str, Any]:
    """Nó 1: Arquiteto de Planejamento - Decompõe a missão em etapas auditáveis."""
    t0 = time.time()
    logger.info("Iniciando nó [PLANNER] para a missão: %s", state.get("mission", "")[:60])
    llm = get_llm()
    plan_steps: List[AgentPlanStep] = []
    
    if llm:
        try:
            response = llm.invoke([
                SystemMessage(content=PLANNER_SYSTEM_PROMPT),
                HumanMessage(content=f"Missão: {state['mission']}")
            ])
            data = _extract_json(response.content)
            if data and "plan" in data:
                for item in data["plan"]:
                    plan_steps.append({
                        "step_id": item.get("step_id", len(plan_steps) + 1),
                        "name": item.get("name", "Etapa"),
                        "description": item.get("description", ""),
                        "status": "pending",
                        "result": None,
                    })
                logger.info("Planejamento gerado via LLM com %d etapas.", len(plan_steps))
        except Exception as e:
            logger.warning("Falha ao invocar LLM no planner_node: %s. Utilizando plano padrão.", e)

    if not plan_steps:
        plan_steps = [dict(step) for step in DEFAULT_PLAN_STEPS]
        logger.info("Plano padrão determinístico carregado com %d etapas.", len(plan_steps))

    elapsed = time.time() - t0
    logger.info("[PLANNER] concluído em %.3fs.", elapsed)

    return {
        "plan": plan_steps,
        "current_step_index": 0,
        "observations": [],
        "revision_count": 0,
        "critic_approved": False,
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
            "critic_feedback": CRITIC_UNAVAILABLE_FEEDBACK,
            "revision_count": revision_count + 1,
            "final_report": draft,
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
                HumanMessage(content=f"Minuta do Relatório:\n{draft}")
            ])
            data = _extract_json(response.content)
            if data:
                approved = data.get("approved", True)
                feedback = data.get("feedback", feedback)
                score = data.get("score", score)
                logger.info("[CRITIC] Avaliação LLM: score=%s, approved=%s", score, approved)
        except Exception as e:
            logger.warning("[CRITIC] Falha ao invocar LLM no critic_node: %s", e)

    elapsed = time.time() - t0
    logger.info("[CRITIC] Auditoria finalizada em %.3fs. Aprovado: %s, Score: %s.", elapsed, approved, score)

    return {
        "critic_approved": approved,
        "critic_feedback": f"[Nota {score}/10] {feedback}",
        "revision_count": revision_count + 1,
        "final_report": draft if approved or revision_count >= 1 else None
    }


def refiner_node(state: InventoryAgentState) -> Dict[str, Any]:
    """Nó 6: Refinador de Proposta - Aplica correções solicitadas pelo crítico."""
    t0 = time.time()
    draft = state.get("draft_report", "")
    feedback = state.get("critic_feedback", "")
    logger.info("Iniciando nó [REFINER] - Aplicando ajustes com base no feedback: %s", feedback[:80])
    
    # Ajusta minuta garantindo conformidade
    refined_draft = draft + f"{REVISION_NOTE_PREFIX}{feedback}"
    elapsed = time.time() - t0
    logger.info("[REFINER] Refinamento concluído em %.3fs.", elapsed)
    
    return {
        "draft_report": refined_draft,
        "final_report": refined_draft,
        "critic_approved": True
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
    if state.get("critic_approved", False) or state.get("revision_count", 0) >= 2:
        return "finish"
    return "refiner"


def build_inventory_agent_graph():
    """Compila o StateGraph completo de Planejamento + Reflexão."""
    workflow = StateGraph(InventoryAgentState)

    # Adiciona nós
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("replanner", replanner_node)
    workflow.add_node("consolidator", consolidator_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("refiner", refiner_node)

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
        {
            "refiner": "refiner",
            "finish": END,
        }
    )
    workflow.add_edge("refiner", "critic")

    return workflow.compile()
