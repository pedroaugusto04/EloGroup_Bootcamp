"""
src/domain/interfaces.py
Abstract contracts and Protocols for Clean Architecture.
"""

from typing import Protocol, Optional, Any, Dict, List

class IInventoryAgentService(Protocol):
    """Contract for the Inventory & Executive Strategy AI Agent."""

    def run_diagnostic(
        self,
        period_key: str = "full_history",
        on_step: Optional[Any] = None
    ) -> Dict[str, Any]:
        ...

    def ask_copilot(
        self,
        query: str,
        thread_id: str = "vertice_default_session",
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        ...

    def seed_copilot(
        self,
        thread_id: str,
        initial_message: str
    ) -> None:
        ...


