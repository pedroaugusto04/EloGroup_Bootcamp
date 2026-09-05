"""
src/agent
Pacote do Agente de Auditoria de Estoque & Decisão Executiva (LangGraph).
"""

from src.agent.state import InventoryAgentState, AgentPlanStep
from src.agent.constants import (
    DEFAULT_PLAN_STEPS,
    DEFAULT_INVENTORY_AUDIT_MISSION,
    LLM_UNAVAILABLE_MESSAGE,
    CRITIC_UNAVAILABLE_FEEDBACK,
    CRITIC_APPROVAL_SUCCESS_FEEDBACK,
    PRESET_MISSIONS,
)
from src.agent.tools import (
    tool_inventory_health_scan,
    tool_sales_demand_matrix,
    tool_marketing_stock_mismatch,
    tool_returns_and_quality_risk,
    tool_discontinued_stranded_capital,
    tool_sku_deep_dive,
)
from src.agent.service import InventoryAgentService

__all__ = [
    "InventoryAgentState",
    "AgentPlanStep",
    "DEFAULT_PLAN_STEPS",
    "DEFAULT_INVENTORY_AUDIT_MISSION",
    "LLM_UNAVAILABLE_MESSAGE",
    "CRITIC_UNAVAILABLE_FEEDBACK",
    "CRITIC_APPROVAL_SUCCESS_FEEDBACK",
    "PRESET_MISSIONS",
    "tool_inventory_health_scan",
    "tool_sales_demand_matrix",
    "tool_marketing_stock_mismatch",
    "tool_returns_and_quality_risk",
    "tool_discontinued_stranded_capital",
    "tool_sku_deep_dive",
    "InventoryAgentService",
]
