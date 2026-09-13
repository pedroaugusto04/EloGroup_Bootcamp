"""
src/agent/deterministic_checks.py
Validações e regras determinísticas de integridade e reconciliação contábil do parecer de estoque.
"""

from typing import Any, Dict


def run_deterministic_checks(package: dict) -> Dict[str, bool]:
    """Executa a bateria de 13 validações determinísticas no envelope de auditoria."""
    meta = package["meta"]
    summary = package["summary"]
    capital = summary["capital"]
    exposure = summary["lead_time_exposure"]
    operational = summary["operational"]
    tolerance = 0.02

    checks = {
        "typed_period": meta["period_key"] in {"full_history", "calendar_2023", "last_90d_observed"},
        "financial_source_is_sales": meta["financial_source"] == "vendas",
        "operational_source_is_stock": meta["operational_source"] == "estoque",
        "stock_reconciliation": abs(
            float(capital.get("capital_fisico") or 0)
            - float(capital.get("capital_reservado") or 0)
            - float(capital.get("capital_disponivel") or 0)
        ) <= tolerance,
        "financial_coverage_reconciled": (
            int(capital.get("skus_com_custo_vendas") or 0)
            + int(capital.get("skus_sem_custo_vendas") or 0)
            == int(capital.get("total_skus") or 0)
        ),
        "discontinued_never_replenished": all(
            not item.get("is_descontinuado") for item in package.get("queues", {}).get("investigacao_reposicao", [])
        ),
        "exposure_count_reconciled": int(exposure["skus"]) == int(operational["investigacao_reposicao"]),
        "data_quality_approved": summary["data_quality"]["blocking_errors"] == 0,
        "liquidation_has_four_scenarios": len(summary["liquidation"]["scenarios"]) == 4,
        "lead_time_formulas_reconciled": summary["reconciliation"]["exposure_formulas_valid"],
        "liquidation_formulas_reconciled": summary["reconciliation"]["liquidation_scenarios_proportional"],
        "liquidation_categories_reconciled": summary["reconciliation"]["liquidation_categories_equal_central"],
        "supplier_exposure_reconciled": summary["reconciliation"]["supplier_exposure_equal_summary"],
        "decision_matrix_traceable": summary["reconciliation"]["decision_matrix_traceable"],
    }
    return checks


__all__ = ["run_deterministic_checks"]
