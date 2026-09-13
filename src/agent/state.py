"""Estado do fluxo reproduzível de auditoria."""

import operator
from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict


class AgentPlanStep(TypedDict):
    step_id: int
    name: str
    description: str
    status: str
    result: Optional[str]


class InventoryAgentState(TypedDict, total=False):
    period_key: str
    plan: List[AgentPlanStep]
    current_step_index: int
    observations: Annotated[List[Dict[str, Any]], operator.add]
    factual_package: Optional[Dict[str, Any]]
    structured_data: Optional[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    draft_report: Optional[str]
    final_report: Optional[str]
    deterministic_checks: Dict[str, bool]
    deterministic_approved: bool
    critic_feedback: Optional[str]
    critic_approved: bool
    critic_reviewed: bool
    revision_count: int
    llm_complement_status: str
