"""
app/views/v_05_clientes.py
Base de Clientes: Segmentação RFM, LTV, frequência de compras, perfil demográfico
e Qualidade dos Canais de Aquisição (Hipótese 2).
"""

import streamlit as st
import plotly.express as px
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query


def show_clientes(repo: DuckDBRepository):
    st.markdown('<div class="page-title">Base de Clientes & Segmentação RFM</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Diagnóstico da Hipótese 2: Concentração de LTV, risco de churn e qualidade por canal de aquisição.</div>', unsafe_allow_html=True)

    # Diagnóstico da Hipótese 2
    st.info(
        """
        💡 **Diagnóstico da Hipótese 2 (O crescimento esconde diferenças entre segmentos):**
        Os segmentos **Campeões** e **Fiéis** (25,9% da base) concentram a vasta maioria do faturamento recorrente.
        No entanto, **46,7% da base total** encontra-se em risco (`Em Risco`, `Hibernando` ou `Churn`), evidenciando que 
        o crescimento por aquisição desordenada atrai clientes de baixa retenção.
        """
    )

    tab1, tab2 = st.tabs(["📊 Segmentação RFM & Perfil", "🎯 Qualidade por Canal de Aquisição"])

    with tab1:
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
            st.plotly_chart(fig_rfm, use_container_width=True)

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
            st.plotly_chart(fig_ltv, use_container_width=True)

        # 4. Demografia e Dispositivos
        col_g3, col_g4 = st.columns(2)
        with col_g3:
            st.subheader("Top 10 Estados por Volume de Clientes")
            q_uf = load_query("clientes/top_estados.sql", uf_where=uf_where, limit=10)
            df_uf = repo.execute_sql(q_uf)
            
            fig_uf = px.bar(df_uf, x="estado", y="total_clientes", labels={"total_clientes": "Clientes", "estado": "UF"})
            fig_uf.update_layout(height=320)
            st.plotly_chart(fig_uf, use_container_width=True)

        with col_g4:
            st.subheader("Clientes por Nível de Fidelidade")
            q_fid = load_query("clientes/nivel_fidelidade.sql", where_sql=where_sql)
            df_fid = repo.execute_sql(q_fid)
            
            fig_fid = px.pie(df_fid, names="nivel_fidelidade", values="total_clientes", hole=0.4)
            fig_fid.update_layout(height=320)
            st.plotly_chart(fig_fid, use_container_width=True)

        # 5. Tabela Resumo dos Segmentos RFM
        st.subheader("Tabela Consolidada de Segmentos RFM")
        st.dataframe(df_rfm.style.format({
            "total_clientes": "{:,.0f}",
            "pct_base": "{:.1f}%",
            "ltv_total": "R$ {:,.2f}",
            "ltv_medio": "R$ {:,.2f}",
            "media_pedidos": "{:.1f}",
            "renda_media": "R$ {:,.2f}"
        }), use_container_width=True)

    with tab2:
        st.subheader("Qualidade e Retenção do Cliente por Canal de Aquisição")
        st.markdown(
            "Cruzamento entre o **canal da primeira compra** e o valor gerado ao longo da vida do cliente (LTV, CAC e taxa de clientes de alto valor vs risco de churn)."
        )

        q_canal = load_query("clientes/qualidade_canal_aquisicao.sql", where_sql="")
        df_canal = repo.execute_sql(q_canal)

        c_col1, c_col2 = st.columns(2)
        with c_col1:
            fig_canal_ltv = px.bar(
                df_canal,
                x="canal_aquisicao",
                y="ltv_medio",
                color="pct_alto_valor",
                labels={"ltv_medio": "LTV Médio (R$)", "canal_aquisicao": "Canal de Aquisição", "pct_alto_valor": "% Alto Valor (Campeões/Fiéis)"},
                title="LTV Médio vs % Clientes de Alto Valor por Canal",
                color_continuous_scale="Viridis"
            )
            fig_canal_ltv.update_layout(height=340)
            st.plotly_chart(fig_canal_ltv, use_container_width=True)

        with c_col2:
            fig_churn = px.bar(
                df_canal,
                x="canal_aquisicao",
                y="pct_risco_churn",
                labels={"pct_risco_churn": "% Em Risco / Churn", "canal_aquisicao": "Canal de Aquisição"},
                title="% de Clientes em Risco de Churn por Canal",
                color="pct_risco_churn",
                color_continuous_scale="Reds"
            )
            fig_churn.update_layout(height=340)
            st.plotly_chart(fig_churn, use_container_width=True)

        st.dataframe(
            df_canal.style.format({
                "total_clientes": "{:,.0f}",
                "pct_base_amostral": "{:.1f}%",
                "ltv_medio": "R$ {:,.2f}",
                "ltv_total": "R$ {:,.2f}",
                "media_pedidos": "{:.1f}",
                "cac_estimado": "R$ {:.2f}",
                "ltv_cac_ratio": "{:.1f}x",
                "clientes_alto_valor": "{:,.0f}",
                "pct_alto_valor": "{:.1f}%",
                "clientes_risco_churn": "{:,.0f}",
                "pct_risco_churn": "{:.1f}%"
            }),
            use_container_width=True
        )
