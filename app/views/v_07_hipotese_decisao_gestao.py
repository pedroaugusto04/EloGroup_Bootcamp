"""
app/views/v_07_hipotese_decisao_gestao.py
Tópico Dedicado — Hipótese 6: "Parte da ineficiência pode estar na forma como a informação vira decisão".
Alinhado estritamente com as observações e conclusões registradas em DEVELOPMENT.md.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query
from app.components.cards import render_data_source_badge


def show_hipotese_decisao_gestao(repo: DuckDBRepository):
    st.markdown('<div class="page-title">Hipótese 6: Informação para Decisão & Estoque</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle"><i>"Parte da ineficiência pode estar na forma como a informação vira decisão."</i></div>', unsafe_allow_html=True)

    render_data_source_badge(
        tables=["estoque"],
        scope="5.000 SKUs (207 descontinuados e 701 em nível crítico) | Snapshot Jan/2026",
        dev_section="Seção 5: Hipótese 6 (Capital Imobilizado vs Ruptura)"
    )

    # 1. Métricas Chave do Estoque
    q_est = load_query("hipotese_6_decisao_gestao/descompasso_estoque_ruptura.sql")
    df_est = repo.execute_sql(q_est)

    df_desc = df_est[df_est["status_disponibilidade"] == "Descontinuado"]
    df_crit = df_est[df_est["status_disponibilidade"] == "Estoque Crítico"]

    if df_est.empty:
        st.info("Não há dados de estoque disponíveis para esta análise.")
        return

    cap_travado = df_desc["capital_travado_descontinuado"].sum()
    skus_desc = df_desc["total_skus"].sum()
    cap_risco = df_crit["capital_em_risco_ruptura"].sum()
    skus_crit = df_crit["total_skus"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Capital Parado em Descontinuados", f"R$ {cap_travado/1e6:.1f}M", help="Mais de R$ 14,7M imobilizados")
    c2.metric("SKUs Fora de Linha", f"{int(skus_desc)} SKUs", help="Produtos sem ação rápida de liquidação")
    c3.metric("Capital em Estoque Crítico", f"R$ {cap_risco/1e6:.1f}M", help="Valor atualmente imobilizado nos 701 SKUs abaixo do ponto de pedido; não representa perda de receita")
    c4.metric("SKUs Abaixo do Ponto de Pedido", f"{int(skus_crit)} SKUs", help="Produtos abaixo do ponto de pedido; demanda e receita perdida não foram estimadas")

    st.markdown("---")

    # 3. Gráficos de Apoio do Descompasso
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Capital em Estoque por Situação")
        fig_cap = px.bar(
            df_est,
            x="status_disponibilidade",
            y="capital_total_estoque",
            color="status_disponibilidade",
            labels={"capital_total_estoque": "Capital Total (R$)", "status_disponibilidade": "Status do SKU"},
            title="Capital Travado vs Em Estoque (R$)"
        )
        fig_cap.update_layout(height=340)
        st.plotly_chart(fig_cap, use_container_width=True)

    with col_g2:
        st.subheader("Participação de SKUs por Status")
        fig_skus = px.pie(df_est, names="status_disponibilidade", values="total_skus", hole=0.4)
        fig_skus.update_layout(height=340)
        st.plotly_chart(fig_skus, use_container_width=True)
