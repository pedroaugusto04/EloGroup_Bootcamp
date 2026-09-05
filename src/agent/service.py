"""
src/agent/service.py
Camada de serviço de alto nível para orquestração do Agente de Auditoria de Estoque.
"""

import os
from typing import Dict, Any, Optional, List
from src.domain.interfaces import IInventoryAgentService

from src.agent.graph import build_inventory_agent_graph
from src.agent.state import InventoryAgentState
from src.agent.copilot import InventoryCopilot


class InventoryAgentService(IInventoryAgentService):
    """Serviço de orquestração do Agente de Estoque (Worker Autônomo + Copiloto Interativo)."""

    def __init__(self, graph=None, copilot: Optional[InventoryCopilot] = None):
        self.graph = graph or build_inventory_agent_graph()
        self.copilot = copilot or InventoryCopilot()

    def run_diagnostic(
        self,
        mission: str = "Auditar a saúde de estoque da Vértice Retail, diagnosticar rupturas e capital travado em descontinuados, e estruturar plano de ação 30/60/90 dias com Quick Wins.",
        date_filter: str = "",
        days_window: float = 365.0,
        period_label: str = "Ano Fechado 2023",
        on_step: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Executa a auditoria completa e retorna o estado consolidado com suporte a filtros temporais e callbacks."""
        initial_state: InventoryAgentState = {
            "mission": mission,
            "plan": [],
            "current_step_index": 0,
            "observations": [],
            "draft_report": None,
            "critic_feedback": None,
            "critic_approved": False,
            "critic_reviewed": False,
            "revision_count": 0,
            "final_report": None,
            "structured_data": None,
            "date_filter": date_filter,
            "days_window": days_window,
            "period_label": period_label,
        }
        
        audit_recursion_limit = int(os.environ.get("AUDIT_RECURSION_LIMIT", "25"))
        config = {"recursion_limit": audit_recursion_limit}

        if on_step:
            accumulated_state = dict(initial_state)
            for chunk in self.graph.stream(initial_state, config=config):
                for node_name, state_update in chunk.items():
                    accumulated_state.update(state_update)
                    if "observations" in state_update and state_update["observations"]:
                        # Redutor de observações
                        accumulated_state["observations"] = (
                            accumulated_state.get("observations", []) + state_update["observations"]
                        )
                    try:
                        on_step(node_name, state_update, accumulated_state)
                    except Exception:
                        pass
            return accumulated_state

        result = self.graph.invoke(initial_state, config=config)
        return result


    def ask_copilot(
        self,
        query: str,
        thread_id: str = "vertice_default_session",
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Processa perguntas ad-hoc e simulações com o Copiloto Interativo ReAct mantendo memória de sessão."""
        return self.copilot.ask(query, thread_id=thread_id, history=history)

    def seed_copilot(self, thread_id: str, initial_message: str) -> None:
        """Inicializa a memória do Copiloto ReAct com uma mensagem prévia (ex: e-mail de auditoria)."""
        self.copilot.seed_conversation(thread_id, initial_message)


