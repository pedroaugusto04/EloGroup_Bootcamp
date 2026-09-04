"""
app/views/v_02_vendas_margem.py
Vendas & Margem: Análise detalhada de rentabilidade, descontos, custos e devoluções.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query
from app.components.cards import render_data_source_badge


def show_vendas_margem(repo: DuckDBRepository):
    st.markdown('<div class="page-title">Análise de Vendas & Rentabilidade</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Exploração detalhada de margem de contribuição, descontos concedidos, fretes e devoluções.</div>', unsafe_allow_html=True)

    render_data_source_badge(
        tables=["vendas"],
        scope="27.753 transações (Status Aprovado) | Jan/2023 a Jan/2024",
        dev_section="Seção 3: Observações por Tabela (Receita/Margem & Devoluções)"
    )

    # 1. Filtros Rápidos com Session Keys Estáveis
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        canais = repo.execute_sql("SELECT DISTINCT canal FROM vendas WHERE canal IS NOT NULL ORDER BY canal;").iloc[:, 0].tolist()
        canal_sel = st.multiselect(
            "Canais (vazio = todos):",
            options=canais,
            default=[],
            placeholder="Todos os canais selecionados",
            key="filtro_canal_vendas_margem"
        )
    with col_f2:
        categorias = repo.execute_sql("SELECT DISTINCT categoria FROM vendas WHERE categoria IS NOT NULL ORDER BY categoria;").iloc[:, 0].tolist()
        cat_sel = st.multiselect(
            "Categorias (vazio = todas):",
            options=categorias,
            default=[],
            placeholder="Todas as categorias selecionadas",
            key="filtro_cat_vendas_margem"
        )

    where_clauses = ["status_pagamento = 'Aprovado'"]
    if canal_sel:
        can_str = "', '".join(canal_sel)
        where_clauses.append(f"canal IN ('{can_str}')")
    if cat_sel:
        cat_str = "', '".join(cat_sel)
        where_clauses.append(f"categoria IN ('{cat_str}')")
    
    where_sql = f"WHERE {' AND '.join(where_clauses)}"

    # 2. Decomposição de Custos e Margem
    q_decomp = load_query("vendas/decomposicao_margem.sql", where_sql=where_sql)
    df_decomp = repo.execute_sql(q_decomp).iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Receita Bruta Total", f"R$ {df_decomp['bruta']/1e6:.2f}M")
    c2.metric("Descontos Concedidos", f"R$ {df_decomp['descontos']/1e6:.2f}M", f"-{(df_decomp['descontos']/df_decomp['bruta']*100 if df_decomp['bruta']>0 else 0):.1f}%")
    c3.metric("Custo de Produtos (CMV)", f"R$ {df_decomp['custo_prod']/1e6:.2f}M")
    c4.metric("Custo Total de Frete", f"R$ {df_decomp['custo_frete']/1e6:.2f}M")

    st.markdown("---")

    # 3. Gráficos de Rentabilidade
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Margem de Contribuição por Categoria")
        q_cat = load_query("vendas/margem_por_categoria.sql", where_sql=where_sql)
        df_cat_margem = repo.execute_sql(q_cat)
        
        fig_cat = px.bar(
            df_cat_margem,
            x="categoria",
            y=["receita", "margem"],
            barmode="group",
            labels={"value": "Valor (R$)", "categoria": "Categoria", "variable": "Indicador"}
        )
        fig_cat.update_layout(height=340, legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_g2:
        st.subheader("Motivos de Devolução (Impacto Financeiro)")
        q_dev = load_query("vendas/motivos_devolucao.sql")
        df_dev = repo.execute_sql(q_dev)
        
        fig_dev = px.pie(df_dev, names="motivo_devolucao", values="valor_devolvido", hole=0.4)
        fig_dev.update_layout(height=340)
        st.plotly_chart(fig_dev, use_container_width=True)

    # 4. Análise Granular por SKU
    st.subheader("Tabela de Produtos (SKU): Top Faturamento e Margem")
    q_skus = load_query("vendas/top_skus_faturamento.sql", where_sql=where_sql, limit=50)
    df_skus = repo.execute_sql(q_skus)
    
    st.dataframe(df_skus.style.format({
        "unidades_vendidas": "{:,.0f}",
        "receita_total": "R$ {:,.2f}",
        "margem_total": "R$ {:,.2f}",
        "margem_pct": "{:.1f}%",
        "desconto_medio_pct": "{:.1f}%"
    }), use_container_width=True)
