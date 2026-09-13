"""Fachada pública das métricas do Copiloto de estoque.

As regras permanecem separadas por domínio em módulos auxiliares; este arquivo
mantém os imports históricos usados pelas ferramentas, API e testes.
"""

from .core import (
    CENTRAL_SELL_THROUGH_PCT,
    DEFAULT_COVERAGE_DAYS,
    DEFAULT_LIQUIDATION_DISCOUNT_PCT,
    LIQUIDATION_SELL_THROUGH_PCTS,
    DataQualityError,
    build_audit_package,
    capital_coverage,
    data_quality,
    demand_matrix,
    discontinued_capital,
    inventory_health,
    liquidation,
    returns_risk,
    sku_deep_dive,
)

__all__ = [
    "DEFAULT_COVERAGE_DAYS",
    "DEFAULT_LIQUIDATION_DISCOUNT_PCT",
    "CENTRAL_SELL_THROUGH_PCT",
    "LIQUIDATION_SELL_THROUGH_PCTS",
    "DataQualityError",
    "build_audit_package",
    "capital_coverage",
    "data_quality",
    "demand_matrix",
    "discontinued_capital",
    "inventory_health",
    "liquidation",
    "returns_risk",
    "sku_deep_dive",
]
