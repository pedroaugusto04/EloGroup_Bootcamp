"""
src/api/routes/audit.py
Rotas de Auditoria de Integridade de Dados, Relações entre Bases e Dispersão / Outliers (Tukey IQR).
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Query
import numpy as np
import pandas as pd

from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query

router = APIRouter(prefix="/audit", tags=["audit"])


def _clean_df(df: pd.DataFrame) -> List[dict]:
    if df is None or df.empty:
        return []
    df_clean = df.replace({np.nan: None})
    return df_clean.to_dict(orient="records")


def calculate_iqr_stats(df: pd.DataFrame, col: str) -> Dict[str, Any]:
    """Calcula estatísticas de dispersão e quantis segundo Tukey IQR 1.5x."""
    s = df[col].dropna()
    if len(s) == 0:
        return {"q1": 0, "median": 0, "q3": 0, "iqr": 0, "lower_bound": 0, "upper_bound": 0, "outliers_count": 0, "outliers_pct": 0}
    q1 = float(s.quantile(0.25))
    median = float(s.quantile(0.50))
    q3 = float(s.quantile(0.75))
    iqr = q3 - q1
    lower_bound = float(q1 - 1.5 * iqr)
    upper_bound = float(q3 + 1.5 * iqr)
    outliers = s[(s < lower_bound) | (s > upper_bound)]
    return {
        "q1": q1,
        "median": median,
        "q3": q3,
        "iqr": iqr,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "min": float(s.min()),
        "max": float(s.max()),
        "mean": float(s.mean()),
        "total_records": len(s),
        "outliers_count": int(len(outliers)),
        "outliers_pct": float(len(outliers) / len(s) * 100) if len(s) > 0 else 0.0
    }


# =========================================================================
# 1. INTEGRIDADE RELACIONAL ENTRE BASES
# =========================================================================

@router.get("/relational")
def get_relational_audit():
    repo = DuckDBRepository()

    # 1. MKT vs Vendas Real
    q_mkt_ven = load_query("relacional/mkt_vs_vendas_real.sql")
    mkt_vs_vendas = _clean_df(repo.execute_sql(q_mkt_ven))

    # 2. Estoque vs Vendas Giro
    q_est_ven = load_query("relacional/estoque_vs_vendas_giro.sql")
    estoque_vs_vendas = _clean_df(repo.execute_sql(q_est_ven))

    # 3. Vendas vs Atendimento Atrito
    q_ven_sup = load_query("relacional/vendas_vs_atendimento_atrito.sql")
    vendas_vs_suporte = _clean_df(repo.execute_sql(q_ven_sup))

    # 4. Clientes Ciclo Atrito
    q_cli_sup = load_query("relacional/clientes_ciclo_atrito.sql")
    clientes_vs_suporte = _clean_df(repo.execute_sql(q_cli_sup))

    # 5. Incoerências Mapeadas em DEVELOPMENT.md (Sumário Executivo)
    audit_findings = [
        {
            "dimension": "Janela Temporal",
            "erp_coverage": "Jan/2023 a 26/Jan/2024 (27.758 pedidos em Vendas)",
            "external_coverage": "Atendimento, Marketing e Estoque cobrem 2023 a 2025/2026",
            "impact": "Incompatibilidade temporal direta para análises de 2024 e 2025 na tabela de Vendas.",
            "severity": "Alta"
        },
        {
            "dimension": "Vínculo Clientes x Vendas",
            "erp_coverage": "Apenas 346 dos 15.000 clientes cadastrados (2,3%) aparecem em Vendas",
            "external_coverage": "1 cliente concentra 11.282 compras (40,6%) e 14.355 tickets (40,0%)",
            "impact": "LTV e histórico de pedidos da base de Clientes não reconciliam com o transacional de Vendas.",
            "severity": "Crítica"
        },
        {
            "dimension": "Concentração de Demanda & Atendimento",
            "erp_coverage": "27 clientes concentram 93,6% dos pedidos (25.989 compras) e 93,5% da receita bruta",
            "external_coverage": "Os mesmos 27 clientes geram 93,05% dos tickets de suporte (33.350 chamados)",
            "impact": "A taxa de suporte por pedido é homogênea (~1,28), revelando clientes corporativos/B2B com compras massivas e risco extremo de dependência de receita.",
            "severity": "Crítica"
        },
        {
            "dimension": "Atribuição de Mídia",
            "erp_coverage": "Receita Líquida em Vendas: R$ 14,2M | 20,8k vendas efetivas",
            "external_coverage": "Mídia Declarada: R$ 210,4M investidos | R$ 878,6M receita declarada",
            "impact": "Mídia reporta ROAS inflado por métricas declaradas de campanhas, não pelo faturamento transacional.",
            "severity": "Crítica"
        },
        {
            "dimension": "Custo de Estoque x Vendas",
            "erp_coverage": "Custo unitário na tabela de Vendas (CMV)",
            "external_coverage": "Custo unitário na tabela de Estoque (Correlação r = 0.008)",
            "impact": "Custos do catálogo de Estoque não coincidem com o histórico transacional de Vendas.",
            "severity": "Média"
        },
        {
            "dimension": "Tickets sem Pedido em Vendas",
            "erp_coverage": "IDs de pedidos na tabela Vendas limitados a ~27k",
            "external_coverage": "65,4% dos chamados de suporte apontam para IDs de pedidos inexistentes em Vendas",
            "impact": "Atendimento opera sobre transações não extraídas no extrato de Vendas.",
            "severity": "Alta"
        }
    ]

    return {
        "mkt_vs_sales": mkt_vs_vendas,
        "inventory_vs_sales": estoque_vs_vendas,
        "sales_vs_support": vendas_vs_suporte,
        "customers_vs_support": clientes_vs_suporte,
        "audit_findings": audit_findings
    }


# =========================================================================
# 2. DISPERSÃO & DETECÇÃO DE OUTLIERS (TUKEY IQR)
# =========================================================================

@router.get("/outliers")
def get_outliers_audit(
    table: str = Query("vendas", description="Tabela para análise (vendas, estoque, clientes, atendimento, marketing)"),
    metric: Optional[str] = Query(None, description="Coluna numérica para cálculo de IQR")
):
    repo = DuckDBRepository()

    valid_tables = {
        "vendas": {
            "default_col": "desconto_reais",
            "cols": ["desconto_reais", "receita_bruta", "receita_liquida", "margem_calculada", "margem_pct", "custo_frete", "tempo_entrega_real"],
            "group_by": "categoria",
            "where": "status_pagamento = 'Aprovado'"
        },
        "estoque": {
            "default_col": "valor_total_estoque",
            "cols": ["valor_total_estoque", "estoque_disponivel", "custo_unitario", "preco_venda_sugerido", "lead_time_reposicao"],
            "group_by": "categoria",
            "where": ""
        },
        "clientes": {
            "default_col": "ltv_acumulado",
            "cols": ["ltv_acumulado", "total_pedidos_historico", "renda_estimada", "idade"],
            "group_by": "segmento_rfm",
            "where": ""
        },
        "atendimento": {
            "default_col": "tempo_resolucao_horas",
            "cols": ["tempo_resolucao_horas", "tempo_primeira_resposta_minutos", "nota_csat", "custo_operacional_ticket"],
            "group_by": "canal_entrada",
            "where": ""
        },
        "marketing": {
            "default_col": "cac",
            "cols": ["cac", "roas", "investimento_reais", "receita_gerada", "cliques", "conversoes"],
            "group_by": "canal",
            "where": ""
        }
    }

    if table not in valid_tables:
        table = "vendas"

    cfg = valid_tables[table]
    target_metric = metric if (metric and metric in cfg["cols"]) else cfg["default_col"]
    where_sql = f"WHERE {cfg['where']}" if cfg["where"] else ""

    df = repo.execute_sql(f"SELECT {target_metric}, {cfg['group_by']} FROM {table} {where_sql}")
    stats = calculate_iqr_stats(df, target_metric)

    # Amostra por categoria / dimensão
    by_dim = []
    for val, grp in df.groupby(cfg["group_by"]):
        dim_stats = calculate_iqr_stats(grp, target_metric)
        dim_stats["dimension_value"] = str(val)
        by_dim.append(dim_stats)

    return {
        "table": table,
        "available_tables": list(valid_tables.keys()),
        "selected_metric": target_metric,
        "available_metrics": cfg["cols"],
        "group_by_dimension": cfg["group_by"],
        "overall_stats": stats,
        "by_dimension": by_dim
    }
