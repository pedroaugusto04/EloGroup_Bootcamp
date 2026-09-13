"""
src/agent/inventory_analytics/core.py
Fachada de reconciliação e agregador das métricas analíticas de estoque.
"""

from __future__ import annotations

from .consolidation import build_audit_package
from .financial import (
    CENTRAL_SELL_THROUGH_PCT,
    DEFAULT_LIQUIDATION_DISCOUNT_PCT,
    LIQUIDATION_SELL_THROUGH_PCTS,
    capital_coverage,
    discontinued_capital,
    liquidation,
    returns_risk,
)
from .operational import (
    DEFAULT_COVERAGE_DAYS,
    demand_matrix,
    inventory_health,
    sku_deep_dive,
)
from .quality import DataQualityError, data_quality

__all__ = [
    "DEFAULT_COVERAGE_DAYS",
    "DEFAULT_LIQUIDATION_DISCOUNT_PCT",
    "CENTRAL_SELL_THROUGH_PCT",
    "LIQUIDATION_SELL_THROUGH_PCTS",
    "DataQualityError",
    "data_quality",
    "capital_coverage",
    "inventory_health",
    "demand_matrix",
    "returns_risk",
    "discontinued_capital",
    "sku_deep_dive",
    "liquidation",
    "build_audit_package",
]
