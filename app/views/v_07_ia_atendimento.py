"""
app/views/v_07_ia_atendimento.py
Módulo de IA & Automação de Atendimento ao Cliente.
Atende à Hipótese 1: Diagnóstico de sintomas operacionais no suporte,
Classificador Inteligente de Tickets (NLP/IA) e Simulador de ROI de Automação.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query


def classify_ticket_text(text: str) -> dict:
    """Classificador de tickets via regras semânticas / NLP."""
    text_lower = text.lower()

    if any(w in text_lower for w in ["onde está", "rastreio", "rastrear", "atraso", "atrasado", "chega quando", "entrega", "status do pedido", "código de rastreio"]):
        return {
            "categoria": "Onde está meu pedido?",
            "urgencia": "Alta",
            "sentimento": "Negativo / Ansioso",
            "automavel": True,
            "sla_sugerido": "< 1 minuto (Bot)",
            "acao_recomendada": "Disparar link de rastreamento em tempo real via WhatsApp/SMS e status da transportadora.",
            "risco_churn": "Médio"
        }
    elif any(w in text_lower for w in ["defeito", "quebrado", "rasgado", "estragado", "com problema", "falha", "veio quebrado", "danificado"]):
        return {
            "categoria": "Defeito / Qualidade",
            "urgencia": "Crítica",
            "sentimento": "Muito Negativo",
            "automavel": False,
            "sla_sugerido": "< 15 minutos (N2)",
            "acao_recomendada": "Coletar fotos via upload automático, gerar código de logística reversa e enviar novo item prioritário.",
            "risco_churn": "Alto"
        }
    elif any(w in text_lower for w in ["tamanho", "ficou pequeno", "ficou grande", "trocar", "troca", "número", "numeração", "não serviu"]):
        return {
            "categoria": "Troca de Tamanho",
            "urgencia": "Média",
            "sentimento": "Neutro",
            "automavel": True,
            "sla_sugerido": "< 2 minutos (Bot)",
            "acao_recomendada": "Emitir voucher de troca imediato e sugerir o tamanho ideal com base no provador virtual.",
            "risco_churn": "Médio"
        }
    elif any(w in text_lower for w in ["dúvida", "como usar", "como funciona", "especificação", "material", "medidas", "composição"]):
        return {
            "categoria": "Dúvida Técnica / Produto",
            "urgencia": "Baixa",
            "sentimento": "Neutro",
            "automavel": True,
            "sla_sugerido": "Imediato (Base de Conhecimento)",
            "acao_recomendada": "Responder via FAQ Dinâmico / GenAI com especificações técnicas do SKU.",
            "risco_churn": "Baixo"
        }
    elif any(w in text_lower for w in ["pagamento", "cartão", "pix", "não aprovado", "estorno", "cobrança", "reprovado"]):
        return {
            "categoria": "Pagamento não aprovado",
            "urgencia": "Alta",
            "sentimento": "Negativo",
            "automavel": True,
            "sla_sugerido": "< 5 minutos",
            "acao_recomendada": "Reenviar link de pagamento alternativo (Pix com 5% desc.) e checar antifraude.",
            "risco_churn": "Alto"
        }
    elif any(w in text_lower for w in ["parabéns", "adorei", "excelente", "muito bom", "ótimo", "recomendo", "amei"]):
        return {
            "categoria": "Elogio / Feedback Positivo",
            "urgencia": "Baixa",
            "sentimento": "Muito Positivo",
            "automavel": True,
            "sla_sugerido": "Automático",
            "acao_recomendada": "Agradecer cliente e convidar para programa de fidelidade / avaliação na loja.",
            "risco_churn": "Nulo"
        }
    else:
        return {
            "categoria": "Outros / Não Identificado",
            "urgencia": "Média",
            "sentimento": "Neutro",
            "automavel": False,
            "sla_sugerido": "< 30 minutos (N1)",
            "acao_recomendada": "Encaminhar para triagem manual de atendente.",
            "risco_churn": "Médio"
        }


def show_ia_atendimento(repo: DuckDBRepository):
    st.markdown('<div class="page-title">🤖 IA & Automação de Atendimento</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Diagnóstico da Hipótese 1: Triagem Inteligente, Causas-Raiz e Simulador de Economia de Custos.</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "📊 1. Diagnóstico de Sintomas & Custo",
        "🧠 2. Protótipo: Classificador Inteligente de Tickets",
        "💰 3. Simulador de ROI & Economia com IA"
    ])

    # ==========================================
    # TAB 1: DIAGNÓSTICO DE CAUSAS-RAIZ
    # ==========================================
    with tab1:
        st.subheader("Causas-Raiz e Volume de Chamados Evitáveis")
        st.markdown(
            """
            > **Diagnóstico da Hipótese 1**: O atendimento concentra os **sintomas** de problemas ocorridos em outras etapas da cadeia 
            (logística de entrega e especificação de produtos). Quase **45% do volume total** de tickets é composto por dúvidas simples ou 
            consultas de rastreamento, passíveis de automação completa via IA.
            """
        )

        q_diag = load_query("atendimento/causas_raiz_e_automacao.sql", where_sql="")
        df_diag = repo.execute_sql(q_diag)

        col_k1, col_k2, col_k3, col_k4 = st.columns(4)
        total_tickets = df_diag["total_tickets"].sum()
        custo_total = df_diag["custo_operacional_total"].sum()
        custo_automavel = df_diag["custo_evitavel_automacao"].sum()
        pct_automatizavel = (df_diag[df_diag["is_automatizavel"]]["total_tickets"].sum() / total_tickets) * 100.0

        col_k1.metric("Volume Total de Chamados", f"{total_tickets:,}")
        col_k2.metric("Custo Total de Operação", f"R$ {custo_total:,.2f}")
        col_k3.metric("Volume Automatizável", f"{pct_automatizavel:.1f}% dos tickets")
        col_k4.metric("Custo Evitável Identificado", f"R$ {custo_automavel:,.2f}", delta="-44.8% custo")

        st.markdown("---")

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_custo = px.bar(
                df_diag,
                x="categoria_problema",
                y="custo_operacional_total",
                color="is_automatizavel",
                labels={"custo_operacional_total": "Custo Total (R$)", "categoria_problema": "Motivo", "is_automatizavel": "Automatizável via IA?"},
                color_discrete_map={True: "#3B82F6", False: "#9CA3AF"},
                title="Custo Operacional por Categoria de Chamado (R$)"
            )
            fig_custo.update_layout(height=340)
            st.plotly_chart(fig_custo, width="stretch")

        with col_g2:
            fig_csat = px.scatter(
                df_diag,
                x="tempo_resposta_medio_min",
                y="csat_medio",
                size="total_tickets",
                color="categoria_problema",
                labels={"tempo_resposta_medio_min": "Tempo Médio 1ª Resposta (min)", "csat_medio": "CSAT Médio (1 a 5)"},
                title="CSAT vs Tempo de Resposta por Motivo"
            )
            fig_csat.update_layout(height=340)
            st.plotly_chart(fig_csat, width="stretch")

        st.subheader("Detalhamento Analítico de Causas-Raiz")
        st.dataframe(
            df_diag.style.format({
                "total_tickets": "{:,.0f}",
                "pct_total": "{:.1f}%",
                "csat_medio": "{:.2f}",
                "tickets_detratores": "{:,.0f}",
                "tempo_resposta_medio_min": "{:.1f} min",
                "tempo_resolucao_medio_h": "{:.1f} h",
                "custo_operacional_total": "R$ {:,.2f}",
                "custo_evitavel_automacao": "R$ {:,.2f}"
            }),
            width="stretch"
        )

    # ==========================================
    # TAB 2: PROTÓTIPO DE IA (CLASSIFICADOR)
    # ==========================================
    with tab2:
        st.subheader("Demonstração Interativa: Classificador & Triagem de Tickets")
        st.markdown(
            "Digite uma mensagem de cliente ou escolha um dos exemplos pré-configurados para ver a IA processar a categorização, urgência, automação e ação sugerida."
        )

        exemplos = {
            "Rastreamento de Pedido": "Olá, meu pedido ORD-084920 foi aprovado há 4 dias e até agora não recebi o código de rastreamento. Onde está meu pacote?",
            "Defeito no Produto": "Recebi a jaqueta hoje mas o zíper veio completamente quebrado e descosturado. Quero devolver ou receber uma nova!",
            "Troca de Tamanho": "O tênis tamanho 40 ficou muito apertado no meu pé. Gostaria de saber como faço para trocar pelo 41.",
            "Dúvida Técnica": "Qual a composição do tecido deste vestido? Ele pode ser lavado em máquina convencional?",
            "Problema no Pagamento": "Tentei pagar com cartão de crédito duas vezes e deu compra recusada, mas o limite foi cobrado.",
            "Elogio ao Atendimento": "Amei a rapidez da entrega e o carinho da embalagem! Estão de parabéns, virei cliente fiel."
        }

        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            escolha_exemplo = st.selectbox("Carregar mensagem de exemplo:", list(exemplos.keys()))
        
        texto_inicial = exemplos[escolha_exemplo]
        texto_input = st.text_area("Mensagem do Cliente:", value=texto_inicial, height=100)

        if st.button("🚀 Processar Ticket com IA", type="primary"):
            resultado = classify_ticket_text(texto_input)

            st.markdown("### Resultado da Análise de IA")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Categoria Prevista", resultado["categoria"])
            c2.metric("Urgência", resultado["urgencia"])
            c3.metric("Risco de Churn", resultado["risco_churn"])
            c4.metric("Automatizável N1?", "Sim (Bot / IA)" if resultado["automavel"] else "Não (Humano N2)")

            st.info(f"**Ação Recomendada pela IA:** {resultado['acao_recomendada']}")
            st.caption(f"**SLA Alvo:** {resultado['sla_sugerido']} | **Sentimento Detectado:** {resultado['sentimento']}")

    # ==========================================
    # TAB 3: SIMULADOR DE ROI DA AUTOMAÇÃO
    # ==========================================
    with tab3:
        st.subheader("Simulador de Impacto Financeiro e Produtividade (Business Case)")
        st.markdown(
            "Ajuste os parâmetros abaixo para projetar a economia financeira e os ganhos operacionais com a implementação da IA Conversacional e Notificações Proativas."
        )

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            taxa_automacao = st.slider("Taxa de Resolução Automática de Tickets N1 (%)", min_value=30, max_value=95, value=75, step=5)
            custo_medio_ticket = st.slider("Custo Médio por Atendimento Humano (R$)", min_value=5.0, max_value=25.0, value=15.0, step=1.0)
        with col_s2:
            volume_n1_ano = st.number_input("Volume Anual de Chamados de Rastreamento & Dúvidas", value=16079, step=500)
            tempo_humano_min = st.slider("Tempo Médio Humano por Ticket (minutos)", min_value=5, max_value=30, value=12, step=1)

        # Cálculos de ROI
        tickets_economizados = int(volume_n1_ano * (taxa_automacao / 100.0))
        custo_economizado_reais = tickets_economizados * custo_medio_ticket
        horas_economizadas = (tickets_economizados * tempo_humano_min) / 60.0
        reducao_sla_pct = taxa_automacao * 0.95  # Redução drástica no tempo de espera

        st.markdown("---")
        st.markdown("#### Ganhos Projetados com Automação de IA:")

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Tickets Automatizados / Ano", f"{tickets_economizados:,}")
        r2.metric("Economia Financeira Anual", f"R$ {custo_economizado_reais:,.2f}", delta=f"+ R$ {custo_economizado_reais/1e3:.1f}k")
        r3.metric("Horas de Atendimento Poupadas", f"{horas_economizadas:,.0f} horas", delta="Produtividade")
        r4.metric("Redução de SLA Médio", f"- {reducao_sla_pct:.0f}%", delta="Resposta Imediata")

        st.success(
            f"💡 **Recomendação Executiva**: A automação de {taxa_automacao}% dos chamados repetitivos elimina a necessidade de triagem manual para mais de **{tickets_economizados:,} clientes/ano**, liberando mais de **{horas_economizadas:,.0f} horas da equipe** para casos complexos de qualidade e devolução."
        )
