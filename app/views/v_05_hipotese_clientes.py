"""
app/views/v_05_hipotese_clientes.py
Tópico Dedicado — Hipótese 5: "O crescimento pode esconder diferenças importantes entre segmentos de clientes".
Alinhado estritamente com as observações e conclusões registradas em DEVELOPMENT.md.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query
from app.components.cards import render_data_source_badge


def show_hipotese_clientes(repo: DuckDBRepository):
    st.markdown('<div class="page-title">Hipótese 5: Segmentação & Concentração de Clientes</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle"><i>"O crescimento pode esconder diferenças importantes entre segmentos de clientes."</i></div>', unsafe_allow_html=True)

    render_data_source_badge(
        tables=["clientes"],
        scope="15.000 clientes cadastrados (LTV declarado no CRM) | Ano Base 2026",
        dev_section="Seção 5: Hipótese 5 (Segmentação RFM, Pareto & Churn)"
    )

    # 1. Métricas Chave
    q_rfm = load_query("hipotese_5_clientes/distribuicao_rfm_pareto.sql", where_sql="")
    df_rfm = repo.execute_sql(q_rfm)

    total_clientes = df_rfm["total_clientes"].sum()
    df_top = df_rfm[df_rfm["segmento"].isin(["Campeão", "Fiel"])]
    df_risco = df_rfm[df_rfm["segmento"].isin(["Em Risco", "Hibernando", "Churn"])]

    pct_top = (df_top["total_clientes"].sum() / total_clientes) * 100.0
    pct_risco = (df_risco["total_clientes"].sum() / total_clientes) * 100.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Base Total de Clientes", f"{total_clientes:,}")
    c2.metric("Campeões + Fiéis", f"{pct_top:.1f}% da base", help="Poucos clientes que representam grande parte do faturamento")
    c3.metric("Em Risco / Hibernando / Churn", f"{pct_risco:.1f}% da base", help="46,7% da base com risco de abandono")
    c4.metric("Ticket Médio Geral", "~ R$ 500,00", help="Praticamente constante em todos os grupos")

    st.markdown("---")

    # 3. Gráficos de Apoio
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Distribuição de Clientes por Segmento RFM")
        fig_rfm = px.bar(
            df_rfm,
            x="segmento",
            y="total_clientes",
            color="segmento",
            labels={"total_clientes": "Número de Clientes", "segmento": "Segmento RFM"},
            color_discrete_map={"Campeão": "#10B981", "Fiel": "#3B82F6", "Promissor": "#6366F1", "Em Risco": "#F59E0B", "Hibernando": "#EF4444", "Churn": "#78716C"}
        )
        fig_rfm.update_layout(height=340)
        st.plotly_chart(fig_rfm, use_container_width=True)

    with col_g2:
        st.subheader("Média de Pedidos por Segmento (Volume de Compras)")
        fig_ped = px.bar(
            df_rfm,
            x="segmento",
            y="media_pedidos",
            color="media_pedidos",
            labels={"media_pedidos": "Média de Pedidos no Histórico", "segmento": "Segmento RFM"},
            color_continuous_scale="Blues"
        )
        fig_ped.update_layout(height=340)
        st.plotly_chart(fig_ped, use_container_width=True)
