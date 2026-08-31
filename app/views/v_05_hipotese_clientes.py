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


def show_hipotese_clientes(repo: DuckDBRepository):
    st.markdown('<div class="page-title">📌 Hipótese 5: Segmentação & Concentração de Clientes</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle"><i>"O crescimento pode esconder diferenças importantes entre segmentos de clientes."</i></div>', unsafe_allow_html=True)

    # 1. Resumo conforme DEVELOPMENT.md
    st.markdown(
        """
        <div style="background-color: #1E293B; padding: 16px; border-radius: 8px; border-left: 4px solid #10B981; margin-bottom: 20px;">
            <b>Principais pontos identificados (DEVELOPMENT.md):</b><br>
            • Clientes <b>'Campeões' e 'Fiéis'</b> são poucos mas representam grande parte do faturamento (a diferença não está no valor de cada compra, mas no volume de compras).<br>
            • <b>46,7% dos clientes</b> estão nas faixas <b>'Em Risco', 'Hibernando' ou 'Churn'</b>.<br>
            • <b>Preferir investimentos em influenciadores:</b> maior receita gerada e os clientes tendem a comprar mais (menos risco de churn).<br>
            • <b>Conclusão:</b> Bom ponto, mas é mais médio/longo prazo quando comparado com a hipótese 4. Talvez dê para tomar alguma ação rápida para clientes em risco (e-mails com cupons, etc).
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Métricas Chave
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

    # 4. Análise de Canais (Foco em Influenciadores)
    st.subheader("Aquisição por Canal: Eficiência de Influenciadores")
    
    q_mkt_canal = """
        SELECT 
            canal, 
            ROUND(SUM(receita_gerada) / 1e6, 2) AS receita_gerada_milhoes,
            ROUND(SUM(investimento_reais) / 1e6, 2) AS investimento_milhoes,
            ROUND(SUM(receita_gerada) / NULLIF(SUM(investimento_reais), 0), 2) AS roas
        FROM marketing
        GROUP BY canal
        ORDER BY receita_gerada_milhoes DESC;
    """
    df_mkt_c = repo.execute_sql(q_mkt_canal)

    q_canal = load_query("hipotese_5_clientes/qualidade_canal_aquisicao.sql")
    df_canal = repo.execute_sql(q_canal)

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        fig_inf_rec = px.bar(
            df_mkt_c,
            x="canal",
            y="receita_gerada_milhoes",
            color="canal",
            labels={"receita_gerada_milhoes": "Receita Gerada (R$ Milhões)", "canal": "Canal"},
            title="Receita Gerada por Canal de Mídia (R$ Milhões)"
        )
        fig_inf_rec.update_layout(height=320)
        st.plotly_chart(fig_inf_rec, use_container_width=True)

    with col_c2:
        fig_inf_churn = px.bar(
            df_canal,
            x="canal_aquisicao",
            y="pct_risco_churn",
            labels={"pct_risco_churn": "% Em Risco / Churn", "canal_aquisicao": "Canal"},
            title="% de Clientes em Risco de Churn por Canal",
            color="pct_risco_churn",
            color_continuous_scale="Reds"
        )
        fig_inf_churn.update_layout(height=320)
        st.plotly_chart(fig_inf_churn, use_container_width=True)

    st.markdown("---")

    # 5. Ações Propostas no DEVELOPMENT.md (Padronizadas)
    st.subheader("Ações Identificadas para a Hipótese 5")

    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.success("### 🟢 Quick Win: Reativação de Clientes em Risco")
        st.markdown("""
        - **Problema:** 46,7% dos clientes estão em risco, hibernando ou churn.
        - **Ação:** Disparo rápido de e-mails com cupons de desconto para incentivar segunda e terceira compras.
        """)

    with col_a2:
        st.info("### 🔵 Médio / Longo Prazo: Foco em Influenciadores & Fidelidade")
        st.markdown("""
        - **Problema:** Aquisição em canais genéricos traz clientes com maior taxa de abandono.
        - **Ação:** Priorizar investimentos em marketing com influenciadores (maior receita gerada e clientes tendem a comprar mais vezes).
        - **Fidelização:** Mecanismos contínuos de incentivo à fidelidade pós-primeira compra.
        """)
