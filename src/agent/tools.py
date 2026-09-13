"""Ferramentas DuckDB com período tipado e parâmetros vinculados."""

import json
from typing import Optional

from langchain_core.tools import tool

from src.agent.inventory_analytics import (
    DEFAULT_COVERAGE_DAYS,
    DEFAULT_LIQUIDATION_DISCOUNT_PCT,
    demand_matrix,
    discontinued_capital,
    inventory_health,
    liquidation,
    returns_risk,
    sku_deep_dive,
)
from src.agent.periods import PeriodKey
from src.infrastructure.database import DuckDBRepository


def _get_repo() -> DuckDBRepository:
    return DuckDBRepository()


def _json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)


@tool
def tool_inventory_health_scan(
    period_key: PeriodKey = "full_history",
    categoria: Optional[str] = None,
    coverage_days: float = DEFAULT_COVERAGE_DAYS,
    limit: int = 25,
) -> str:
    """Separa ruptura atual, ponto de pedido, exposição no lead time cadastral,
    alta cobertura histórica e ausência de venda. Não prevê demanda futura.
    """
    return _json(inventory_health(_get_repo(), period_key, categoria, coverage_days, limit))


@tool
def tool_sales_demand_matrix(
    period_key: PeriodKey = "full_history",
    categoria: Optional[str] = None,
    top_n: int = 20,
) -> str:
    """Retorna demanda bruta aprovada, receita efetiva e margem efetiva na janela tipada."""
    return _json(demand_matrix(_get_repo(), period_key, categoria, top_n))


@tool
def tool_returns_and_quality_risk(
    period_key: PeriodKey = "full_history",
    min_orders: int = 10,
    min_returns: int = 2,
    limit: int = 20,
) -> str:
    """Resume devoluções e o motivo declarado, sem inferir causalidade."""
    return _json(returns_risk(_get_repo(), period_key, min_orders, min_returns, limit))


@tool
def tool_discontinued_stranded_capital(
    period_key: PeriodKey = "full_history",
    categoria: Optional[str] = None,
    limit: int = 20,
) -> str:
    """Valora estoque descontinuado pelo custo médio ponderado observado em Vendas."""
    return _json(discontinued_capital(_get_repo(), period_key, categoria, limit))


@tool
def tool_sku_deep_dive(sku_id: str, period_key: PeriodKey = "full_history") -> str:
    """Investiga um SKU, distinguindo posição operacional, lead time cadastral e finanças históricas."""
    return _json(sku_deep_dive(_get_repo(), sku_id, period_key))


@tool
def tool_simulate_inventory_liquidation(
    period_key: PeriodKey = "full_history",
    categoria: Optional[str] = None,
    desconto_pct: float = DEFAULT_LIQUIDATION_DISCOUNT_PCT,
) -> str:
    """Simula 25/50/75/100% de sell-through sobre preço líquido histórico, com ajuste de devolução."""
    return _json(liquidation(_get_repo(), period_key, categoria, desconto_pct))
