"""
app/views/v_05_clientes.py
Base de Clientes: Segmentação RFM, LTV, frequência de compras, perfil demográfico
e Qualidade dos Canais de Aquisição (Hipótese 2).
"""

import streamlit as st
import plotly.express as px
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query
from app.components.cards import render_data_source_badge


def show_clientes(repo: DuckDBRepository):
    st.markdown('<div class="page-title">Base de Clientes & Perfil Cadastral</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Perfil demográfico, distribuição por estado, frequência de compra e LTV da base de CRM.</div>', unsafe_allow_html=True)

    render_data_source_badge(
        tables=["clientes"],
        scope="15.000 clientes cadastrados (CRM) | Ano Base 2026",
        dev_section="Seção 3: Observações por Tabela (Base de Clientes)"
    )

    # 1. Filtro por Segmento
    segmentos = repo.execute_sql("SELECT DISTINCT segmento_rfm FROM clientes WHERE segmento_rfm IS NOT NULL ORDER BY segmento_rfm;").iloc[:, 0].tolist()
    seg_sel = st.multiselect(
        "Filtrar Segmentos RFM (vazio = todos):",
        options=segmentos,
        default=[],
        placeholder="Todos os segmentos selecionados",
        key="filtro_seg_clientes"
    )

    if seg_sel:
        seg_str = "', '".join(seg_sel)
        where_sql = f"WHERE segmento_rfm IN ('{seg_str}')"
        uf_where = f"WHERE segmento_rfm IN ('{seg_str}') AND estado IS NOT NULL"
    else:
        where_sql = ""
        uf_where = "WHERE estado IS NOT NULL"

    # 2. Métricas da Base de Clientes
    q_kpi = load_query("clientes/kpis_clientes.sql", where_sql=where_sql)
    df_cli_kpi = repo.execute_sql(q_kpi).iloc[0]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total de Clientes", f"{int(df_cli_kpi['total_clientes']):,}")
    c2.metric("LTV Médio", f"R$ {df_cli_kpi['ltv_medio']:.2f}")
    c3.metric("Frequência Média", f"{df_cli_kpi['frequencia_media']:.1f} pedidos")
    c4.metric("Renda Média", f"R$ {df_cli_kpi['renda_media']:.2f}")
    c5.metric("Idade Média", f"{df_cli_kpi['idade_media']:.0f} anos")

    st.markdown("---")

    # 3. Segmentos RFM
    q_rfm = load_query("clientes/segmentos_rfm.sql", where_sql=where_sql)
    df_rfm = repo.execute_sql(q_rfm)

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Distribuição de Clientes por Segmento RFM")
        fig_rfm = px.bar(
            df_rfm,
            x="segmento",
            y="total_clientes",
            labels={"total_clientes": "Clientes", "segmento": "Segmento RFM"},
            color="total_clientes",
            color_continuous_scale="Blues"
        )
        fig_rfm.update_layout(height=340)
        st.plotly_chart(fig_rfm, width="stretch")

    with col_g2:
        st.subheader("LTV Médio por Segmento (R$)")
        fig_ltv = px.bar(
            df_rfm,
            x="segmento",
            y="ltv_medio",
            labels={"ltv_medio": "LTV Médio (R$)", "segmento": "Segmento RFM"},
            color="ltv_medio",
            color_continuous_scale="Greens"
        )
        fig_ltv.update_layout(height=340)
        st.plotly_chart(fig_ltv, width="stretch")

    # 4. Demografia e Dispositivos
    col_g3, col_g4 = st.columns(2)
    with col_g3:
        st.subheader("Top 10 Estados por Volume de Clientes")
        q_uf = load_query("clientes/top_estados.sql", uf_where=uf_where, limit=10)
        df_uf = repo.execute_sql(q_uf)
        
        fig_uf = px.bar(df_uf, x="estado", y="total_clientes", labels={"total_clientes": "Clientes", "estado": "UF"})
        fig_uf.update_layout(height=320)
        st.plotly_chart(fig_uf, width="stretch")

    with col_g4:
        st.subheader("Clientes por Nível de Fidelidade")
        q_fid = load_query("clientes/nivel_fidelidade.sql", where_sql=where_sql)
        df_fid = repo.execute_sql(q_fid)
        
        fig_fid = px.pie(df_fid, names="nivel_fidelidade", values="total_clientes", hole=0.4)
        fig_fid.update_layout(height=320)
        st.plotly_chart(fig_fid, width="stretch")

    # 5. Tabela Resumo dos Segmentos RFM
    st.subheader("Tabela Consolidada de Segmentos RFM")
    st.dataframe(df_rfm.style.format({
        "total_clientes": "{:,.0f}",
        "pct_base": "{:.1f}%",
        "ltv_total": "R$ {:,.2f}",
        "ltv_medio": "R$ {:,.2f}",
        "media_pedidos": "{:.1f}",
        "renda_media": "R$ {:,.2f}"
    }), width="stretch")
