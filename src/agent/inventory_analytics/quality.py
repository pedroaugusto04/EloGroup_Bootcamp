"""
src/agent/inventory_analytics/quality.py
Validações de qualidade de dados operacionais e de vendas no DuckDB.
"""

from __future__ import annotations

import csv
from typing import Any, Dict

from src.agent.periods import resolve_period
from src.infrastructure.database import DuckDBRepository
from .common import one_row


class DataQualityError(RuntimeError):
    """Falha que impede reconciliação determinística do estoque."""


def data_quality(repo: DuckDBRepository, period_key: str = "full_history") -> Dict[str, Any]:
    """Audita a integridade dos dados de estoque e vendas no período especificado."""
    period = resolve_period(repo, period_key)
    inventory = one_row(repo.execute_sql("""
        SELECT
          COUNT(*) FILTER (WHERE sku_id IS NULL OR TRIM(sku_id) = '') AS missing_sku,
          COUNT(*) - COUNT(DISTINCT sku_id) AS duplicate_sku,
          COUNT(*) FILTER (WHERE estoque_fisico IS NULL OR estoque_reservado IS NULL OR estoque_disponivel IS NULL) AS missing_balance,
          COUNT(*) FILTER (WHERE estoque_fisico < 0 OR estoque_reservado < 0 OR estoque_disponivel < 0
                            OR estoque_fisico - estoque_reservado <> estoque_disponivel) AS inconsistent_balance
        FROM estoque
    """))
    sales = one_row(repo.execute_sql("""
        SELECT
          COUNT(*) AS rows_in_period,
          COUNT(*) FILTER (WHERE order_id IS NULL OR TRIM(order_id) = '' OR sku_id IS NULL OR TRIM(sku_id) = ''
                            OR data_pedido IS NULL) AS invalid_keys,
          COUNT(*) FILTER (WHERE status_pagamento = 'Aprovado' AND (quantidade IS NULL OR quantidade <= 0)) AS invalid_quantity,
          COUNT(*) FILTER (WHERE status_pagamento = 'Aprovado' AND (custo_produto IS NULL OR custo_produto < 0)) AS invalid_cost,
          COUNT(*) FILTER (WHERE status_pagamento = 'Aprovado' AND (receita_liquida IS NULL OR receita_liquida <= 0)) AS invalid_price
        FROM vendas WHERE CAST(data_pedido AS DATE) BETWEEN ? AND ?
    """, [period.start, period.end]))

    raw_malformed = 0
    raw_path = repo.processed_dir.parent / "raw" / "[BootCamp EloGroup 2026] Vendas.csv"
    if raw_path.exists():
        # O registro curto conhecido permanece no CSV bruto e não participa do parquet.
        with raw_path.open("r", encoding="utf-8", newline="") as source:
            rows = csv.reader(source)
            expected = len(next(rows))
            raw_malformed = sum(1 for row in rows if len(row) != expected)

    blocking = sum(int(inventory.get(k) or 0) for k in (
        "missing_sku", "duplicate_sku", "missing_balance", "inconsistent_balance"
    ))
    result = {
        "inventory": inventory,
        "sales_quarantine": sales,
        "malformed_raw_sales_rows_excluded": raw_malformed,
        "blocking_errors": blocking,
    }
    if blocking:
        raise DataQualityError(f"Qualidade operacional do estoque reprovada: {result}")
    return result


__all__ = ["DataQualityError", "data_quality"]
