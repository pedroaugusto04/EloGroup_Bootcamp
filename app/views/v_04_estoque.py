"""
app/views/v_04_estoque.py
Estoque & Operações: Níveis de disponibilidade, rupturas, lead times e capital imobilizado.
"""

import streamlit as st
import plotly.express as px
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query
from app.components.cards import render_data_source_badge


def show_estoque(repo: DuckDBRepository):
    st.markdown('<div class="page-title">Gestão de Estoque & Operações</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Acompanhamento de rupturas, pontos de pedido, lead times de fornecedores e estoque imobilizado.</div>', unsafe_allow_html=True)

    render_data_source_badge(
        tables=["estoque"],
        scope="5.000 SKUs cadastrados (WMS) | Snapshot Jan/2026",
        dev_section="Seção 3: Observações por Tabela (Estoque & Rupturas)"
    )

    # 1. Filtro
    categorias = repo.execute_sql("SELECT DISTINCT categoria FROM estoque WHERE categoria IS NOT NULL ORDER BY categoria;").iloc[:, 0].tolist()
    cat_sel = st.multiselect(
        "Filtrar Categorias (vazio = todas):",
        options=categorias,
        default=[],
        placeholder="Todas as categorias selecionadas",
        key="filtro_cat_estoque"
    )

    if cat_sel:
        cat_str = "', '".join(cat_sel)
        where_sql = f"WHERE categoria IN ('{cat_str}')"
        crit_where = f"WHERE (em_ruptura = true OR is_estoque_critico = true) AND categoria IN ('{cat_str}')"
    else:
        where_sql = ""
        crit_where = "WHERE em_ruptura = true OR is_estoque_critico = true"

    # 2. Métricas Globais de Estoque
    q_kpi = load_query("estoque/kpis_estoque.sql", where_sql=where_sql)
    df_est_kpi = repo.execute_sql(q_kpi).iloc[0]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total de SKUs", f"{int(df_est_kpi['total_skus']):,}")
    c2.metric("SKUs em Ruptura", f"{int(df_est_kpi['skus_ruptura'])}", f"{df_est_kpi['taxa_ruptura']:.1f}% catálogo")
    c3.metric("Taxa de Ruptura", f"{df_est_kpi['taxa_ruptura']:.1f}%")
    c4.metric("Capital em Estoque", f"R$ {df_est_kpi['capital_parado']/1e6:.2f}M")
    c5.metric("Lead Time Médio", f"{df_est_kpi['lead_time_medio']:.0f} dias")

    st.markdown("---")

    # 3. Gráficos de Estoque
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("SKUs com Necessidade de Reposição por Categoria")
        q_cat = load_query("estoque/ruptura_por_categoria.sql", where_sql=where_sql)
        df_cat_est = repo.execute_sql(q_cat)
        
        df_plot_rep = df_cat_est.melt(
            id_vars=["categoria"],
            value_vars=["skus_ruptura", "skus_estoque_critico"],
            var_name="Tipo_Risco",
            value_name="Qtd_SKUs"
        )
        df_plot_rep["Tipo_Risco"] = df_plot_rep["Tipo_Risco"].map({
            "skus_ruptura": "Ruptura Real (Estoque = 0)",
            "skus_estoque_critico": "Estoque Crítico (<= Ponto de Pedido)"
        })
        
        fig_cat = px.bar(
            df_plot_rep,
            x="categoria",
            y="Qtd_SKUs",
            color="Tipo_Risco",
            barmode="stack",
            labels={"Qtd_SKUs": "Total de SKUs", "categoria": "Categoria", "Tipo_Risco": "Severidade"},
            color_discrete_map={
                "Ruptura Real (Estoque = 0)": "#EF4444",
                "Estoque Crítico (<= Ponto de Pedido)": "#F59E0B"
            }
        )
        fig_cat.update_layout(height=340, legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig_cat, width="stretch")

    with col_g2:
        st.subheader("Lead Time Médio por Categoria (Dias)")
        fig_lt = px.bar(
            df_cat_est,
            x="categoria",
            y="lead_time_medio",
            labels={"lead_time_medio": "Lead Time Médio (Dias)", "categoria": "Categoria"}
        )
        fig_lt.update_layout(height=340)
        st.plotly_chart(fig_lt, width="stretch")

    # 4. Tabela de SKUs Críticos (Abaixo do Ponto de Pedido)
    st.subheader("SKUs em Ruptura ou Estoque Crítico")
    q_crit = load_query("estoque/skus_criticos.sql", crit_where=crit_where, limit=50)
    df_criticos = repo.execute_sql(q_crit)
    
    st.dataframe(df_criticos.style.format({
        "estoque_disponivel": "{:,.0f}",
        "ponto_pedido": "{:,.0f}",
        "deficit_unidades": "{:,.0f}",
        "lead_time_dias": "{:.0f}",
        "custo_unitario": "R$ {:,.2f}",
        "preco_venda_sugerido": "R$ {:,.2f}"
    }), width="stretch")
