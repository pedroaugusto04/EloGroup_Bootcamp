"""
src/api/routes/analytics.py
Rotas de analytics para Visão Geral, Vendas & Margem, Marketing, Estoque, Clientes e Suporte.
Reutiliza 100% das queries SQL em src/queries e o DuckDBRepository.
"""

from typing import List, Optional
from fastapi import APIRouter, Query
import numpy as np
import pandas as pd

from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _clean_df(df: pd.DataFrame) -> List[dict]:
    """Converte DataFrame para lista de dicionários sanitizando NaNs e tipos numéricos."""
    if df is None or df.empty:
        return []
    df_clean = df.replace({np.nan: None})
    return df_clean.to_dict(orient="records")


def get_repo() -> DuckDBRepository:
    return DuckDBRepository()


# =========================================================================
# 1. VISÃO EXECUTIVA & MACRO
# =========================================================================

@router.get("/executive")
def get_executive_overview(
    status: str = Query("Aprovado", description="Status de pagamento"),
    categoria: Optional[List[str]] = Query(None, description="Filtro de categorias"),
    ano: str = Query("Todos", description="Ano do pedido")
):
    repo = get_repo()
    where_clauses = []
    if status != "Todos":
        where_clauses.append(f"status_pagamento = '{status}'")
    if categoria:
        cats_str = "', '".join(categoria)
        where_clauses.append(f"categoria IN ('{cats_str}')")
    if ano != "Todos":
        where_clauses.append(f"ano = {ano}")
    
    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    q_kpi = load_query("visao_geral/kpis_consolidados.sql", where_sql=where_sql)
    df_kpi = repo.execute_sql(q_kpi)
    kpis = _clean_df(df_kpi)[0] if not df_kpi.empty else {}

    q_trend = load_query("visao_geral/evolucao_mensal.sql", where_sql=where_sql)
    trend = _clean_df(repo.execute_sql(q_trend))

    q_canal = load_query("visao_geral/receita_por_canal.sql", where_sql=where_sql)
    canais = _clean_df(repo.execute_sql(q_canal))

    q_cat = load_query("vendas/margem_por_categoria.sql", where_sql=where_sql)
    categorias = _clean_df(repo.execute_sql(q_cat))

    return {
        "kpis": kpis,
        "monthly_trend": trend,
        "channels": canais,
        "categories": categorias,
    }


# =========================================================================
# 2. VENDAS & DECOMPOSIÇÃO DE MARGEM
# =========================================================================

@router.get("/sales")
def get_sales_analytics(
    canal: Optional[List[str]] = Query(None),
    categoria: Optional[List[str]] = Query(None)
):
    repo = get_repo()
    where_clauses = ["status_pagamento = 'Aprovado'"]
    if canal:
        can_str = "', '".join(canal)
        where_clauses.append(f"canal IN ('{can_str}')")
    if categoria:
        cat_str = "', '".join(categoria)
        where_clauses.append(f"categoria IN ('{cat_str}')")
    
    where_sql = f"WHERE {' AND '.join(where_clauses)}"

    q_decomp = load_query("vendas/decomposicao_margem.sql", where_sql=where_sql)
    decomp = _clean_df(repo.execute_sql(q_decomp))[0] if not repo.execute_sql(q_decomp).empty else {}

    q_cat = load_query("vendas/margem_por_categoria.sql", where_sql=where_sql)
    cat_margin = _clean_df(repo.execute_sql(q_cat))

    q_dev = load_query("vendas/motivos_devolucao.sql")
    returns = _clean_df(repo.execute_sql(q_dev))

    q_skus = load_query("vendas/top_skus_faturamento.sql", where_sql=where_sql, limit=50)
    top_skus = _clean_df(repo.execute_sql(q_skus))

    return {
        "decomposition": decomp,
        "categories_margin": cat_margin,
        "returns_impact": returns,
        "top_skus": top_skus
    }


# =========================================================================
# 3. MARKETING & EFICIÊNCIA DE CANAIS
# =========================================================================

@router.get("/marketing")
def get_marketing_analytics(
    canal: Optional[List[str]] = Query(None)
):
    repo = get_repo()
    where_sql = f"WHERE canal IN ('{chr(39).join(canal)}')" if canal else ""
    if canal:
        c_str = "', '".join(canal)
        where_sql = f"WHERE canal IN ('{c_str}')"

    q_kpi = load_query("marketing/kpis_marketing.sql", where_sql=where_sql)
    df_kpi = repo.execute_sql(q_kpi)
    kpis = _clean_df(df_kpi)[0] if not df_kpi.empty else {}

    q_canal = load_query("marketing/eficiencia_canais.sql", where_sql=where_sql)
    channels = _clean_df(repo.execute_sql(q_canal))

    return {
        "kpis": kpis,
        "channels": channels
    }


# =========================================================================
# 4. ESTOQUE & SUPRIMENTOS
# =========================================================================

@router.get("/inventory")
def get_inventory_analytics(
    categoria: Optional[List[str]] = Query(None)
):
    repo = get_repo()
    if categoria:
        cat_str = "', '".join(categoria)
        where_sql = f"WHERE categoria IN ('{cat_str}')"
        crit_where = f"WHERE (em_ruptura = true OR is_estoque_critico = true) AND categoria IN ('{cat_str}')"
    else:
        where_sql = ""
        crit_where = "WHERE em_ruptura = true OR is_estoque_critico = true"

    q_kpi = load_query("estoque/kpis_estoque.sql", where_sql=where_sql)
    df_kpi = repo.execute_sql(q_kpi)
    kpis = _clean_df(df_kpi)[0] if not df_kpi.empty else {}

    q_cat = load_query("estoque/ruptura_por_categoria.sql", where_sql=where_sql)
    categories = _clean_df(repo.execute_sql(q_cat))

    q_crit = load_query("estoque/skus_criticos.sql", crit_where=crit_where, limit=50)
    critical_skus = _clean_df(repo.execute_sql(q_crit))

    # Hipótese 6: Descompasso de Estoque
    q_desc = load_query("hipotese_6_decisao_gestao/descompasso_estoque_ruptura.sql", where_sql="")
    discontinued_breakdown = _clean_df(repo.execute_sql(q_desc))

    return {
        "kpis": kpis,
        "categories_rupture": categories,
        "critical_skus": critical_skus,
        "status_breakdown": discontinued_breakdown
    }


# =========================================================================
# 5. CLIENTES & PERFIL CADASTRAL (RFM)
# =========================================================================

@router.get("/customers")
def get_customers_analytics(
    segmento: Optional[List[str]] = Query(None)
):
    repo = get_repo()
    if segmento:
        seg_str = "', '".join(segmento)
        where_sql = f"WHERE segmento_rfm IN ('{seg_str}')"
        uf_where = f"WHERE segmento_rfm IN ('{seg_str}') AND estado IS NOT NULL"
    else:
        where_sql = ""
        uf_where = "WHERE estado IS NOT NULL"

    q_kpi = load_query("clientes/kpis_clientes.sql", where_sql=where_sql)
    df_kpi = repo.execute_sql(q_kpi)
    kpis = _clean_df(df_kpi)[0] if not df_kpi.empty else {}

    q_rfm = load_query("clientes/segmentos_rfm.sql", where_sql=where_sql)
    segments = _clean_df(repo.execute_sql(q_rfm))

    q_uf = load_query("clientes/top_estados.sql", uf_where=uf_where, limit=10)
    top_states = _clean_df(repo.execute_sql(q_uf))

    q_fid = load_query("clientes/nivel_fidelidade.sql", where_sql=where_sql)
    loyalty = _clean_df(repo.execute_sql(q_fid))

    # Hipótese 5: Pareto e Canais de Aquisição
    q_pareto = load_query("hipotese_5_clientes/distribuicao_rfm_pareto.sql", where_sql="")
    pareto = _clean_df(repo.execute_sql(q_pareto))

    q_acq = load_query("hipotese_5_clientes/qualidade_canal_aquisicao.sql", where_sql="")
    acq_channels = _clean_df(repo.execute_sql(q_acq))

    return {
        "kpis": kpis,
        "segments": segments,
        "top_states": top_states,
        "loyalty": loyalty,
        "pareto_distribution": pareto,
        "acquisition_channels": acq_channels
    }


# =========================================================================
# 6. ATENDIMENTO & IA (HIPÓTESE 4)
# =========================================================================

@router.get("/support")
def get_support_analytics(
    canal: Optional[List[str]] = Query(None)
):
    repo = get_repo()
    where_sql = f"WHERE canal_entrada IN ('{chr(39).join(canal)}')" if canal else ""
    if canal:
        c_str = "', '".join(canal)
        where_sql = f"WHERE canal_entrada IN ('{c_str}')"

    q_kpi = load_query("atendimento/kpis_atendimento.sql", where_sql=where_sql)
    df_kpi = repo.execute_sql(q_kpi)
    kpis = _clean_df(df_kpi)[0] if not df_kpi.empty else {}

    q_canais = load_query("atendimento/canais_entrada.sql", where_sql=where_sql)
    channels = _clean_df(repo.execute_sql(q_canais))

    q_motivos = load_query("atendimento/volume_motivos.sql", where_sql=where_sql)
    motivos = _clean_df(repo.execute_sql(q_motivos))

    q_csat = load_query("atendimento/distribuicao_csat.sql", where_sql=where_sql)
    csat = _clean_df(repo.execute_sql(q_csat))

    # Hipótese 4: Causas Raiz & Automação com IA
    q_root = load_query("hipotese_4_atendimento/causas_raiz_e_automacao.sql", where_sql="")
    root_causes = _clean_df(repo.execute_sql(q_root))

    return {
        "kpis": kpis,
        "channels": channels,
        "reasons": motivos,
        "csat_distribution": csat,
        "root_causes_ai": root_causes
    }


# =========================================================================
# 7. FILTROS GLOBAIS DE OPÇÕES
# =========================================================================

@router.get("/filters")
def get_filter_options():
    """Retorna listas únicas de categorias, canais e anos para popular os selects."""
    repo = get_repo()
    cats = repo.execute_sql("SELECT DISTINCT categoria FROM vendas WHERE categoria IS NOT NULL ORDER BY categoria;").iloc[:, 0].tolist()
    canais_vendas = repo.execute_sql("SELECT DISTINCT canal FROM vendas WHERE canal IS NOT NULL ORDER BY canal;").iloc[:, 0].tolist()
    canais_mkt = repo.execute_sql("SELECT DISTINCT canal FROM marketing WHERE canal IS NOT NULL ORDER BY canal;").iloc[:, 0].tolist()
    canais_sup = repo.execute_sql("SELECT DISTINCT canal_entrada FROM atendimento WHERE canal_entrada IS NOT NULL ORDER BY canal_entrada;").iloc[:, 0].tolist()
    segmentos_rfm = repo.execute_sql("SELECT DISTINCT segmento_rfm FROM clientes WHERE segmento_rfm IS NOT NULL ORDER BY segmento_rfm;").iloc[:, 0].tolist()

    return {
        "categories": cats,
        "sales_channels": canais_vendas,
        "marketing_channels": canais_mkt,
        "support_channels": canais_sup,
        "rfm_segments": segmentos_rfm,
        "years": ["Todos", "2023", "2024", "2025", "2026"]
    }
