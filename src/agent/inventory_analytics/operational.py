"""
src/agent/inventory_analytics/operational.py
Métricas operacionais de saúde do estoque, demanda de vendas e deep dive de SKU.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional

from src.agent.periods import build_meta, resolve_period
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query
from .common import one_row, records
from .quality import data_quality
from .validation import validate_category, validate_limit, validate_sku

DEFAULT_COVERAGE_DAYS = 120.0


def inventory_health(
    repo: DuckDBRepository,
    period_key: str = "full_history",
    category: Optional[str] = None,
    coverage_days: float = DEFAULT_COVERAGE_DAYS,
    limit: Optional[int] = 25,
) -> Dict[str, Any]:
    """Calcula indicadores de ruptura, ponto de pedido, lead time e cobertura."""
    period = resolve_period(repo, period_key)
    data_quality(repo, period_key)
    category = validate_category(repo, category)
    if limit is not None:
        limit = validate_limit(limit)
    if not isinstance(coverage_days, (int, float)) or not math.isfinite(coverage_days) or coverage_days <= 0:
        raise ValueError("coverage_days deve ser um número positivo.")
    params = [
        period.start, period.end, period.start, period.end,
        *([period.days] * 6), float(coverage_days), *([period.days] * 3),
        category, category,
    ]
    df = repo.execute_sql(load_query("agent/inventory_health.sql"), params)
    items = records(df if limit is None else df.head(limit))
    summary = {
        "ruptura_atual": int(df["ruptura_atual"].fillna(False).sum()) if not df.empty else 0,
        "abaixo_ou_no_ponto_pedido": int(df["abaixo_ou_no_ponto_pedido"].fillna(False).sum()) if not df.empty else 0,
        "exposicao_lead_time": int(df["exposicao_lead_time"].fillna(False).sum()) if not df.empty else 0,
        "alta_cobertura_historica": int(df["alta_cobertura_historica"].fillna(False).sum()) if not df.empty else 0,
        "sem_venda_observada": int(df["sem_venda_observada"].fillna(False).sum()) if not df.empty else 0,
        "coverage_threshold_days": float(coverage_days),
    }
    warnings = []
    if not df.empty and summary["sem_venda_observada"] == len(df):
        warnings.append("Nenhuma venda aprovada válida foi observada na janela; rankings e ações foram omitidos.")
    return {"meta": build_meta(period, warnings), "summary": summary, "items": items}


def demand_matrix(
    repo: DuckDBRepository,
    period_key: str = "full_history",
    category: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """Calcula demanda, faturamento e margem agregados por SKU."""
    period = resolve_period(repo, period_key)
    category = validate_category(repo, category)
    limit = validate_limit(limit)
    df = repo.execute_sql(
        load_query("agent/sales_demand.sql"),
        [period.start, period.end, category, category],
    )
    summary = {
        "skus": len(df),
        "unidades_aprovadas": float(df["unidades_aprovadas"].sum()) if not df.empty else 0.0,
        "receita_efetiva": float(df["receita_efetiva"].sum()) if not df.empty else 0.0,
        "margem_efetiva": float(df["margem_efetiva"].sum()) if not df.empty else 0.0,
    }
    warnings = ["Nenhuma venda aprovada válida foi observada na janela."] if df.empty else []
    return {"meta": build_meta(period, warnings), "summary": summary, "items": records(df.head(limit))}


def sku_deep_dive(repo: DuckDBRepository, sku_id: str, period_key: str = "full_history") -> Dict[str, Any]:
    """Diagnóstico individual profundo de estoque e demanda para um SKU específico."""
    period = resolve_period(repo, period_key)
    data_quality(repo, period_key)
    sku_id = validate_sku(sku_id)
    df = repo.execute_sql(
        load_query("agent/sku_deep_dive.sql"),
        [period.start, period.end, sku_id, sku_id, sku_id],
    )
    warnings = ["Lead time exibido é cadastral; a base não permite medir lead time realizado de reposição."]
    if df.empty:
        warnings.append(f"SKU {sku_id} não encontrado na posição de estoque.")
    return {"meta": build_meta(period, warnings), "summary": {"found": not df.empty}, "items": records(df)}


__all__ = ["DEFAULT_COVERAGE_DAYS", "inventory_health", "demand_matrix", "sku_deep_dive"]
