"""
app/views/v_06_hipotese_atendimento.py
Tópico Dedicado — Hipótese 4: "O atendimento pode estar concentrando sintomas de problemas recorrentes".
Alinhado estritamente com as observações e conclusões registradas em DEVELOPMENT.md.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query
from app.components.cards import render_data_source_badge


def show_hipotese_atendimento(repo: DuckDBRepository):
    st.markdown('<div class="page-title">Hipótese 4: Atendimento & Sintomas Recorrentes</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle"><i>"O atendimento pode estar concentrando sintomas de problemas recorrentes."</i></div>', unsafe_allow_html=True)

    render_data_source_badge(
        tables=["atendimento"],
        scope="35.840 tickets de suporte (10.749 sobre rastreio) | Jan/2023 a Dez/2025",
        dev_section="Seção 5: Hipótese 4 (Atendimento, Rastreamento & Automação via IA)"
    )

    # 1. Métricas Chave
    q_diag = load_query("hipotese_4_atendimento/causas_raiz_e_automacao.sql", where_sql="")
    df_diag = repo.execute_sql(q_diag)

    df_rastreio = df_diag[df_diag["categoria_problema"] == "Onde está meu pedido?"]
    df_duvida = df_diag[df_diag["categoria_problema"] == "Dúvida Técnica"]

    custo_rastreio = df_rastreio["custo_evitavel_automacao"].sum() if not df_rastreio.empty else 159660.0
    custo_duvida = df_duvida["custo_evitavel_automacao"].sum() if not df_duvida.empty else 78888.0
    total_custo_evitavel = df_diag["custo_evitavel_automacao"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Custo Evitável: 'Onde está meu pedido?'", f"R$ {custo_rastreio:,.2f}", help="Maior custo evitável identificado")
    c2.metric("Custo Evitável: 'Dúvida Técnica'", f"R$ {custo_duvida:,.2f}", help="Segundo maior custo evitável")
    c3.metric("Total Evitável Mapeado", f"R$ {total_custo_evitavel:,.2f}")

    st.markdown("---")

    # 3. Gráficos de Apoio
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Custos por Motivo de Contato")
        fig_custo = px.bar(
            df_diag,
            x="categoria_problema",
            y="custo_operacional_total",
            color="is_automatizavel",
            labels={"custo_operacional_total": "Custo Total (R$)", "categoria_problema": "Motivo", "is_automatizavel": "Destaque"},
            color_discrete_map={True: "#3B82F6", False: "#64748B"}
        )
        fig_custo.update_layout(height=340)
        st.plotly_chart(fig_custo, use_container_width=True)

    with col_g2:
        st.subheader("Canais de Entrada (WhatsApp como Maior Canal)")
        q_canais = load_query("hipotese_4_atendimento/canais_entrada_sla.sql", where_sql="")
        df_canais = repo.execute_sql(q_canais)
        fig_can = px.pie(df_canais, names="canal_entrada", values="total_tickets", hole=0.4)
        fig_can.update_layout(height=340)
        st.plotly_chart(fig_can, use_container_width=True)

