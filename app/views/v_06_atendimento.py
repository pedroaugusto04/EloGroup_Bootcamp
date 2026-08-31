"""
app/views/v_06_atendimento.py
Atendimento & Suporte: Chamados, canais de entrada, motivos de contato e CSAT.
"""

import streamlit as st
import plotly.express as px
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query


def show_atendimento(repo: DuckDBRepository):
    st.markdown('<div class="page-title">Atendimento & Suporte ao Cliente</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Volume de chamados, motivos de contato, satisfação (CSAT) e canais de suporte.</div>', unsafe_allow_html=True)

    # 1. Filtros
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        canais_at = repo.execute_sql("SELECT DISTINCT canal_entrada FROM atendimento WHERE canal_entrada IS NOT NULL ORDER BY canal_entrada;").iloc[:, 0].tolist()
        canal_sel = st.multiselect(
            "Filtrar Canais de Entrada (vazio = todos):",
            options=canais_at,
            default=[],
            placeholder="Todos os canais selecionados",
            key="filtro_canal_atendimento"
        )
    with col_f2:
        motivos_at = repo.execute_sql("SELECT DISTINCT categoria_problema FROM atendimento WHERE categoria_problema IS NOT NULL ORDER BY categoria_problema;").iloc[:, 0].tolist()
        motivo_sel = st.multiselect(
            "Filtrar Motivos (vazio = todos):",
            options=motivos_at,
            default=[],
            placeholder="Todos os motivos selecionados",
            key="filtro_motivo_atendimento"
        )

    where_clauses = []
    if canal_sel:
        can_str = "', '".join(canal_sel)
        where_clauses.append(f"canal_entrada IN ('{can_str}')")
    if motivo_sel:
        mot_str = "', '".join(motivo_sel)
        where_clauses.append(f"categoria_problema IN ('{mot_str}')")

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    # 2. Métricas Globais de Atendimento
    q_kpi = load_query("atendimento/kpis_atendimento.sql", where_sql=where_sql)
    df_at_kpi = repo.execute_sql(q_kpi).iloc[0]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total de Chamados", f"{int(df_at_kpi['total_tickets']):,}")
    c2.metric("CSAT Médio", f"{df_at_kpi['csat_medio']:.2f} / 5.0")
    c3.metric("Tempo Médio 1ª Resposta", f"{df_at_kpi['tempo_resposta_min']:.1f} min")
    c4.metric("Tempo Médio Resolução", f"{df_at_kpi['tempo_resolucao_h']:.1f} horas")
    c5.metric("Custo Total Suporte", f"R$ {df_at_kpi['custo_total']/1e3:,.1f}k")

    st.markdown("---")

    # 3. Gráficos de Motivos e CSAT
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Volume por Categoria de Problema")
        q_mot = load_query("atendimento/volume_motivos.sql", where_sql=where_sql)
        df_motivos = repo.execute_sql(q_mot)
        
        fig_mot = px.bar(
            df_motivos,
            x="categoria_problema",
            y="total_tickets",
            labels={"total_tickets": "Chamados", "categoria_problema": "Motivo / Categoria"},
            color="total_tickets",
            color_continuous_scale="Blues"
        )
        fig_mot.update_layout(height=340)
        st.plotly_chart(fig_mot, use_container_width=True)

    with col_g2:
        st.subheader("Distribuição de Notas CSAT (1 a 5)")
        q_csat = load_query("atendimento/distribuicao_csat.sql", where_sql=where_sql)
        df_csat = repo.execute_sql(q_csat)
        
        fig_csat = px.bar(
            df_csat,
            x="nota_csat",
            y="total_chamados",
            labels={"total_chamados": "Chamados", "nota_csat": "Nota CSAT"},
            color="nota_csat",
            color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"]
        )
        fig_csat.update_layout(height=340)
        st.plotly_chart(fig_csat, use_container_width=True)

    # 4. Canais de Entrada e Status
    col_g3, col_g4 = st.columns(2)
    with col_g3:
        st.subheader("Volume por Canal de Entrada")
        q_can = load_query("atendimento/canais_entrada.sql", where_sql=where_sql)
        df_canais_at = repo.execute_sql(q_can)
        
        fig_canais_at = px.pie(df_canais_at, names="canal_entrada", values="total_tickets", hole=0.4)
        fig_canais_at.update_layout(height=320)
        st.plotly_chart(fig_canais_at, use_container_width=True)

    with col_g4:
        st.subheader("Status dos Atendimentos")
        q_stat = load_query("atendimento/status_chamados.sql", where_sql=where_sql)
        df_status_at = repo.execute_sql(q_stat)
        
        fig_status_at = px.bar(df_status_at, x="status_atendimento", y="total_tickets", labels={"total_tickets": "Chamados", "status_atendimento": "Status"})
        fig_status_at.update_layout(height=320)
        st.plotly_chart(fig_status_at, use_container_width=True)

    # 5. Amostra de Mensagens Recentes de Clientes
    st.subheader("Amostra Recente de Chamados de Clientes")
    q_sample = load_query("atendimento/amostra_recentes.sql", where_sql=where_sql, limit=50)
    df_amostra = repo.execute_sql(q_sample)
    st.dataframe(df_amostra, use_container_width=True)
