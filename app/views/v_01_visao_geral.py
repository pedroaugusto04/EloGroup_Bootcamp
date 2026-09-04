"""
app/views/v_01_visao_geral.py
Visão Geral: KPIs consolidados, evolução temporal e desempenho macro por canal e categoria.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query
from app.components.cards import render_data_source_badge


def show_visao_geral(repo: DuckDBRepository):
    st.markdown('<div class="page-title">Visão Geral & Métricas Consolidadas</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Panorama agregado de vendas, margem, canais e categorias para análise exploratória.</div>', unsafe_allow_html=True)

    render_data_source_badge(
        tables=["vendas"],
        scope="27.753 transações (ERP) | Jan/2023 a 26/Jan/2024",
        dev_section="Seção 3: Observações por Tabela (Receita/Margem)"
    )

    # 1. Filtros Rápidos com Session Keys Estáveis
    col_f1, col_f2, col_f3 = st.columns([2, 3, 2])
    with col_f1:
        status_opts = ["Aprovado", "Todos", "Aguardando", "Cancelado"]
        status_sel = st.selectbox("Status de Pagamento:", status_opts, index=0, key="filtro_status_visao_geral")
    with col_f2:
        df_cats = repo.execute_sql("SELECT DISTINCT categoria FROM vendas WHERE categoria IS NOT NULL ORDER BY categoria;").iloc[:, 0].tolist()
        cat_sel = st.multiselect(
            "Categorias (vazio = todas):",
            options=df_cats,
            default=[],
            placeholder="Todas as categorias selecionadas",
            key="filtro_cat_visao_geral"
        )
    with col_f3:
        anos = ["Todos", "2023", "2024", "2025", "2026"]
        ano_sel = st.selectbox("Ano do Pedido:", anos, index=0, key="filtro_ano_visao_geral")

    where_clauses = []
    if status_sel != "Todos":
        where_clauses.append(f"status_pagamento = '{status_sel}'")
    if cat_sel:
        cats_str = "', '".join(cat_sel)
        where_clauses.append(f"categoria IN ('{cats_str}')")
    if ano_sel != "Todos":
        where_clauses.append(f"ano = {ano_sel}")
    
    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    # 2. Métricas Consolidadas
    q_kpi = load_query("visao_geral/kpis_consolidados.sql", where_sql=where_sql)
    df_kpi = repo.execute_sql(q_kpi).iloc[0]
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Receita Líquida", f"R$ {df_kpi['liquida']/1e6:.2f}M")
    c2.metric("Margem Contribuição", f"R$ {df_kpi['margem']/1e6:.2f}M", f"{(df_kpi['margem']/df_kpi['liquida']*100 if df_kpi['liquida']>0 else 0):.1f}%")
    c3.metric("Total de Pedidos", f"{int(df_kpi['total_pedidos']):,}")
    c4.metric("Ticket Médio", f"R$ {df_kpi['ticket_medio']:.2f}")
    c5.metric("Taxa Devolução", f"{df_kpi['taxa_devolucao']:.1f}%")

    st.markdown("---")

    # 3. Gráficos Analíticos
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Evolução Mensal (Receita vs. Margem)")
        q_trend = load_query("visao_geral/evolucao_mensal.sql", where_sql=where_sql)
        df_mensal = repo.execute_sql(q_trend)
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=df_mensal["ano_mes"], y=df_mensal["receita_liquida"],
            name="Receita Líquida", mode="lines+markers", line=dict(width=2.5, color="#38BDF8")
        ))
        fig_trend.add_trace(go.Bar(
            x=df_mensal["ano_mes"], y=df_mensal["margem_contribuicao"],
            name="Margem Contribuição", marker_color="#94A3B8", opacity=0.7
        ))
        fig_trend.update_layout(height=340, hovermode="x unified", legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_g2:
        st.subheader("Receita Líquida por Canal de Venda")
        q_canal = load_query("visao_geral/receita_por_canal.sql", where_sql=where_sql)
        df_canal = repo.execute_sql(q_canal)
        
        fig_canal = px.bar(
            df_canal,
            x="canal",
            y=["receita_liquida", "margem_contribuicao"],
            barmode="group",
            labels={"value": "Valor (R$)", "canal": "Canal", "variable": "Métrica"},
            color_discrete_map={"receita_liquida": "#38BDF8", "margem_contribuicao": "#94A3B8"}
        )
        fig_canal.update_layout(height=340, legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig_canal, use_container_width=True)

    # 4. Distribuição por Categoria e Métodos de Pagamento
    col_g3, col_g4 = st.columns(2)
    with col_g3:
        st.subheader("Mix de Receita por Categoria")
        q_cat = load_query("visao_geral/mix_categoria.sql", where_sql=where_sql)
        df_cat = repo.execute_sql(q_cat)
        
        fig_cat = px.pie(df_cat, names="categoria", values="receita_liquida", hole=0.4)
        fig_cat.update_layout(height=320)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_g4:
        st.subheader("Volume por Método de Pagamento")
        q_pag = load_query("visao_geral/metodos_pagamento.sql", where_sql=where_sql)
        df_pag = repo.execute_sql(q_pag)
        
        fig_pag = px.bar(
            df_pag,
            x="metodo_pagamento",
            y="total_pedidos",
            labels={"total_pedidos": "Pedidos", "metodo_pagamento": "Método de Pagamento"},
            color="total_pedidos",
            color_continuous_scale="Blues"
        )
        fig_pag.update_layout(height=320)
        st.plotly_chart(fig_pag, use_container_width=True)

    # 5. Tabela Resumo Agregada
    st.subheader("Tabela Resumo: Desempenho Mensal Consolidado")
    st.dataframe(df_mensal.style.format({
        "receita_liquida": "R$ {:,.2f}",
        "margem_contribuicao": "R$ {:,.2f}",
        "pedidos": "{:,.0f}"
    }), use_container_width=True)
