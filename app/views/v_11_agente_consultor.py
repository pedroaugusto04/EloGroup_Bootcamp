"""
app/views/v_11_agente_consultor.py
Interface de Chat Dedicada & Minimalista para o Copiloto de Estoque (Vértice Retail).
Foco em conversação analítica, consultas determinísticas no DuckDB e memória contínua.
"""

import uuid
import streamlit as st
from src.infrastructure.database import DuckDBRepository
from src.agent.service import InventoryAgentService


def show_agente_consultor(repo: DuckDBRepository):
    """Renderiza a interface de chat minimalista para o Copiloto de Estoque."""
    service = InventoryAgentService()

    # Inicialização de estado da sessão de chat
    if "copilot_thread_id" not in st.session_state:
        st.session_state["copilot_thread_id"] = str(uuid.uuid4())

    if "copilot_messages" not in st.session_state:
        st.session_state["copilot_messages"] = []

    # Verificação de origem: Se o usuário veio por deep link de e-mail e o chat está no início,
    # pré-carrega o conteúdo da auditoria executiva como contexto inicial da conversa.
    source_param = str(st.query_params.get("source", "")).lower()
    from_param = str(st.query_params.get("from", "")).lower()
    is_from_email = (source_param == "email" or from_param == "email")

    if is_from_email and len(st.session_state["copilot_messages"]) == 0:
        from src.agent.worker import load_latest_audit_snapshot
        snapshot = load_latest_audit_snapshot() or {}
        report_content = snapshot.get("final_report")
        
        if report_content:
            init_context = (
                f"{report_content}\n\n"
                "---\n"
                "**Como posso apoiar a sua análise?** Você pode solicitar simulações detalhadas, aprofundamento em SKUs específicos ou estratégias de liquidação."
            )
        else:
            structured = snapshot.get("structured_data") or {}
            total_stranded = structured.get("total_stranded_cash")
            ruptura_count = structured.get("ruptura_count")
            criticos_count = structured.get("criticos_count")
            mkt_cats = structured.get("mkt_alert_categories", [])
            summary = []
            if total_stranded is not None:
                summary.append(f"- **Capital imobilizado**: `R$ {total_stranded:,.2f}`")
            if ruptura_count is not None and criticos_count is not None:
                summary.append(f"- **Ruptura e risco**: `{ruptura_count + criticos_count} SKUs`")
            if mkt_cats:
                summary.append(f"- **Categorias em alerta**: `{', '.join(mkt_cats)}`")
            init_context = (
                "**Contexto da auditoria de estoque:**\n\n"
                + ("\n".join(summary) if summary else "Nenhum dado da auditoria está disponível no momento.")
                + "\n\n**Como posso apoiar a sua análise?** Você pode solicitar simulações, investigações de SKUs específicos ou estratégias de abastecimento."
            )
            
        st.session_state["copilot_messages"] = [{"role": "assistant", "content": init_context}]
        service.seed_copilot(
            thread_id=st.session_state["copilot_thread_id"],
            initial_message=init_context
        )



    # =========================================================================
    # CABEÇALHO MINIMALISTA DO CHAT
    # =========================================================================
    col_header, col_actions = st.columns([4, 1])
    with col_header:
        st.markdown(
            """
            <div style="margin-bottom: 8px;">
                <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #F3F4F6;">Copiloto de Estoque</h2>
                <p style="margin: 2px 0 0 0; font-size: 12px; color: #9CA3AF;">
                    Consultoria Analítica de Estoque & Rentabilidade &bull; <span style="color: #10B981; font-weight: 600;">Conectado</span>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_actions:
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        if st.button("Nova Conversa", use_container_width=True, help="Reinicia a conversa e limpa o contexto da sessão."):
            st.session_state["copilot_thread_id"] = str(uuid.uuid4())
            st.session_state["copilot_messages"] = []
            st.rerun()

    st.markdown("<hr style='margin-top: 4px; margin-bottom: 24px; border: none; border-top: 1px solid rgba(255, 255, 255, 0.08);'>", unsafe_allow_html=True)

    prompt_to_send = None

    # =========================================================================
    # EMPTY STATE (BOAS-VINDAS QUANDO NÃO HÁ MENSAGENS)
    # =========================================================================
    if len(st.session_state["copilot_messages"]) == 0:
        st.markdown(
            """
            <div style="text-align: center; margin: 30px 0 25px 0;">
                <h3 style="font-size: 20px; font-weight: 600; color: #F9FAFB; margin-bottom: 6px;">
                    Como posso apoiar a estratégia de estoque hoje?
                </h3>
                <p style="font-size: 13px; color: #9CA3AF; max-width: 620px; margin: 0 auto;">
                    Acesso direto ao banco analítico DuckDB (Ano Base 2026). Simulações financeiras de liquidação, mapeamento de rupturas, auditoria de marketing e detalhamento de SKUs.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<p style='font-size: 11px; font-weight: 600; color: #9CA3AF; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px;'>Sugestões de Análise:</p>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "**Simular Liquidação de Moda (-30%)**\n\n"
                "Simula a queima da categoria com desconto e calcula o caixa liberado.",
                use_container_width=True,
            ):
                prompt_to_send = "Simule liquidar a categoria Moda com 30% de desconto e mostre o potencial de liberação de caixa e impacto financeiro."

            if st.button(
                "**Diagnóstico 360° do SKU-00185**\n\n"
                "Investigação detalhada de vendas, margem, estoque e devoluções.",
                use_container_width=True,
            ):
                prompt_to_send = "Faça uma investigação detalhada 360° do produto SKU-00185."

        with col2:
            if st.button(
                "**Descompasso entre Marketing e Ruptura**\n\n"
                "Identifica categorias com verba de mídia ativa e estoque em ruptura.",
                use_container_width=True,
            ):
                prompt_to_send = "Quais categorias apresentam descompasso crítico entre verba de marketing e ruptura de estoque?"

            if st.button(
                "**Atrito Operacional e Devoluções**\n\n"
                "Lista produtos com alto índice de devolução e frete desperdiçado.",
                use_container_width=True,
            ):
                prompt_to_send = "Quais produtos têm a maior taxa de devolução e custo de frete desperdiçado?"

    # =========================================================================
    # HISTÓRICO DE CONVERSAÇÃO (MENSAGENS)
    # =========================================================================
    for msg in st.session_state["copilot_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # =========================================================================
    # BARRA DE ENTRADA DO CHAT (CHAT INPUT OU SUGESTÃO CLICADA)
    # =========================================================================
    chat_input = st.chat_input("Digite sua pergunta sobre estoque, vendas ou rentabilidade...")
    user_query = chat_input or prompt_to_send

    if user_query:
        # Registra e exibe mensagem do usuário
        st.session_state["copilot_messages"].append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Executa ciclo ReAct com memória de thread
        with st.chat_message("assistant"):
            with st.spinner("Consultando dados no DuckDB..."):
                response_text = service.ask_copilot(
                    query=user_query,
                    thread_id=st.session_state["copilot_thread_id"],
                )
                st.markdown(response_text)

        st.session_state["copilot_messages"].append({"role": "assistant", "content": response_text})
        st.rerun()

