"""
src/domain/models.py
Domain entities and dataclasses for Project Vértice.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import StrEnum


@dataclass(frozen=True)
class ExecutiveKPIs:
    gross_revenue: float
    net_revenue: float
    contribution_margin: float
    contribution_margin_pct: float
    total_orders: int
    average_ticket: float
    return_rate_pct: float
    marketing_investment: float
    average_cac: float
    overall_roas: float
    average_csat: float
    stockout_skus: int


@dataclass(frozen=True)
class ChannelPerformance:
    channel: str
    net_revenue: float
    contribution_margin: float
    margin_pct: float
    orders: int
    average_ticket: float
    investment: float
    cac: float
    roas: float
    return_rate_pct: float


@dataclass(frozen=True)
class CategoryPerformance:
    category: str
    net_revenue: float
    product_cost: float
    shipping_cost: float
    discounts: float
    contribution_margin: float
    margin_pct: float
    orders: int
    return_rate_pct: float


@dataclass(frozen=True)
class CustomerSegmentSummary:
    rfm_segment: str
    total_customers: int
    pct_base: float
    average_ltv: float
    average_orders: float
    average_income: float


@dataclass(frozen=True)
class InventoryAlert:
    sku_id: str
    product_name: str
    category: str
    available_stock: int
    reorder_point: int
    lead_time: int
    status: str
    unit_cost: float
    selling_price: float


class Sentiment(StrEnum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"


class Urgency(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class IssueCategory(StrEnum):
    LOGISTICS = "Logistics & Delivery Delay"
    SIZE_FIT = "Size / Fit Exchange"
    DEFECT = "Product Quality / Defect"
    FINANCIAL = "Financial & Refund"
    GENERAL = "General Questions & Navigation"


class ChurnRisk(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class RoadmapHorizon(StrEnum):
    DAYS_30 = "30 Days"
    DAYS_60 = "60 Days"
    DAYS_90 = "90 Days"


class Pillar(StrEnum):
    COMMERCIAL = "Commercial & Margin"
    MARKETING = "Marketing & CAC"
    OPERATIONS = "Operations & Inventory"
    CUSTOMER_SERVICE = "Customer Service & AI"


class Effort(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Speed(StrEnum):
    IMMEDIATE = "Immediate (Quick-Win)"
    MEDIUM = "Medium"
    STRUCTURAL = "Structural"


@dataclass(frozen=True)
class TicketClassification:
    ticket_id: str
    customer_id: str
    customer_text: str
    sentiment: Sentiment
    urgency: Urgency
    issue_category: IssueCategory
    recommended_action: str
    automatable: bool
    churn_risk: ChurnRisk


@dataclass(frozen=True)
class RoadmapInitiative:
    horizon: RoadmapHorizon
    pillar: Pillar
    title: str
    description: str
    estimated_monthly_financial_impact: float
    effort: Effort
    speed: Speed


@dataclass
class AuditRecord:
    table: str
    source_file: str
    hash_sha256: str
    processing_timestamp: str
    raw_rows: int
    processed_rows: int
    handled_nulls: Dict[str, int]
    transformation_notes: List[str] = field(default_factory=list)
