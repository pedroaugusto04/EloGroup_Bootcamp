"""
src/domain/interfaces.py
Abstract contracts and Protocols for Clean Architecture.
"""

from typing import Protocol, List, Dict, Any, Optional
import pandas as pd
from src.domain.models import (
    ExecutiveKPIs,
    ChannelPerformance,
    CategoryPerformance,
    CustomerSegmentSummary,
    InventoryAlert,
    TicketClassification,
    RoadmapInitiative,
    AuditRecord,
)


class IDataRepository(Protocol):
    """Contract for analytical data access (DuckDB / Repository)."""

    def get_executive_kpis(self) -> ExecutiveKPIs:
        ...

    def get_channel_performance(self) -> List[ChannelPerformance]:
        ...

    def get_category_performance(self) -> List[CategoryPerformance]:
        ...

    def get_customer_segments(self) -> List[CustomerSegmentSummary]:
        ...

    def get_inventory_alerts(self, limit: int = 50) -> List[InventoryAlert]:
        ...

    def get_support_tickets_sample(self, limit: int = 100) -> pd.DataFrame:
        ...

    def execute_sql(self, query: str) -> pd.DataFrame:
        ...


class IAuditLogger(Protocol):
    """Contract for data auditability and lineage tracking."""

    def log(self, record: AuditRecord) -> None:
        ...

    def get_all_records(self) -> List[Dict[str, Any]]:
        ...

    def export_report(self) -> Dict[str, Any]:
        ...


class ISalesService(Protocol):
    """Contract for sales and margin analysis services."""

    def get_sales_drilldown(self) -> Dict[str, Any]:
        ...

    def get_margin_leakage_breakdown(self) -> Dict[str, float]:
        ...

    def get_top_skus_margin(self, top_n: int = 10, ascending: bool = False) -> pd.DataFrame:
        ...


class IMarketingService(Protocol):
    """Contract for marketing analysis and simulation."""

    def get_channel_metrics(self) -> pd.DataFrame:
        ...

    def simulate_budget_reallocation(
        self, budget_shifts: Dict[str, float]
    ) -> Dict[str, Any]:
        ...


class IOpsService(Protocol):
    """Contract for operations and inventory."""

    def get_stockout_summary(self) -> Dict[str, Any]:
        ...

    def get_return_impact_by_category(self) -> pd.DataFrame:
        ...


class ICustomerService(Protocol):
    """Contract for customer and retention analysis."""

    def get_rfm_distribution(self) -> pd.DataFrame:
        ...

    def get_high_risk_revenue(self) -> float:
        ...


class IAIService(Protocol):
    """Contract for AI modules (Classifier and Simulator)."""

    def classify_ticket(self, text: str, ticket_id: str = "LIVE-001", customer_id: str = "CLI-DEMO") -> TicketClassification:
        ...

    def batch_classify_tickets(self, df_tickets: pd.DataFrame) -> pd.DataFrame:
        ...

    def get_roadmap_initiatives(self) -> List[RoadmapInitiative]:
        ...

    def simulate_recovery_scenario(
        self,
        pct_marketing_opt: float,
        pct_return_reduction: float,
        pct_stockout_fix: float,
        pct_support_automation: float,
    ) -> Dict[str, Any]:
        ...
