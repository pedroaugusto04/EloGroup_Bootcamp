"""
app/views/v_03_marketing.py
Marketing & Mídia: Eficiência de canais, ROAS, CAC, CTR e conversões.
"""

import streamlit as st
import plotly.express as px
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query


def show_marketing(repo: DuckDBRepository):
    st.markdown('<div class="page-title">Desempenho de Marketing & Mídia</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Análise de retorno sobre investimento (ROAS), custo de aquisição (CAC), cliques e conversões por canal.</div>', unsafe_allow_html=True)

    # 1. Filtro
    canais = repo.execute_sql("SELECT DISTINCT canal FROM marketing WHERE canal IS NOT NULL ORDER BY canal;").iloc[:, 0].tolist()
    canal_sel = st.multiselect(
        "Filtrar Canais de Mídia (vazio = todos):",
        options=canais,
        default=[],
        placeholder="Todos os canais selecionados",
        key="filtro_canal_marketing"
    )

    if canal_sel:
        can_str = "', '".join(canal_sel)
        where_sql = f"WHERE canal IN ('{can_str}')"
    else:
        where_sql = ""

    # 2. Métricas Globais
    q_kpi = load_query("marketing/kpis_marketing.sql", where_sql=where_sql)
    df_mkt_kpi = repo.execute_sql(q_kpi).iloc[0]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Investimento Total", f"R$ {df_mkt_kpi['invest_total']/1e6:.2f}M")
    c2.metric("Receita Gerada (Mkt)", f"R$ {df_mkt_kpi['rec_total']/1e6:.2f}M")
    c3.metric("ROAS Global", f"{df_mkt_kpi['roas_global']:.2f}x")
    c4.metric("CAC Médio", f"R$ {df_mkt_kpi['cac_medio']:.2f}")
    c5.metric("Total de Conversões", f"{int(df_mkt_kpi['conv_total']):,}")

    st.markdown("---")

    # 3. Desempenho por Canal
    q_canal = load_query("marketing/eficiencia_canais.sql", where_sql=where_sql)
    df_canal_mkt = repo.execute_sql(q_canal)

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Investimento vs. Receita por Canal")
        fig_bar = px.bar(
            df_canal_mkt,
            x="canal",
            y=["investimento", "receita_gerada"],
            barmode="group",
            labels={"value": "Valor (R$)", "canal": "Canal", "variable": "Métrica"}
        )
        fig_bar.update_layout(height=340, legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2:
        st.subheader("Dispersão: CAC vs. ROAS por Canal")
        fig_scatter = px.scatter(
            df_canal_mkt,
            x="cac",
            y="roas",
            size="investimento",
            color="canal",
            text="canal",
            labels={"cac": "CAC (R$)", "roas": "ROAS (x)"}
        )
        fig_scatter.update_traces(textposition="top center")
        fig_scatter.update_layout(height=340)
        st.plotly_chart(fig_scatter, use_container_width=True)

    # 4. Tabela Completa de Eficiência por Canal
    st.subheader("Matriz de Eficiência por Canal")
    st.dataframe(df_canal_mkt.style.format({
        "investimento": "R$ {:,.2f}",
        "receita_gerada": "R$ {:,.2f}",
        "conversoes": "{:,.0f}",
        "cliques": "{:,.0f}",
        "impressoes": "{:,.0f}",
        "roas": "{:.2f}x",
        "cac": "R$ {:,.2f}",
        "ctr_pct": "{:.2f}%",
        "taxa_conversao_pct": "{:.2f}%"
    }), use_container_width=True)
