"""Pacote factual do copiloto, independente do LLM."""

from __future__ import annotations

import math
import re
import csv
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import numpy as np
import pandas as pd

from src.agent.periods import build_meta, methodology_banner, resolve_period
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query

DEFAULT_COVERAGE_DAYS = 120.0
SKU_PATTERN = re.compile(r"^SKU-\d{5}$")


class DataQualityError(RuntimeError):
    """Falha que impede reconciliação determinística do estoque."""


def _python_value(value: Any) -> Any:
    if value is None or (not isinstance(value, (list, dict)) and pd.isna(value)):
        return None
    if isinstance(value, (pd.Timestamp,)):
        return value.date().isoformat() if value.time().isoformat() == "00:00:00" else value.isoformat()
    if hasattr(value, "isoformat") and not isinstance(value, str):
        return value.isoformat()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def records(df: pd.DataFrame) -> list[dict]:
    return [{key: _python_value(value) for key, value in row.items()} for row in df.to_dict("records")]


def _one_row(df: pd.DataFrame) -> dict:
    return records(df)[0] if not df.empty else {}


def validate_limit(limit: int, maximum: int = 5000) -> int:
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= maximum:
        raise ValueError(f"limit deve estar entre 1 e {maximum}.")
    return limit


def validate_category(repo: DuckDBRepository, category: Optional[str]) -> Optional[str]:
    if category is None:
        return None
    if not isinstance(category, str) or not category.strip() or len(category) > 100:
        raise ValueError("categoria inválida.")
    category = category.strip()
    valid = set(repo.execute_sql("SELECT DISTINCT categoria FROM estoque WHERE categoria IS NOT NULL")["categoria"])
    if category not in valid:
        raise ValueError("categoria não encontrada; nenhum trecho SQL é aceito nesse campo.")
    return category


def validate_sku(sku_id: str) -> str:
    if not isinstance(sku_id, str) or not SKU_PATTERN.fullmatch(sku_id.strip()):
        raise ValueError("sku_id inválido; use o formato SKU-00000.")
    return sku_id.strip()


def data_quality(repo: DuckDBRepository, period_key: str = "full_history") -> Dict[str, Any]:
    period = resolve_period(repo, period_key)
    inventory = _one_row(repo.execute_sql("""
        SELECT
          COUNT(*) FILTER (WHERE sku_id IS NULL OR TRIM(sku_id) = '') AS missing_sku,
          COUNT(*) - COUNT(DISTINCT sku_id) AS duplicate_sku,
          COUNT(*) FILTER (WHERE estoque_fisico IS NULL OR estoque_reservado IS NULL OR estoque_disponivel IS NULL) AS missing_balance,
          COUNT(*) FILTER (WHERE estoque_fisico < 0 OR estoque_reservado < 0 OR estoque_disponivel < 0
                            OR estoque_fisico - estoque_reservado <> estoque_disponivel) AS inconsistent_balance
        FROM estoque
    """))
    sales = _one_row(repo.execute_sql("""
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


def capital_coverage(repo: DuckDBRepository, period_key: str = "full_history") -> Dict[str, Any]:
    period = resolve_period(repo, period_key)
    data_quality(repo, period_key)
    summary = _one_row(repo.execute_sql(load_query("agent/capital_coverage_v2.sql")))
    return {"meta": build_meta(period), "summary": summary, "items": []}


def inventory_health(
    repo: DuckDBRepository,
    period_key: str = "full_history",
    category: Optional[str] = None,
    coverage_days: float = DEFAULT_COVERAGE_DAYS,
    limit: int = 25,
) -> Dict[str, Any]:
    period = resolve_period(repo, period_key)
    data_quality(repo, period_key)
    category = validate_category(repo, category)
    limit = validate_limit(limit)
    if not isinstance(coverage_days, (int, float)) or not math.isfinite(coverage_days) or coverage_days <= 0:
        raise ValueError("coverage_days deve ser um número positivo.")
    # O limite SQL permanece no universo conhecido de 5.000 SKUs para que o
    # resumo seja global; ``limit`` recorta somente a lista apresentada.
    params = [
        period.start, period.end, period.start, period.end,
        *([period.days] * 6), float(coverage_days), *([period.days] * 3),
        category, category, 5000,
    ]
    df = repo.execute_sql(load_query("agent/inventory_health_v2.sql"), params)
    items = records(df.head(limit))
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
    repo: DuckDBRepository, period_key: str = "full_history", category: Optional[str] = None, limit: int = 20
) -> Dict[str, Any]:
    period = resolve_period(repo, period_key)
    category = validate_category(repo, category)
    limit = validate_limit(limit)
    df = repo.execute_sql(
        load_query("agent/sales_demand_v2.sql"),
        [period.start, period.end, category, category, 5000],
    )
    summary = {
        "skus": len(df),
        "unidades_aprovadas": float(df["unidades_aprovadas"].sum()) if not df.empty else 0.0,
        "receita_efetiva": float(df["receita_efetiva"].sum()) if not df.empty else 0.0,
        "margem_efetiva": float(df["margem_efetiva"].sum()) if not df.empty else 0.0,
    }
    warnings = ["Nenhuma venda aprovada válida foi observada na janela."] if df.empty else []
    return {"meta": build_meta(period, warnings), "summary": summary, "items": records(df.head(limit))}


def returns_risk(
    repo: DuckDBRepository,
    period_key: str = "full_history",
    min_orders: int = 10,
    min_returns: int = 2,
    limit: int = 20,
) -> Dict[str, Any]:
    period = resolve_period(repo, period_key)
    if min_orders < 1 or min_returns < 0:
        raise ValueError("Limites de pedidos/devoluções inválidos.")
    limit = validate_limit(limit)
    df = repo.execute_sql(
        load_query("agent/returns_v2.sql"),
        [period.start, period.end, int(min_orders), int(min_returns), 5000],
    )
    return {
        "meta": build_meta(period, ["Motivos são declarações registradas, não causas-raiz comprovadas."]),
        "summary": {"skus": len(df)},
        "items": records(df.head(limit)),
    }


def discontinued_capital(
    repo: DuckDBRepository, period_key: str = "full_history", category: Optional[str] = None, limit: int = 20
) -> Dict[str, Any]:
    period = resolve_period(repo, period_key)
    data_quality(repo, period_key)
    category = validate_category(repo, category)
    limit = validate_limit(limit)
    df = repo.execute_sql(load_query("agent/discontinued_items_v2.sql"), [category, category, 5000])
    covered = df[df["custo_unitario_vendas"].notna()] if not df.empty else df
    summary = {
        "skus_retornados": len(df),
        "skus_valorados": int(df["custo_unitario_vendas"].notna().sum()) if not df.empty else 0,
        "skus_excluidos_sem_custo": int(df["custo_unitario_vendas"].isna().sum()) if not df.empty else 0,
        "capital_fisico": float(covered["capital_fisico"].sum()) if not covered.empty else 0.0,
        "capital_disponivel": float(covered["capital_disponivel"].sum()) if not covered.empty else 0.0,
    }
    return {"meta": build_meta(period), "summary": summary, "items": records(df.head(limit))}


def sku_deep_dive(repo: DuckDBRepository, sku_id: str, period_key: str = "full_history") -> Dict[str, Any]:
    period = resolve_period(repo, period_key)
    data_quality(repo, period_key)
    sku_id = validate_sku(sku_id)
    df = repo.execute_sql(
        load_query("agent/sku_deep_dive_v2.sql"),
        [period.start, period.end, sku_id, sku_id, sku_id],
    )
    warnings = ["Lead time exibido é cadastral; a base não permite medir lead time realizado de reposição."]
    if df.empty:
        warnings.append(f"SKU {sku_id} não encontrado na posição de estoque.")
    return {"meta": build_meta(period, warnings), "summary": {"found": not df.empty}, "items": records(df)}


def liquidation(
    repo: DuckDBRepository,
    period_key: str = "full_history",
    category: Optional[str] = None,
    discount_pct: float = 30.0,
) -> Dict[str, Any]:
    period = resolve_period(repo, period_key)
    data_quality(repo, period_key)
    category = validate_category(repo, category)
    if not isinstance(discount_pct, (int, float)) or not math.isfinite(discount_pct) or not 0 <= discount_pct <= 90:
        raise ValueError("desconto_pct deve estar entre 0 e 90.")
    df = repo.execute_sql(
        load_query("agent/liquidation_v2.sql"),
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
    for sell_through in (0.25, 0.50, 0.75, 1.00):
        units = eligible["estoque_disponivel"] * sell_through
        capital = units * eligible["custo_unitario_vendas"]
        revenue_before = units * eligible["preco_liquido_unitario"] * factor
        revenue_adjusted = revenue_before * (1 - eligible["taxa_devolucao_categoria"].fillna(0))
        contribution = revenue_adjusted - capital - units * eligible["frete_unitario"]
        scenarios.append({
            "sell_through_pct": int(sell_through * 100),
            "unidades_cenario": float(units.sum()),
            "capital_historico_envolvido": float(capital.sum()),
            "receita_antes_devolucoes": float(revenue_before.sum()),
            "receita_ajustada_devolucoes": float(revenue_adjusted.sum()),
            "contribuicao_estimada": float(contribution.sum()),
        })
    summary = {
        "categoria": category or "Todas",
        "desconto_pct": float(discount_pct),
        "skus_descontinuados_com_saldo": len(df),
        "skus_elegiveis": len(eligible),
        "skus_excluidos_sem_custo_ou_preco": int(len(df) - len(eligible)),
        "scenarios": scenarios,
        "central_scenario": next(s for s in scenarios if s["sell_through_pct"] == 50),
        "limitations": [
            "Não há modelagem de retorno físico do item devolvido.",
            "Impostos, comissões, logística reversa e elasticidade de preço não estão disponíveis.",
        ],
    }
    warnings = []
    if df.empty or eligible.empty:
        warnings.append("Não há SKUs descontinuados com custo e preço válidos para simular nessa seleção.")
    return {"meta": build_meta(period, warnings), "summary": summary, "items": records(df)}


def _sum_column(items: Iterable[dict], key: str) -> float:
    return float(sum(float(item.get(key) or 0) for item in items))


def build_audit_package(
    repo: DuckDBRepository,
    period_key: str = "full_history",
    coverage_days: float = DEFAULT_COVERAGE_DAYS,
) -> Dict[str, Any]:
    """Reconcilia fatos, filas independentes, categorias e cenários."""
    period = resolve_period(repo, period_key)
    quality = data_quality(repo, period_key)
    health = inventory_health(repo, period_key, coverage_days=coverage_days, limit=5000)
    capital = capital_coverage(repo, period_key)
    demand = demand_matrix(repo, period_key, limit=5000)
    returns = returns_risk(repo, period_key, limit=5000)
    liquidation_data = liquidation(repo, period_key, discount_pct=30.0)
    all_items = health["items"]
    queues = {
        "ruptura_atual": [x for x in all_items if x["ruptura_atual"]],
        "ponto_pedido": [x for x in all_items if x["abaixo_ou_no_ponto_pedido"]],
        "exposicao_lead_time": [x for x in all_items if x["exposicao_lead_time"]],
        "alta_cobertura": [x for x in all_items if x["alta_cobertura_historica"] and not x["is_descontinuado"]],
        "sem_venda_observada": [x for x in all_items if x["sem_venda_observada"]],
    }
    # Nenhuma fila de investigação/reposição inclui descontinuados ou itens sem demanda observada.
    queues["investigacao_reposicao"] = [
        x for x in queues["exposicao_lead_time"] if not x["is_descontinuado"] and not x["sem_venda_observada"]
    ]

    category_summary: dict[str, dict] = {}
    for item in all_items:
        cat = item.get("categoria") or "Não informado"
        row = category_summary.setdefault(cat, {
            "categoria": cat, "ruptura_atual": 0, "ponto_pedido": 0,
            "exposicao_lead_time": 0, "alta_cobertura": 0,
            "margem_potencialmente_exposta": 0.0,
        })
        row["ruptura_atual"] += int(bool(item["ruptura_atual"]))
        row["ponto_pedido"] += int(bool(item["abaixo_ou_no_ponto_pedido"]))
        row["exposicao_lead_time"] += int(bool(item["exposicao_lead_time"]))
        row["alta_cobertura"] += int(bool(item["alta_cobertura_historica"] and not item["is_descontinuado"]))
        row["margem_potencialmente_exposta"] += float(item.get("margem_potencialmente_exposta") or 0)
    categories = sorted(
        category_summary.values(),
        key=lambda x: (-x["margem_potencialmente_exposta"], -x["ruptura_atual"], x["categoria"]),
    )
    exposure = queues["investigacao_reposicao"]
    formulas_valid = all(
        math.isclose(
            float(item["necessidade_lead_time"]),
            float(item["demanda_diaria_historica"]) * float(item["lead_time_cadastral_dias"]),
            rel_tol=1e-9, abs_tol=1e-7,
        )
        and math.isclose(
            float(item["deficit_potencial_unidades"]),
            max(float(item["necessidade_lead_time"]) - float(item["estoque_disponivel"]), 0.0),
            rel_tol=1e-9, abs_tol=1e-7,
        )
        for item in exposure
    )
    summary = {
        "methodology_banner": methodology_banner(period),
        "capital": capital["summary"],
        "operational": {key: len(value) for key, value in queues.items()},
        "lead_time_exposure": {
            "skus": len(exposure),
            "receita_antes_devolucao": _sum_column(exposure, "receita_antes_devolucao_exposta"),
            "receita_ajustada_devolucao": _sum_column(exposure, "receita_ajustada_exposta"),
            "margem_potencialmente_exposta": _sum_column(exposure, "margem_potencialmente_exposta"),
            "interpretation": "Cenário secundário de priorização baseado em tendência histórica; não é perda realizada.",
        },
        "liquidation": liquidation_data["summary"],
        "demand": demand["summary"],
        "returns": returns["summary"],
        "financial_coverage": {
            "skus_covered": capital["summary"].get("skus_com_custo_vendas"),
            "skus_excluded": capital["summary"].get("skus_sem_custo_vendas"),
        },
        "top_attention_category": categories[0] if categories else None,
        "category_summary": categories,
        "data_quality": quality,
        "reconciliation": {
            "exposure_formulas_valid": formulas_valid,
            "exposure_items_equal_summary": len(exposure) == len(queues["investigacao_reposicao"]),
            "liquidation_scenarios_proportional": math.isclose(
                liquidation_data["summary"]["scenarios"][3]["capital_historico_envolvido"],
                4 * liquidation_data["summary"]["scenarios"][0]["capital_historico_envolvido"],
                rel_tol=1e-9, abs_tol=0.02,
            ),
        },
    }
    warnings = [
        "A posição de estoque não possui data de snapshot confirmada.",
        "Vendas representam tendência histórica observada, não previsão atual.",
        "Valores de exposição e liquidação são cenários, não perdas realizadas.",
    ]
    if demand["summary"]["skus"] == 0:
        warnings.append("Nenhuma venda aprovada válida foi observada na janela; rankings e ações foram omitidos.")
    return {
        "meta": build_meta(period, warnings),
        "summary": summary,
        "items": exposure[:25],
        "queues": {key: value[:25] for key, value in queues.items()},
    }
