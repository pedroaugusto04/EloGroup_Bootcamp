"""
app/views/v_08_plano_estrategico.py
Matriz de Priorização de Iniciativas e Roadmap Executivo.
Alinhado estritamente com as oportunidades e conclusões mapeadas em DEVELOPMENT.md.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from src.infrastructure.database import DuckDBRepository


def show_plano_estrategico(repo: DuckDBRepository):
    st.markdown('<div class="page-title">🎯 Matriz de Priorização & Roadmap</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Priorização das ações identificadas nas Hipóteses 4, 5 e 6 descritas no DEVELOPMENT.md.</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs([
        "⚖️ 1. Matriz de Priorização (Impacto x Prazo)",
        "🗓️ 2. Roadmap Executivo (Curto vs Médio/Longo Prazo)"
    ])

    # ==========================================
    # TAB 1: MATRIZ DE PRIORIZAÇÃO
    # ==========================================
    with tab1:
        st.subheader("Matriz de Priorização das Iniciativas Mapeadas")
        st.markdown(
            "Classificação das iniciativas baseadas estritamente nos pontos e conclusões do `DEVELOPMENT.md`:"
        )

        # Iniciativas estritamente descritas no DEVELOPMENT.md
        iniciativas = [
            {
                "Iniciativa": "Notificações de Status do Pedido via WhatsApp/E-mail",
                "Hipótese": "Hipótese 4 (Atendimento)",
                "Tipo": "Quick Win (Curto Prazo)",
                "Impacto_Financeiro": "R$ 159.660,00 (Custo Evitável)",
                "Impacto_Valor_R$": 159660,
                "Esforço_Dias": 15,
                "Descrição": "Uma única mensagem de WhatsApp após a compra com link de rastreamento direto para evitar chamadas de 'Onde está meu pedido'."
            },
            {
                "Iniciativa": "Liquidação para Queima de Estoque Descontinuado",
                "Hipótese": "Hipótese 6 (Decisão & Estoque)",
                "Tipo": "Quick Win (Curto Prazo)",
                "Impacto_Financeiro": "R$ 14.775.347,64 (Capital Parado)",
                "Impacto_Valor_R$": 14775347,
                "Esforço_Dias": 20,
                "Descrição": "Liquidação promocional para liberar o capital travado em 207 SKUs fora de linha e transformar em caixa imediato."
            },
            {
                "Iniciativa": "Ação Rápida de Reativação para Clientes 'Em Risco'",
                "Hipótese": "Hipótese 5 (Segmentação)",
                "Tipo": "Curto / Médio Prazo",
                "Impacto_Financeiro": "Proteção de Recompra (46,7% da base)",
                "Impacto_Valor_R$": 650000,
                "Esforço_Dias": 30,
                "Descrição": "Disparo de e-mails com cupons de desconto para incentivar segunda e terceira compras em clientes da faixa 'Em Risco'."
            },
            {
                "Iniciativa": "Melhorias de FAQ / Páginas de Produto & Atendimento IA",
                "Hipótese": "Hipótese 4 (Atendimento)",
                "Tipo": "Médio Prazo",
                "Impacto_Financeiro": "R$ 78.888,00 (Custo Evitável)",
                "Impacto_Valor_R$": 78888,
                "Esforço_Dias": 45,
                "Descrição": "Melhores explicações nas páginas dos produtos / FAQ detalhado e atendimento automatizado com IA via WhatsApp para dúvidas técnicas."
            },
            {
                "Iniciativa": "Priorização de Investimento em Influenciadores",
                "Hipótese": "Hipótese 5 (Segmentação)",
                "Tipo": "Médio Prazo",
                "Impacto_Financeiro": "Maior Receita e Menor Churn",
                "Impacto_Valor_R$": 1200000,
                "Esforço_Dias": 50,
                "Descrição": "Focar investimentos em marketing com influenciadores, canal que gera maior receita e clientes com menor risco de abandono."
            },
            {
                "Iniciativa": "Ajuste no Mecanismo de Compras e Alertas de Ruptura",
                "Hipótese": "Hipótese 6 (Decisão & Estoque)",
                "Tipo": "Médio / Longo Prazo",
                "Impacto_Financeiro": "R$ 7.250.310,60 (Risco de Falta)",
                "Impacto_Valor_R$": 7250310,
                "Esforço_Dias": 70,
                "Descrição": "Ajustar compras e reposição para os 701 SKUs que operam abaixo do ponto de pedido, evitando falta de produtos muito vendidos."
            },
            {
                "Iniciativa": "Relatórios Gerados com IA / Dashboards para Gestão",
                "Hipótese": "Hipótese 6 (Decisão & Estoque)",
                "Tipo": "Médio Prazo",
                "Impacto_Financeiro": "Apoio à Decisão da Gestão",
                "Impacto_Valor_R$": 350000,
                "Esforço_Dias": 40,
                "Descrição": "Resumos automatizados com IA e dashboards dinâmicos para a gestão acompanhar a situação do estoque e decidir com base em dados."
            }
        ]

        df_iniciativas = pd.DataFrame(iniciativas)

        # Gráfico da Matriz
        fig_matriz = px.scatter(
            df_iniciativas,
            x="Esforço_Dias",
            y="Impacto_Valor_R$",
            size="Impacto_Valor_R$",
            color="Tipo",
            hover_name="Iniciativa",
            text="Iniciativa",
            labels={"Esforço_Dias": "Tempo Estimado de Implementação (Dias)", "Impacto_Valor_R$": "Impacto / Volume Mapeado (R$)"},
            title="Matriz de Priorização: Impacto Financeiro vs Tempo de Implementação",
            color_discrete_map={"Quick Win (Curto Prazo)": "#10B981", "Curto / Médio Prazo": "#3B82F6", "Médio Prazo": "#6366F1", "Médio / Longo Prazo": "#F59E0B"}
        )
        fig_matriz.update_traces(textposition='top center')
        fig_matriz.update_layout(height=460)
        st.plotly_chart(fig_matriz, use_container_width=True)

        st.markdown("#### Tabela Detalhada das Iniciativas do `DEVELOPMENT.md`:")
        st.dataframe(
            df_iniciativas[["Iniciativa", "Hipótese", "Tipo", "Impacto_Financeiro", "Descrição"]],
            use_container_width=True
        )

    # ==========================================
    # TAB 2: ROADMAP EXECUTIVO
    # ==========================================
    with tab2:
        st.subheader("Roadmap das Ações por Horizonte de Tempo")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.success("### 🟢 Curto Prazo (Quick Wins)")
            st.markdown("""
            **Foco:** Ações rápidas de alto retorno imediato.
            
            1. **Notificações de Rastreio (Hipótese 4):**
               - Envio de mensagem no WhatsApp após a compra com link de rastreamento (ataca o gargalo de R$ 159,6k).
            2. **Queima de Estoque Parado (Hipótese 6):**
               - Liquidação dos 207 SKUs descontinuados para liberar até R$ 14,7M em caixa.
            3. **Cupons para Clientes em Risco (Hipótese 5):**
               - Disparo de e-mails promocionais para incentivar recompras em clientes da faixa 'Em Risco'.
            """)

        with c2:
            st.info("### 🔵 Médio Prazo (Processos & Mídia)")
            st.markdown("""
            **Foco:** Eficiência operacional e melhor alocação de verba.
            
            1. **FAQ & Atendimento com IA (Hipótese 4):**
               - Melhores explicações nas páginas dos produtos e automação com IA via WhatsApp para dúvidas técnicas (R$ 78,8k).
            2. **Foco em Influenciadores (Hipótese 5):**
               - Priorizar investimentos de marketing em influenciadores (maior receita gerada e menor risco de churn).
            3. **Relatórios com IA para a Gestão (Hipótese 6):**
               - Relatórios automatizados e dashboards dinâmicos para apoiar a tomada de decisão da gestão.
            """)

        with c3:
            st.warning("### 🟣 Médio / Longo Prazo (Estrutural)")
            st.markdown("""
            **Foco:** Planejamento sustentável de estoque e fidelização.
            
            1. **Ajuste no Mecanismo de Compras (Hipótese 6):**
               - Ajustar mecanismo de compra e liberação de estoque para evitar falta nos 701 SKUs com estoque abaixo do ponto de pedido (R$ 7,2M em risco).
            2. **Mecanismos Contínuos de Fidelidade (Hipótese 5):**
               - Estruturar programas de fidelidade para incentivar segunda e terceira compras recorrentes.
            """)
