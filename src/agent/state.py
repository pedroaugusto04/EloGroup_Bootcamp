"""
src/agent/state.py
Definição do estado e estruturas de dados do LangGraph para o Agente de Estoque.
"""

from typing import List, Dict, Any, Optional, Annotated
from typing_extensions import TypedDict
import operator


class AgentPlanStep(TypedDict):
    step_id: int
    name: str
    description: str
    status: str  # 'pending', 'in_progress', 'completed'
    result: Optional[str]


class InventoryAgentState(TypedDict):
    mission: str
    plan: List[AgentPlanStep]
    current_step_index: int
    observations: Annotated[List[Dict[str, Any]], operator.add]
    draft_report: Optional[str]
    critic_feedback: Optional[str]
    critic_approved: bool
    critic_reviewed: bool
    revision_count: int
    final_report: Optional[str]
    structured_data: Optional[Dict[str, Any]]
