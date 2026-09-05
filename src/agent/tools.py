"""
src/agent/tools.py
Ferramentas determinísticas executadas no DuckDB para o Agente de Estoque.
As consultas SQL estão centralizadas e documentadas em `src/queries/agent/*.sql` e são carregadas via `load_query`.
"""

import json
from typing import Optional, Dict, Any, List
import pandas as pd
from langchain_core.tools import tool

from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query


def _get_repo() -> DuckDBRepository:
    return DuckDBRepository()


@tool
def tool_inventory_health_scan(categoria: Optional[str] = None, limit: int = 25) -> str:
    """
    Audita a saúde do estoque identificando rupturas ativas e SKUs em risco iminente de falta.
    Calcula velocidade diária de vendas (unidades/dia) e dias de cobertura física.
    
    Args:
        categoria: Categoria opcional para filtrar (ex: 'Beleza', 'Moda', 'Lifestyle', 'Decoração', 'Esportes').
        limit: Número máximo de registros retornados.
    """
    repo = _get_repo()
    cat_filter = f"WHERE e.categoria = '{categoria}'" if categoria else ""
    query = load_query(
        "agent/inventory_health_scan.sql",
        cat_filter=cat_filter,
        limit=limit
    )
    df = repo.execute_sql(query)
    return json.dumps(df.to_dict(orient="records"), ensure_ascii=False, indent=2)


@tool
def tool_sales_demand_matrix(categoria: Optional[str] = None, top_n: int = 20) -> str:
    """
    Gera a matriz de demanda e faturamento real de vendas, trazendo a Curva de Volume vs Receita Real.
    Permite identificar quais são os produtos mais vendidos em unidades e quais geram mais margem.
    
    Args:
        categoria: Categoria opcional para filtrar.
        top_n: Quantidade de top produtos a retornar.
    """
    repo = _get_repo()
    cat_filter = f"AND v.categoria = '{categoria}'" if categoria else ""
    query = load_query(
        "agent/sales_demand_matrix.sql",
        cat_filter=cat_filter,
        top_n=top_n
    )
    df = repo.execute_sql(query)
    return json.dumps(df.to_dict(orient="records"), ensure_ascii=False, indent=2)


@tool
def tool_marketing_stock_mismatch() -> str:
    """
    Identifica o descompasso entre campanhas de marketing pagas e a disponibilidade de estoque.
    Detecta categorias com alta taxa de ruptura onde marketing continua investindo e gerando tráfego.
    """
    repo = _get_repo()
    query = load_query("agent/marketing_stock_mismatch.sql")
    df = repo.execute_sql(query)
    return json.dumps(df.to_dict(orient="records"), ensure_ascii=False, indent=2)


@tool
def tool_returns_and_quality_risk(min_orders: int = 10, min_returns: int = 2) -> str:
    """
    Cruza dados de devoluções com produtos e motivos de atrito para diagnosticar problemas de qualidade.
    Evita repor ou manter em estoque produtos com alta taxa de devolução e rejeição.
    """
    repo = _get_repo()
    query = load_query(
        "agent/returns_and_quality_risk.sql",
        min_orders=min_orders,
        min_returns=min_returns
    )
    df = repo.execute_sql(query)
    return json.dumps(df.to_dict(orient="records"), ensure_ascii=False, indent=2)


@tool
def tool_discontinued_stranded_capital(limit: int = 20) -> str:
    """
    Identifica SKUs descontinuados com capital de giro parado no galpão.
    Calcula o capital travado utilizando o custo médio realizado real da base de vendas.
    """
    repo = _get_repo()
    query = load_query(
        "agent/discontinued_stranded_capital.sql",
        limit=limit
    )
    df = repo.execute_sql(query)
    return json.dumps(df.to_dict(orient="records"), ensure_ascii=False, indent=2)


@tool
def tool_sku_deep_dive(sku_id: str) -> str:
    """
    Realiza uma investigação detalhada 360° em um SKU específico:
    posição de estoque, histórico de vendas, margem unitária real, lead time e taxa de devolução.
    
    Args:
        sku_id: O identificador único do SKU (ex: 'SKU-00185').
    """
    repo = _get_repo()
    query = load_query(
        "agent/sku_deep_dive.sql",
        sku_id=sku_id
    )
    df = repo.execute_sql(query)
    if df.empty:
        return json.dumps({"error": f"SKU {sku_id} não encontrado na base de dados."})
    return json.dumps(df.to_dict(orient="records")[0], ensure_ascii=False, indent=2)


@tool
def tool_simulate_inventory_liquidation(categoria: Optional[str] = None, desconto_pct: float = 30.0) -> str:
    """
    Simula o impacto financeiro de uma campanha de liquidação (clearance) de itens descontinuados.
    Calcula a liberação imediata de capital de giro (caixa gerado) e o impacto na margem.
    
    Args:
        categoria: Categoria opcional para simular (ex: 'Moda', 'Beleza', 'Lifestyle', 'Decoração', 'Esportes').
        desconto_pct: Percentual de desconto a ser aplicado (ex: 20.0, 30.0, 50.0).
    """
    repo = _get_repo()
    cat_filter = f"AND e.categoria = '{categoria}'" if categoria else ""
    discount_factor = (100.0 - float(desconto_pct)) / 100.0
    
    query = load_query(
        "agent/simulate_inventory_liquidation.sql",
        discount_factor=discount_factor,
        cat_filter=cat_filter
    )
    df = repo.execute_sql(query)
    if df.empty:
        return json.dumps({
            "categoria": categoria or "Todas",
            "desconto_pct": desconto_pct,
            "total_skus": 0,
            "total_unidades": 0,
            "capital_imobilizado_custo": 0.0,
            "caixa_destravado_projetado": 0.0,
            "margem_contribuicao_projetada": 0.0,
            "skus": []
        }, ensure_ascii=False, indent=2)
        
    summary = {
        "categoria": categoria or "Todas",
        "desconto_aplicado_pct": desconto_pct,
        "total_skus_descontinuados": len(df),
        "total_unidades_liquidacao": int(df["estoque_disponivel"].sum()),
        "capital_imobilizado_custo_total": round(float(df["capital_travado_custo"].sum()), 2),
        "caixa_destravado_projetado_total": round(float(df["receita_caixa_projetada"].sum()), 2),
        "margem_contribuicao_projetada_total": round(float(df["margem_contribuicao_projetada"].sum()), 2),
        "top_5_skus_impactados": df.head(5).to_dict(orient="records")
    }
    return json.dumps(summary, ensure_ascii=False, indent=2)


