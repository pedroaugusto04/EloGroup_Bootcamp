"""
src/domain/models.py
Domain entities and dataclasses for Project Vértice.
"""

from dataclasses import dataclass


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
