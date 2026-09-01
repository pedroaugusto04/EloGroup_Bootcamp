"""
app/views/v_10_analise_relacional.py
Análise Relacional Integrada (Visão 360°).
Cruzamento sistêmico entre Vendas, Marketing, Estoque, Clientes e Atendimento
para diagnosticar efeitos em cascata, gargalos operacionais e oportunidades de rentabilidade.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query


def show_analise_relacional(repo: DuckDBRepository):
    st.markdown('<div class="page-title">🔗 Análise Relacional Integrada (Visão 360°)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Diagnóstico cruzado entre Vendas, Marketing, Estoque, Clientes e Atendimento para identificar impactos sistêmicos na rentabilidade.</div>',
        unsafe_allow_html=True
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "📣 Marketing x Vendas (Mídia vs. ERP)",
        "📦 Estoque x Vendas (Giro & Ruptura)",
        "🚚 Vendas x Atendimento (Logística & CSAT)",
        "👥 Clientes x Suporte (Ciclo & Atrito VIP)"
    ])

    # =========================================================================
    # TAB 1: MARKETING X VENDAS (MÍDIA VS ERP)
    # =========================================================================
    with tab1:
        st.markdown("##### 🎯 Atribuição de Mídia Declarada vs. Realidade Transacional do ERP")
        
        q_mkt_ven = load_query("relacional/mkt_vs_vendas_real.sql")
        df_mkt_ven = repo.execute_sql(q_mkt_ven)

        tot_inv = df_mkt_ven["investimento_mkt"].sum()
        tot_rec_mkt = df_mkt_ven["receita_declarada_mkt"].sum()
        tot_rec_real = df_mkt_ven["receita_liquida_real"].sum()
        tot_margem_real = df_mkt_ven["margem_contribuicao_real"].sum()
        roas_global_mkt = tot_rec_mkt / tot_inv if tot_inv > 0 else 0.0
        roas_global_real = tot_rec_real / tot_inv if tot_inv > 0 else 0.0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Investimento de Mídia Total", f"R$ {tot_inv/1e6:.2f}M", help="Soma de investimento em campanhas de marketing")
        c2.metric("Receita Declarada (Mídia)", f"R$ {tot_rec_mkt/1e6:.2f}M", f"{roas_global_mkt:.2f}x ROAS Declarado")
        c3.metric("Receita Líquida Real (ERP)", f"R$ {tot_rec_real/1e6:.2f}M", f"{roas_global_real:.2f}x ROAS Real Caixa")
        c4.metric("Margem de Contribuição Real", f"R$ {tot_margem_real/1e6:.2f}M", f"{(tot_margem_real/tot_rec_real*100):.1f}% Margem Real")

        st.markdown("---")

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("Receita Declarada (Mídia) vs. Receita Real (ERP)")
            df_plot_rec = df_mkt_ven.melt(
                id_vars=["canal"],
                value_vars=["receita_declarada_mkt", "receita_liquida_real"],
                var_name="Tipo_Receita",
                value_name="Valor_Reais"
            )
            df_plot_rec["Tipo_Receita"] = df_plot_rec["Tipo_Receita"].map({
                "receita_declarada_mkt": "Mídia Declarada (Marketing)",
                "receita_liquida_real": "Receita Real (ERP Vendas)"
            })
            fig_rec_comp = px.bar(
                df_plot_rec,
                x="canal",
                y="Valor_Reais",
                color="Tipo_Receita",
                barmode="group",
                labels={"Valor_Reais": "Receita (R$)", "canal": "Canal", "Tipo_Receita": "Fonte dos Dados"},
                color_discrete_map={
                    "Mídia Declarada (Marketing)": "#64748B",
                    "Receita Real (ERP Vendas)": "#38BDF8"
                }
            )
            fig_rec_comp.update_layout(height=340, legend=dict(orientation="h", y=1.05))
            st.plotly_chart(fig_rec_comp, use_container_width=True)

        with col_g2:
            st.subheader("Ticket Médio Real por Canal (ERP Vendas)")
            fig_tkt = px.bar(
                df_mkt_ven,
                x="canal",
                y="ticket_medio_real",
                color="canal",
                labels={"ticket_medio_real": "Ticket Médio Real (R$)", "canal": "Canal"},
                color_discrete_map={"Influenciador": "#10B981"}
            )
            fig_tkt.add_hline(
                y=df_mkt_ven["ticket_medio_real"].mean(),
                line_dash="dot",
                line_color="#F59E0B",
                annotation_text="Média Geral (~R$ 690)",
                annotation_position="top left"
            )
            fig_tkt.update_layout(height=340, showlegend=False)
            st.plotly_chart(fig_tkt, use_container_width=True)

        st.subheader("Tabela Cruzada: Mídia Declarada vs. Realidade Financeira do ERP")
        st.dataframe(df_mkt_ven.style.format({
            "investimento_mkt": "R$ {:,.2f}",
            "receita_declarada_mkt": "R$ {:,.2f}",
            "roas_declarado_mkt": "{:.2f}x",
            "cac_declarado_mkt": "R$ {:,.2f}",
            "total_pedidos_real": "{:,.0f}",
            "receita_liquida_real": "R$ {:,.2f}",
            "margem_contribuicao_real": "R$ {:,.2f}",
            "ticket_medio_real": "R$ {:,.2f}",
            "desconto_medio_reais": "R$ {:,.2f}",
            "desconto_medio_pct": "{:.1f}%",
            "margem_pct_real": "{:.1f}%",
            "taxa_devolucao_pct": "{:.1f}%",
            "roas_real_erp": "{:.2f}x"
        }), use_container_width=True)

    # =========================================================================
    # TAB 2: ESTOQUE X VENDAS (GIRO & RUPTURA)
    # =========================================================================
    with tab2:
        st.markdown("##### 📦 Cruzamento de Posição de Estoque, Ruptura e Velocidade de Vendas")

        q_est_ven = load_query("relacional/estoque_vs_vendas_giro.sql")
        df_est_ven = repo.execute_sql(q_est_ven)

        tot_cap_est = df_est_ven["capital_imobilizado_estoque"].sum()
        tot_cap_desc = df_est_ven["capital_travado_descontinuado"].sum()
        tot_skus_rup = df_est_ven["skus_em_ruptura"].sum()
        tot_skus = df_est_ven["total_skus"].sum()
        tot_rec_est = df_est_ven["receita_real"].sum()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Capital Total em Estoque", f"R$ {tot_cap_est/1e6:.2f}M", help="Total de valor imobilizado nos 5.000 SKUs")
        c2.metric("Capital em Descontinuados", f"R$ {tot_cap_desc/1e6:.2f}M", f"{(tot_cap_desc/tot_cap_est*100):.1f}% do estoque parado")
        c3.metric("SKUs em Ruptura / Crítico", f"{int(tot_skus_rup)} SKUs", f"{(tot_skus_rup/tot_skus*100):.1f}% do catálogo")
        c4.metric("Receita Anual de Vendas", f"R$ {tot_rec_est/1e6:.2f}M", f"Giro: {(tot_rec_est/tot_cap_est):.2f}x")

        st.markdown("---")

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.subheader("Capital Imobilizado em Estoque vs. Receita Real por Categoria")
            fig_est_bar = px.bar(
                df_est_ven,
                x="categoria",
                y=["capital_imobilizado_estoque", "receita_real"],
                barmode="group",
                labels={"value": "Valor (R$)", "categoria": "Categoria", "variable": "Métrica"},
                color_discrete_map={
                    "capital_imobilizado_estoque": "#94A3B8",
                    "receita_real": "#38BDF8"
                }
            )
            fig_est_bar.update_layout(height=340, legend=dict(orientation="h", y=1.05))
            st.plotly_chart(fig_est_bar, use_container_width=True)

        with col_e2:
            st.subheader("Taxa de Ruptura de Estoque (%) por Categoria")
            fig_rup = px.bar(
                df_est_ven,
                x="categoria",
                y="taxa_ruptura_pct",
                color="taxa_ruptura_pct",
                labels={"taxa_ruptura_pct": "Taxa de Ruptura (%)", "categoria": "Categoria"},
                color_continuous_scale="Reds"
            )
            fig_rup.update_layout(height=340)
            st.plotly_chart(fig_rup, use_container_width=True)

        st.subheader("Tabela Cruzada: Desempenho de Giro e Ruptura por Categoria")
        st.dataframe(df_est_ven.style.format({
            "total_skus": "{:,.0f}",
            "capital_imobilizado_estoque": "R$ {:,.2f}",
            "skus_em_ruptura": "{:,.0f}",
            "taxa_ruptura_pct": "{:.1f}%",
            "skus_descontinuados": "{:,.0f}",
            "capital_travado_descontinuado": "R$ {:,.2f}",
            "lead_time_medio_dias": "{:.1f} dias",
            "unidades_vendidas": "{:,.0f}",
            "receita_real": "R$ {:,.2f}",
            "margem_real": "R$ {:,.2f}",
            "giro_estoque_ratio": "{:.2f}x"
        }), use_container_width=True)

    # =========================================================================
    # TAB 3: VENDAS X ATENDIMENTO (LOGÍSTICA & CSAT)
    # =========================================================================
    with tab3:
        st.markdown("##### 🚚 Atrito Operacional: Como Prazo de Entrega e Devoluções Impactam Suporte e CSAT")

        q_log_atd = load_query("relacional/vendas_vs_atendimento_atrito.sql")
        df_log_atd = repo.execute_sql(q_log_atd)

        tot_ped_log = df_log_atd["total_pedidos"].sum()
        tot_tkt_log = df_log_atd["total_chamados_suporte"].sum()
        tot_custo_sup = df_log_atd["custo_suporte_total"].sum()
        tot_custo_evit = df_log_atd["custo_evitavel_automacao"].sum()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pedidos Analisados", f"{tot_ped_log:,}")
        c2.metric("Chamados Vinculados a Pedidos", f"{tot_tkt_log:,}", f"{(tot_tkt_log/tot_ped_log*100):.1f}% taxa de contato")
        c3.metric("Custo Total de Suporte Vinculado", f"R$ {tot_custo_sup:,.2f}")
        c4.metric("Custo Evitável Mapeado", f"R$ {tot_custo_evit:,.2f}", f"{(tot_custo_evit/tot_custo_sup*100 if tot_custo_sup>0 else 0):.1f}% automatizável")

        st.markdown("---")

        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.subheader("Taxa de Abertura de Chamados e % CSAT Crítico por Prazo de Entrega")
            fig_sla = go.Figure()
            fig_sla.add_trace(go.Bar(
                x=df_log_atd["faixa_entrega"],
                y=df_log_atd["taxa_abertura_chamados_pct"],
                name="Taxa de Abertura de Chamados (%)",
                marker_color="#38BDF8"
            ))
            fig_sla.add_trace(go.Scatter(
                x=df_log_atd["faixa_entrega"],
                y=df_log_atd["pct_csat_critico"],
                name="% Chamados com CSAT Crítico (<=2)",
                mode="lines+markers",
                line=dict(color="#EF4444", width=2.5),
                yaxis="y2"
            ))
            fig_sla.update_layout(
                height=340,
                yaxis=dict(title="Taxa de Contato (%)"),
                yaxis2=dict(title="% CSAT Crítico", overlaying="y", side="right"),
                legend=dict(orientation="h", y=1.1)
            )
            st.plotly_chart(fig_sla, use_container_width=True)

        with col_l2:
            st.subheader("Custos de Suporte (Total vs. Evitável) por Faixa de Entrega")
            fig_c_log = px.bar(
                df_log_atd,
                x="faixa_entrega",
                y=["custo_suporte_total", "custo_evitavel_automacao"],
                barmode="group",
                labels={"value": "Custo (R$)", "faixa_entrega": "Faixa de Prazo de Entrega", "variable": "Tipo de Custo"},
                color_discrete_map={
                    "custo_suporte_total": "#64748B",
                    "custo_evitavel_automacao": "#F59E0B"
                }
            )
            fig_c_log.update_layout(height=340, legend=dict(orientation="h", y=1.05))
            st.plotly_chart(fig_c_log, use_container_width=True)

        st.subheader("Tabela Cruzada: Desempenho Logístico x Atrito no Atendimento")
        st.dataframe(df_log_atd.style.format({
            "total_pedidos": "{:,.0f}",
            "total_chamados_suporte": "{:,.0f}",
            "taxa_abertura_chamados_pct": "{:.1f}%",
            "csat_medio": "{:.2f}",
            "pct_csat_critico": "{:.1f}%",
            "taxa_devolucao_pct": "{:.1f}%",
            "custo_suporte_total": "R$ {:,.2f}",
            "custo_evitavel_automacao": "R$ {:,.2f}"
        }), use_container_width=True)

    # =========================================================================
    # TAB 4: CLIENTES X VENDAS X SUPORTE (CICLO DE VIDA & ATRITO VIP)
    # =========================================================================
    with tab4:
        st.markdown("##### 👥 Ciclo de Vida do Cliente: Identificação de Atrito Operacional nos Clientes de Alto Valor")

        q_cli_atd = load_query("relacional/clientes_ciclo_atrito.sql")
        df_cli_atd = repo.execute_sql(q_cli_atd)

        tot_cli_base = df_cli_atd["total_clientes"].sum()
        tot_ltv_base = df_cli_atd["ltv_total_segmento"].sum()
        df_vip = df_cli_atd[df_cli_atd["segmento_rfm"].isin(["Campeão", "Fiel"])]
        vips_com_atrito = df_vip["clientes_com_csat_critico"].sum()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Base Total de Clientes", f"{tot_cli_base:,}")
        c2.metric("LTV Total Acumulado", f"R$ {tot_ltv_base/1e6:.2f}M")
        c3.metric("Clientes VIPs (Campeões+Fiéis)", f"{df_vip['total_clientes'].sum():,}", f"{(df_vip['total_clientes'].sum()/tot_cli_base*100):.1f}% da base")
        c4.metric("VIPs com CSAT Crítico (Atenção)", f"{int(vips_com_atrito):,} clientes", f"{(vips_com_atrito/df_vip['total_clientes'].sum()*100):.1f}% dos VIPs")

        st.markdown("---")

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("LTV Médio vs. Média de Pedidos no Histórico")
            fig_ltv = px.bar(
                df_cli_atd,
                x="segmento_rfm",
                y="ltv_medio",
                color="media_pedidos_historico",
                labels={"ltv_medio": "LTV Médio (R$)", "segmento_rfm": "Segmento RFM", "media_pedidos_historico": "Média de Pedidos"},
                color_continuous_scale="Blues"
            )
            fig_ltv.update_layout(height=340)
            st.plotly_chart(fig_ltv, use_container_width=True)

        with col_c2:
            st.subheader("Clientes com Experiência Negativa (CSAT Crítico) por Segmento")
            fig_crit = px.bar(
                df_cli_atd,
                x="segmento_rfm",
                y="clientes_com_csat_critico",
                color="pct_clientes_com_csat_critico",
                labels={"clientes_com_csat_critico": "Clientes com CSAT <= 2", "segmento_rfm": "Segmento RFM", "pct_clientes_com_csat_critico": "% do Segmento"},
                color_continuous_scale="Reds"
            )
            fig_crit.update_layout(height=340)
            st.plotly_chart(fig_crit, use_container_width=True)

        st.subheader("Tabela Cruzada: Ciclo de Vida do Cliente, Devoluções e Atrito no Suporte")
        st.dataframe(df_cli_atd.style.format({
            "total_clientes": "{:,.0f}",
            "ltv_medio": "R$ {:,.2f}",
            "ltv_total_segmento": "R$ {:,.2f}",
            "media_pedidos_historico": "{:.1f}",
            "chamados_medios_por_cliente": "{:.2f}",
            "csat_medio_atendimento": "{:.2f}",
            "clientes_com_csat_critico": "{:,.0f}",
            "pct_clientes_com_csat_critico": "{:.1f}%",
            "taxa_devolucao_pedidos_pct": "{:.1f}%",
            "custo_suporte_segmento": "R$ {:,.2f}"
        }), use_container_width=True)
