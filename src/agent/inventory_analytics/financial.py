"""
src/agent/inventory_analytics/financial.py
Métricas financeiras de cobertura de capital, descontinuados, liquidação e risco de devolução.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional

import pandas as pd

from src.agent.periods import build_meta, resolve_period
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query
from .common import one_row, records
from .quality import data_quality
from .validation import validate_category, validate_limit

DEFAULT_LIQUIDATION_DISCOUNT_PCT = 30.0
CENTRAL_SELL_THROUGH_PCT = 50
LIQUIDATION_SELL_THROUGH_PCTS = (25, 50, 75, 100)


def capital_coverage(repo: DuckDBRepository, period_key: str = "full_history") -> Dict[str, Any]:
    """Calcula a cobertura de capital e conciliação entre custos de Vendas e Estoque."""
    period = resolve_period(repo, period_key)
    data_quality(repo, period_key)
    summary = one_row(repo.execute_sql(load_query("agent/capital_coverage.sql")))
    return {"meta": build_meta(period), "summary": summary, "items": []}


def discontinued_capital(
    repo: DuckDBRepository,
    period_key: str = "full_history",
    category: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """Calcula o capital retido em produtos descontinuados."""
    period = resolve_period(repo, period_key)
    data_quality(repo, period_key)
    category = validate_category(repo, category)
    limit = validate_limit(limit)
    df = repo.execute_sql(load_query("agent/discontinued_items.sql"), [category, category])
    covered = df[df["custo_unitario_vendas"].notna()] if not df.empty else df
    summary = {
        "skus_retornados": len(df),
        "skus_valorados": int(df["custo_unitario_vendas"].notna().sum()) if not df.empty else 0,
        "skus_excluidos_sem_custo": int(df["custo_unitario_vendas"].isna().sum()) if not df.empty else 0,
        "capital_fisico": float(covered["capital_fisico"].sum()) if not covered.empty else 0.0,
        "capital_disponivel": float(covered["capital_disponivel"].sum()) if not covered.empty else 0.0,
    }
    return {"meta": build_meta(period), "summary": summary, "items": records(df.head(limit))}


def liquidation(
    repo: DuckDBRepository,
    period_key: str = "full_history",
    category: Optional[str] = None,
    discount_pct: float = DEFAULT_LIQUIDATION_DISCOUNT_PCT,
) -> Dict[str, Any]:
    """Simula cenários de liquidação de produtos descontinuados com base no histórico de vendas."""
    period = resolve_period(repo, period_key)
    data_quality(repo, period_key)
    category = validate_category(repo, category)
    if not isinstance(discount_pct, (int, float)) or not math.isfinite(discount_pct) or not 0 <= discount_pct <= 90:
        raise ValueError("desconto_pct deve estar entre 0 e 90.")
    df = repo.execute_sql(
        load_query("agent/liquidation.sql"),
        [period.start, period.end, period.start, period.end, category, category],
    )
    eligible_mask = (
        df["custo_unitario_vendas"].notna()
        & df["preco_liquido_unitario"].notna()
        & (df["preco_liquido_unitario"] > 0)
        & df["frete_unitario"].notna()
    ) if not df.empty else pd.Series(dtype=bool)
    eligible = df[eligible_mask].copy() if not df.empty else df.copy()
    scenarios = []
    factor = 1 - float(discount_pct) / 100.0
    for sell_through_pct in LIQUIDATION_SELL_THROUGH_PCTS:
        sell_through = sell_through_pct / 100
        units = eligible["estoque_disponivel"] * sell_through
        capital = units * eligible["custo_unitario_vendas"]
        revenue_before = units * eligible["preco_liquido_unitario"] * factor
        revenue_adjusted = revenue_before * (1 - eligible["taxa_devolucao_categoria"].fillna(0))
        shipping = units * eligible["frete_unitario"]
        return_adjustment = revenue_before - revenue_adjusted
        contribution = revenue_adjusted - capital - shipping
        revenue_adjusted_total = float(revenue_adjusted.sum())
        capital_total = float(capital.sum())
        contribution_total = float(contribution.sum())
        scenarios.append({
            "sell_through_pct": sell_through_pct,
            "unidades_cenario": float(units.sum()),
            "capital_historico_envolvido": capital_total,
            "receita_antes_devolucoes": float(revenue_before.sum()),
            "ajuste_estimado_devolucoes": float(return_adjustment.sum()),
            "receita_ajustada_devolucoes": revenue_adjusted_total,
            "frete_historico_estimado": float(shipping.sum()),
            "contribuicao_estimada": contribution_total,
            "contribuicao_sobre_receita_pct": contribution_total / revenue_adjusted_total * 100 if revenue_adjusted_total else None,
            "contribuicao_sobre_capital_pct": contribution_total / capital_total * 100 if capital_total else None,
        })
    central_detail = eligible[["sku_id", "nome_produto", "categoria"]].copy()
    if not eligible.empty:
        central_units = eligible["estoque_disponivel"] * (CENTRAL_SELL_THROUGH_PCT / 100)
        central_revenue_before = central_units * eligible["preco_liquido_unitario"] * factor
        central_revenue_adjusted = central_revenue_before * (1 - eligible["taxa_devolucao_categoria"].fillna(0))
        central_detail = central_detail.assign(
            unidades_cenario=central_units,
            capital_historico_envolvido=central_units * eligible["custo_unitario_vendas"],
            receita_antes_devolucoes=central_revenue_before,
            ajuste_estimado_devolucoes=central_revenue_before - central_revenue_adjusted,
            receita_ajustada_devolucoes=central_revenue_adjusted,
            frete_historico_estimado=central_units * eligible["frete_unitario"],
        )
        central_detail["contribuicao_estimada"] = (
            central_detail["receita_ajustada_devolucoes"]
            - central_detail["capital_historico_envolvido"]
            - central_detail["frete_historico_estimado"]
        )
        value_columns = [
            "unidades_cenario", "capital_historico_envolvido", "receita_antes_devolucoes",
            "ajuste_estimado_devolucoes", "receita_ajustada_devolucoes",
            "frete_historico_estimado", "contribuicao_estimada",
        ]
        central_by_category = records(
            central_detail.groupby("categoria", as_index=False)[value_columns]
            .sum().sort_values(["contribuicao_estimada", "categoria"], ascending=[False, True])
        )
        central_top_skus = records(
            central_detail.sort_values(["contribuicao_estimada", "sku_id"], ascending=[False, True]).head(10)
        )
    else:
        central_by_category = []
        central_top_skus = []

    summary = {
        "categoria": category or "Todas",
        "desconto_pct": float(discount_pct),
        "skus_descontinuados_com_saldo": len(df),
        "skus_elegiveis": len(eligible),
        "skus_excluidos_sem_custo_ou_preco": int(len(df) - len(eligible)),
        "scenarios": scenarios,
        "central_scenario": next(s for s in scenarios if s["sell_through_pct"] == CENTRAL_SELL_THROUGH_PCT),
        "central_by_category": central_by_category,
        "central_top_skus": central_top_skus,
        "limitations": [
            "Não há modelagem de retorno físico do item devolvido.",
            "Impostos, comissões, logística reversa e elasticidade de preço não estão disponíveis.",
        ],
    }
    warnings = []
    if df.empty or eligible.empty:
        warnings.append("Não há SKUs descontinuados com custo e preço válidos para simular nessa seleção.")
    return {"meta": build_meta(period, warnings), "summary": summary, "items": records(df)}


def returns_risk(
    repo: DuckDBRepository,
    period_key: str = "full_history",
    min_orders: int = 10,
    min_returns: int = 2,
    limit: int = 20,
) -> Dict[str, Any]:
    """Analisa SKUs com maior volume e taxa de devoluções no histórico."""
    period = resolve_period(repo, period_key)
    if min_orders < 1 or min_returns < 0:
        raise ValueError("Limites de pedidos/devoluções inválidos.")
    limit = validate_limit(limit)
    df = repo.execute_sql(
        load_query("agent/returns.sql"),
        [period.start, period.end, int(min_orders), int(min_returns)],
    )
    return {
        "meta": build_meta(period, ["Motivos são declarações registradas, não causas-raiz comprovadas."]),
        "summary": {"skus": len(df)},
        "items": records(df.head(limit)),
    }


__all__ = [
    "DEFAULT_LIQUIDATION_DISCOUNT_PCT",
    "CENTRAL_SELL_THROUGH_PCT",
    "LIQUIDATION_SELL_THROUGH_PCTS",
    "capital_coverage",
    "discontinued_capital",
    "liquidation",
    "returns_risk",
]
