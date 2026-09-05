"""
src/domain/interfaces.py
Abstract contracts and Protocols for Clean Architecture.
"""

from typing import Protocol, Optional, Any, Dict

class IInventoryAgentService(Protocol):
    """Contract for the Inventory & Executive Strategy AI Agent."""

    def run_diagnostic(
        self,
        mission: str = "Auditar a saúde de estoque da Vértice Retail, diagnosticar rupturas e descompasso com marketing, e estruturar plano de ação 30/60/90 dias com Quick Wins.",
        on_step: Optional[Any] = None
    ) -> Dict[str, Any]:
        ...

    def ask_copilot(
        self,
        query: str,
        thread_id: str = "vertice_default_session"
    ) -> str:
        ...

    def seed_copilot(
        self,
        thread_id: str,
        initial_message: str
    ) -> None:
        ...



