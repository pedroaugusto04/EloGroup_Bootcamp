"""
src/agent/inventory_analytics/consolidation.py
Consolidação factual e reconciliação dos pacotes de auditoria de estoque.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable

from src.agent.periods import build_meta, methodology_banner, resolve_period
from src.infrastructure.database import DuckDBRepository
from .financial import (
    DEFAULT_LIQUIDATION_DISCOUNT_PCT,
    capital_coverage,
    liquidation,
    returns_risk,
)
from .operational import DEFAULT_COVERAGE_DAYS, demand_matrix, inventory_health
from .quality import data_quality


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
    health = inventory_health(repo, period_key, coverage_days=coverage_days, limit=None)
    capital = capital_coverage(repo, period_key)
    demand = demand_matrix(repo, period_key, limit=1000)
    returns = returns_risk(repo, period_key, limit=1000)
    liquidation_data = liquidation(repo, period_key, discount_pct=DEFAULT_LIQUIDATION_DISCOUNT_PCT)
    all_items = health["items"]
    for item in all_items:
        daily_demand = float(item.get("demanda_diaria_historica") or 0)
        available = float(item.get("estoque_disponivel") or 0)
        unit_cost = float(item.get("custo_unitario_historico") or 0)
        is_disc = bool(item.get("is_descontinuado"))
        is_high_cov = bool(item.get("alta_cobertura_historica"))
        if is_high_cov and not is_disc and daily_demand > 0:
            target_stock = daily_demand * float(coverage_days)
            excess_units = max(available - target_stock, 0.0)
            item["unidades_excedentes"] = excess_units
            item["capital_excedente"] = excess_units * unit_cost
        else:
            item["unidades_excedentes"] = 0.0
            item["capital_excedente"] = 0.0

    queues = {
        "ruptura_atual": [x for x in all_items if x["ruptura_atual"]],
        "ponto_pedido": [x for x in all_items if x["abaixo_ou_no_ponto_pedido"]],
        "exposicao_lead_time": [x for x in all_items if x["exposicao_lead_time"]],
        "alta_cobertura": sorted(
            [x for x in all_items if x["alta_cobertura_historica"] and not x["is_descontinuado"]],
            key=lambda x: -float(x.get("capital_excedente") or 0),
        ),
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
            "categoria": cat, "skus_ativos": 0, "ruptura_atual": 0, "ponto_pedido": 0,
            "exposicao_lead_time": 0, "alta_cobertura": 0,
            "margem_potencialmente_exposta": 0.0,
            "unidades_excedentes": 0.0,
            "capital_excedente": 0.0,
        })
        row["skus_ativos"] += int(not item["is_descontinuado"])
        row["ruptura_atual"] += int(bool(item["ruptura_atual"]))
        row["ponto_pedido"] += int(bool(item["abaixo_ou_no_ponto_pedido"]))
        row["exposicao_lead_time"] += int(bool(item["exposicao_lead_time"]))
        row["alta_cobertura"] += int(bool(item["alta_cobertura_historica"] and not item["is_descontinuado"]))
        row["margem_potencialmente_exposta"] += float(item.get("margem_potencialmente_exposta") or 0)
        row["unidades_excedentes"] += float(item.get("unidades_excedentes") or 0)
        row["capital_excedente"] += float(item.get("capital_excedente") or 0)
    categories = sorted(
        category_summary.values(),
        key=lambda x: (-x["margem_potencialmente_exposta"], -x["ruptura_atual"], x["categoria"]),
    )
    exposure = queues["investigacao_reposicao"]
    supplier_summary: dict[str, dict] = {}
    for item in exposure:
        supplier = item.get("fornecedor_id") or "Não informado"
        row = supplier_summary.setdefault(supplier, {
            "fornecedor_id": supplier, "skus_expostos": 0,
            "deficit_potencial_unidades": 0.0, "receita_ajustada_exposta": 0.0,
            "margem_potencialmente_exposta": 0.0,
        })
        row["skus_expostos"] += 1
        row["deficit_potencial_unidades"] += float(item.get("deficit_potencial_unidades") or 0)
        row["receita_ajustada_exposta"] += float(item.get("receita_ajustada_exposta") or 0)
        row["margem_potencialmente_exposta"] += float(item.get("margem_potencialmente_exposta") or 0)
    suppliers = sorted(
        supplier_summary.values(),
        key=lambda x: (-x["margem_potencialmente_exposta"], -x["skus_expostos"], x["fornecedor_id"]),
    )
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
    operational_summary = {key: len(value) for key, value in queues.items()}
    active_skus = int(capital["summary"]["total_skus"] - capital["summary"]["skus_descontinuados"])
    total_unidades_excedentes = _sum_column(queues["alta_cobertura"], "unidades_excedentes")
    total_capital_excedente = _sum_column(queues["alta_cobertura"], "capital_excedente")
    operational_summary.update({
        "active_skus": active_skus,
        "coverage_threshold_days": float(coverage_days),
        "high_coverage_share_active_pct": (
            operational_summary["alta_cobertura"] / active_skus * 100 if active_skus else None
        ),
        "unidades_excedentes": total_unidades_excedentes,
        "capital_excedente": total_capital_excedente,
    })
    central_liquidation = liquidation_data["summary"]["central_scenario"]
    liquidation_value_fields = (
        "unidades_cenario", "capital_historico_envolvido", "receita_antes_devolucoes",
        "ajuste_estimado_devolucoes", "receita_ajustada_devolucoes",
        "frete_historico_estimado", "contribuicao_estimada",
    )
    liquidation_categories_reconciled = all(
        math.isclose(
            _sum_column(liquidation_data["summary"]["central_by_category"], field),
            float(central_liquidation[field]), rel_tol=1e-9, abs_tol=0.02,
        )
        for field in liquidation_value_fields
    )
    supplier_exposure_reconciled = (
        math.isclose(_sum_column(suppliers, "margem_potencialmente_exposta"),
                     _sum_column(exposure, "margem_potencialmente_exposta"), rel_tol=1e-9, abs_tol=0.02)
        and sum(int(row["skus_expostos"]) for row in suppliers) == len(exposure)
    )
    liquidation_leader = (liquidation_data["summary"]["central_by_category"] or [{}])[0]
    liq_cat_name = liquidation_leader.get("categoria") or "categoria líder"
    top_cat_name = categories[0]["categoria"] if categories else "categoria prioritária"
    top_supplier_name = suppliers[0]["fornecedor_id"] if suppliers else "Fornecedor principal"
    decision_matrix = [
        {
            "priority": "P1", "horizon": "30 dias", "type": "Quick Win",
            "initiative": f"Liquidação direcionada de descontinuados ({liq_cat_name})",
            "decision": f"Executar liquidação focada na categoria {liq_cat_name} para destravar capital parado e capturar margem de contribuição projetada.",
            "evidence": ["summary.liquidation.central_scenario", "summary.liquidation.central_by_category"],
            "scope": liquidation_leader.get("categoria"),
            "financial_metric": "contribuicao_estimada",
            "financial_value": liquidation_leader.get("contribuicao_estimada"),
            "effort": "Estimativa comercial e definição de canais de liquidação.",
            "decision_gate": "Avaliar sell-through e margem líquida realizada no primeiro lote piloto.",
        },
        {
            "priority": "P1", "horizon": "30 dias", "type": "Quick Win",
            "initiative": f"Reposição prioritária dos SKUs ativos expostos ({top_cat_name})",
            "decision": f"Iniciar triagem e reposição emergencial dos {len(exposure)} SKUs em risco de ruptura, priorizando a categoria {top_cat_name} e o fornecedor {top_supplier_name}.",
            "evidence": ["summary.lead_time_exposure", "summary.category_summary", "items", "summary.supplier_exposure_summary"],
            "scope": top_cat_name,
            "financial_metric": "margem_potencialmente_exposta",
            "financial_value": (categories[0]["margem_potencialmente_exposta"] if categories else None),
            "effort": "Negociação de pedido emergencial com compras e fornecedores.",
            "decision_gate": "Confirmação de prazo de entrega e lote mínimo com fornecedor.",
        },
        {
            "priority": "P2", "horizon": "60 dias", "type": "Ação Estrutural",
            "initiative": "Recalibração de ponto de pedido e sobre-estoque",
            "decision": f"Ajustar parâmetros de ponto de pedido e suspender compras OTB para os {operational_summary['alta_cobertura']} SKUs com cobertura excessiva (>{int(coverage_days)} dias) para liberar capital imobilizado.",
            "evidence": ["summary.operational.high_coverage_share_active_pct", "summary.operational.capital_excedente", "summary.category_summary"],
            "scope": "SKUs ativos com alta cobertura",
            "financial_metric": "capital_excedente",
            "financial_value": total_capital_excedente,
            "effort": "Revisão de curvas ABC/XYZ com Planejamento e congelamento de ordens de compra OTB.",
            "decision_gate": "Aprovação dos novos pontos de pedido por categoria e validação do OTB liberado.",
        },
        {
            "priority": "P3", "horizon": "90 dias", "type": "Governança & Processos",
            "initiative": "Governança de dados de estoque e lead time real",
            "decision": "Implementar snapshots datados de estoque e monitoramento de lead time real por fornecedor para automatizar reposição com segurança.",
            "evidence": ["meta.stock_as_of", "summary.capital", "summary.data_quality"],
            "scope": "Processo e integrações Estoque/Vendas",
            "financial_metric": None, "financial_value": None,
            "effort": "Alinhamento com equipes de Dados, Logística e TI.",
            "decision_gate": "Auditoria de dados com 100% de cobertura de custo e lead time real medido.",
        },
    ]

    summary = {
        "methodology_banner": methodology_banner(period),
        "capital": capital["summary"],
        "operational": operational_summary,
        "lead_time_exposure": {
            "skus": len(exposure),
            "receita_antes_devolucao": _sum_column(exposure, "receita_antes_devolucao_exposta"),
            "receita_ajustada_devolucao": _sum_column(exposure, "receita_ajustada_exposta"),
            "margem_potencialmente_exposta": _sum_column(exposure, "margem_potencialmente_exposta"),
            "interpretation": "Margem em risco de ruptura calculada no lead time cadastral sobre o giro histórico.",
        },
        "overstock_exposure": {
            "skus": operational_summary["alta_cobertura"],
            "unidades_excedentes": total_unidades_excedentes,
            "capital_excedente": total_capital_excedente,
            "interpretation": f"Capital imobilizado acima de {int(coverage_days)} dias de giro histórico para SKUs ativos.",
        },
        "top_overstock_skus": queues["alta_cobertura"][:10],
        "liquidation": liquidation_data["summary"],
        "demand": demand["summary"],
        "returns": returns["summary"],
        "financial_coverage": {
            "skus_covered": capital["summary"].get("skus_com_custo_vendas"),
            "skus_excluded": capital["summary"].get("skus_sem_custo_vendas"),
        },
        "top_attention_category": categories[0] if categories else None,
        "category_summary": categories,
        "supplier_exposure_summary": suppliers,
        "decision_matrix": decision_matrix,
        "data_quality": quality,
        "reconciliation": {
            "exposure_formulas_valid": formulas_valid,
            "exposure_items_equal_summary": len(exposure) == len(queues["investigacao_reposicao"]),
            "liquidation_categories_equal_central": liquidation_categories_reconciled,
            "supplier_exposure_equal_summary": supplier_exposure_reconciled,
            "decision_matrix_traceable": len(decision_matrix) == 4 and all(row["evidence"] for row in decision_matrix),
            "liquidation_scenarios_proportional": math.isclose(
                liquidation_data["summary"]["scenarios"][3]["capital_historico_envolvido"],
                4 * liquidation_data["summary"]["scenarios"][0]["capital_historico_envolvido"],
                rel_tol=1e-9, abs_tol=0.02,
            ),
        },
    }
    warnings = [
        "A posição de estoque não possui data de snapshot confirmada.",
        "Vendas representam tendência histórica observada.",
    ]
    if demand["summary"]["skus"] == 0:
        warnings.append("Nenhuma venda aprovada válida foi observada na janela; rankings e ações foram omitidos.")
    return {
        "meta": build_meta(period, warnings),
        "summary": summary,
        "items": exposure[:25],
        "queues": {key: value[:25] for key, value in queues.items()},
    }


__all__ = ["build_audit_package"]
