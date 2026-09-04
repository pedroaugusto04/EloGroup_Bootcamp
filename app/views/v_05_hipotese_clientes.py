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
    st.markdown('<div class="page-title">Hipótese 5: Segmentação & Concentração de Clientes</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle"><i>"O crescimento pode esconder diferenças importantes entre segmentos de clientes."</i></div>', unsafe_allow_html=True)

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

    st.warning("O cruzamento de canal, LTV e churn foi removido: o CRM contém 15.000 clientes, mas apenas 346 têm vínculo com vendas, e o Marketing cobre um período maior que o ERP.")
    return

    # 4. Análise de Canais: Mídia Declarada (Marketing) vs. Vendas Reais (ERP)
    st.subheader("Comparativo de Canais: Mídia Declarada vs. Vendas Reais no ERP")
    
    q_cross = """
        WITH mkt AS (
            SELECT 
                canal,
                SUM(investimento_reais) AS investimento_mkt,
                SUM(receita_gerada) AS receita_mkt,
                ROUND(SUM(receita_gerada) / NULLIF(SUM(investimento_reais), 0), 2) AS roas_mkt
            FROM marketing
            GROUP BY canal
        ),
        vendas_real AS (
            SELECT 
                canal,
                COUNT(order_id) AS total_pedidos,
                SUM(receita_liquida) AS receita_real,
                SUM(margem_calculada) AS margem_real,
                ROUND(AVG(receita_liquida), 2) AS ticket_medio_real,
                ROUND(AVG(desconto_reais), 2) AS desconto_medio_reais,
                ROUND(SUM(margem_calculada) / NULLIF(SUM(receita_liquida), 0) * 100.0, 1) AS margem_pct_real
            FROM vendas
            WHERE status_pagamento = 'Aprovado'
            GROUP BY canal
        ),
        first_order AS (
            SELECT 
                customer_id, 
                canal AS canal_aquisicao, 
                MIN(data_pedido) AS data_primeira_compra
            FROM vendas
            WHERE status_pagamento = 'Aprovado'
            GROUP BY customer_id, canal
            QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY data_primeira_compra ASC) = 1
        ),
        churn_qualidade AS (
            SELECT 
                f.canal_aquisicao AS canal,
                ROUND(SUM(CASE WHEN c.segmento_rfm IN ('Em Risco', 'Hibernando', 'Churn') THEN 1 ELSE 0 END) * 100.0 / COUNT(c.customer_id), 1) AS pct_risco_churn
            FROM clientes c
            JOIN first_order f ON c.customer_id = f.customer_id
            GROUP BY f.canal_aquisicao
        )
        SELECT 
            v.canal,
            m.investimento_mkt,
            m.receita_mkt,
            m.roas_mkt,
            v.receita_real,
            v.ticket_medio_real,
            v.margem_pct_real,
            v.desconto_medio_reais,
            COALESCE(q.pct_risco_churn, 0.0) AS pct_risco_churn
        FROM vendas_real v
        LEFT JOIN mkt m ON v.canal = m.canal
        LEFT JOIN churn_qualidade q ON v.canal = q.canal
        ORDER BY v.ticket_medio_real DESC;
    """
    df_cross = repo.execute_sql(q_cross)

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        fig_ticket = px.bar(
            df_cross,
            x="canal",
            y="ticket_medio_real",
            color="canal",
            labels={"ticket_medio_real": "Ticket Médio Real (R$)", "canal": "Canal"},
            title="Ticket Médio Real por Canal (ERP Vendas)",
            color_discrete_map={"Influenciador": "#10B981"}
        )
        fig_ticket.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig_ticket, use_container_width=True)

    with col_c2:
        fig_churn = px.bar(
            df_cross,
            x="canal",
            y="pct_risco_churn",
            labels={"pct_risco_churn": "% Em Risco / Churn", "canal": "Canal de Entrada"},
            title="% de Clientes em Risco de Churn por Canal de Aquisição",
            color="pct_risco_churn",
            color_continuous_scale="Reds"
        )
        fig_churn.update_layout(height=320)
        st.plotly_chart(fig_churn, use_container_width=True)

    st.markdown("##### 📊 Tabela Comparativa Cruzada (Mídia vs. ERP Vendas):")
    st.dataframe(df_cross.style.format({
        "investimento_mkt": "R$ {:,.2f}",
        "receita_mkt": "R$ {:,.2f}",
        "roas_mkt": "{:.2f}x",
        "receita_real": "R$ {:,.2f}",
        "ticket_medio_real": "R$ {:,.2f}",
        "margem_pct_real": "{:.1f}%",
        "desconto_medio_reais": "R$ {:,.2f}",
        "pct_risco_churn": "{:.1f}%"
    }), use_container_width=True)

