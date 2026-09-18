"""
src/agent/graph.py
Construção e compilação do Grafo LangGraph (Planejamento + Reflexão).
"""

import logging
from langgraph.graph import StateGraph, START, END

from src.agent.state import InventoryAgentState
import src.agent.nodes as nodes
from src.utils.json_parser import (
    extract_json_from_llm_response,
    validate_critic_payload,
)
from src.agent.nodes import (
    planner_node,
    executor_node,
    replanner_node,
    consolidator_node,
    critic_node,
)

from src.infrastructure.llm import get_llm


# Aliases para compatibilidade retroativa e testes existentes
_extract_json = extract_json_from_llm_response
_validate_critic_payload = validate_critic_payload

logger = logging.getLogger("vertice.inventory_agent")


def should_continue_executing(state: InventoryAgentState) -> str:
    """Decide se continua executando etapas do plano ou se consolida o relatório."""
    if state["current_step_index"] < len(state["plan"]):
        return "executor"
    return "consolidator"


def should_reflect_or_finish(state: InventoryAgentState) -> str:
    """Decide se o relatório foi aprovado pelo crítico ou se retorna para revisão do consolidador."""
    approved = state.get("critic_approved", False)
    revision_count = int(state.get("revision_count", 0))
    if not approved and revision_count < 2:
        logger.warning(
            "Crítico reprovou draft na revisão %d. Redirecionando para consolidator: %s",
            revision_count,
            state.get("critic_feedback"),
        )
        return "consolidator"
    return "finish"


def build_inventory_agent_graph():
    """Compila o StateGraph completo de Planejamento + Reflexão."""
    workflow = StateGraph(InventoryAgentState)

    # Adiciona nós modulares
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
        {
            "consolidator": "consolidator",
            "finish": END,
        }
    )

    return workflow.compile()
