"""
app/views/v_11_agente_consultor.py
Interface de Chat Dedicada & Minimalista para o Copiloto de Estoque (Vértice Retail).
Foco em conversação analítica, consultas determinísticas no DuckDB e memória contínua persistente.
"""

import uuid
import streamlit as st
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.chat_store import CopilotChatStore
from src.agent.service import InventoryAgentService
from src.utils.formatters import sanitize_markdown_for_streamlit


def show_agente_consultor(repo: DuckDBRepository):
    """Renderiza a interface de chat minimalista para o Copiloto de Estoque com persistência."""
    service = InventoryAgentService()
    chat_store = CopilotChatStore()

    # Inicialização do ID da thread ativa
    if "copilot_thread_id" not in st.session_state:
        threads = chat_store.list_threads()
        if threads:
            st.session_state["copilot_thread_id"] = threads[0]["id"]
            thread_data = chat_store.get_thread(threads[0]["id"])
            st.session_state["copilot_messages"] = thread_data.get("messages", []) if thread_data else []
        else:
            st.session_state["copilot_thread_id"] = str(uuid.uuid4())
            st.session_state["copilot_messages"] = []

    active_thread_id = st.session_state["copilot_thread_id"]

    # Sincroniza mensagens do estado com o armazenamento persistente caso necessário
    if "copilot_messages" not in st.session_state:
        thread_data = chat_store.get_thread(active_thread_id)
        st.session_state["copilot_messages"] = thread_data.get("messages", []) if thread_data else []

    # Verificação de origem por e-mail
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
        chat_store.save_thread(active_thread_id, st.session_state["copilot_messages"], title="Auditoria de Estoque")
        service.seed_copilot(
            thread_id=active_thread_id,
            initial_message=init_context
        )

    # =========================================================================
    # CABEÇALHO DO CHAT
    # =========================================================================
    thread_info = chat_store.get_thread(active_thread_id)
    chat_title = thread_info.get("title", "Nova Conversa") if thread_info else "Nova Conversa"

    col_header, col_actions = st.columns([4, 1.2])
    with col_header:
        st.markdown(
            f"""
            <div style="margin-bottom: 8px;">
                <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #F3F4F6;">{chat_title}</h2>
                <p style="margin: 2px 0 0 0; font-size: 12px; color: #9CA3AF;">
                    Consultoria Analítica &bull; <span style="color: #10B981; font-weight: 600;">Conectado ao DuckDB</span>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_actions:
        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
        if st.button("Nova Conversa", key="btn_new_chat_header", width="stretch", help="Inicia uma nova conversa e limpa o contexto da sessão."):
            new_id = str(uuid.uuid4())
            st.session_state["copilot_thread_id"] = new_id
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
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <style>
            .sug-card-container div[data-testid="stButton"] > button {
                text-align: left !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: flex-start !important;
                justify-content: center !important;
                padding: 12px 16px !important;
                background-color: rgba(255, 255, 255, 0.02) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-radius: 8px !important;
                min-height: 74px !important;
                width: 100% !important;
                transition: all 0.2s ease-in-out !important;
            }
            .sug-card-container div[data-testid="stButton"] > button:hover {
                background-color: rgba(56, 189, 248, 0.05) !important;
                border-color: rgba(56, 189, 248, 0.35) !important;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }
            .sug-card-container div[data-testid="stButton"] > button p {
                font-size: 13px !important;
                line-height: 1.4 !important;
                margin: 0 !important;
                color: #E2E8F0 !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<p style='font-size: 11px; font-weight: 600; color: #9CA3AF; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;'>Sugestões de Análise:</p>", unsafe_allow_html=True)

        suggestions = [
            (
                "⚡ **Simular Liquidação de Moda (-30%)**\n\nCalcula liberação de caixa e margem de contribuição.",
                "Simule liquidar a categoria Moda com 30% de desconto e mostre o potencial de liberação de caixa e impacto financeiro.",
                "btn_sug_liquidation",
            ),
            (
                "📦 **Auditoria de Rupturas & Risco**\n\nIdentifica SKUs em falta e dias de cobertura crítica.",
                "Faça uma varredura na saúde do estoque identificando quais SKUs estão em ruptura ou em risco crítico de falta nos próximos dias.",
                "btn_sug_rupturas",
            ),
            (
                "🔍 **Diagnóstico 360° (SKU-00185)**\n\nInvestigação de estoque, vendas, margem e devoluções.",
                "Faça uma investigação detalhada 360° do produto SKU-00185 (Camisa Social Clássico Nude).",
                "btn_sug_sku_dive",
            ),
            (
                "⚠️ **Capital em Descontinuados**\n\nRanking de itens fora de linha com capital imobilizado.",
                "Quais são os principais SKUs descontinuados com maior capital de giro travado no estoque?",
                "btn_sug_stranded",
            ),
            (
                "📊 **Matriz Volume vs Receita Real**\n\nCurva de faturamento e produtos com maior margem.",
                "Gere a matriz de demanda e faturamento de vendas identificando os produtos com maior volume e margem de contribuição.",
                "btn_sug_demand_matrix",
            ),
            (
                "🔄 **Atrito & Devoluções Críticas**\n\nProdutos com alta devolução e frete desperdiçado.",
                "Quais produtos têm a maior taxa de devolução, principais motivos de atrito e custo de frete desperdiçado?",
                "btn_sug_returns_risk",
            ),
        ]

        st.markdown('<div class="sug-card-container">', unsafe_allow_html=True)
        for i in range(0, len(suggestions), 2):
            c1, c2 = st.columns(2)
            with c1:
                label_1, prompt_1, key_1 = suggestions[i]
                if st.button(label_1, key=key_1, use_container_width=True):
                    prompt_to_send = prompt_1
            with c2:
                if i + 1 < len(suggestions):
                    label_2, prompt_2, key_2 = suggestions[i + 1]
                    if st.button(label_2, key=key_2, use_container_width=True):
                        prompt_to_send = prompt_2
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # HISTÓRICO DE CONVERSAÇÃO (MENSAGENS)
    # =========================================================================
    for msg in st.session_state["copilot_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(sanitize_markdown_for_streamlit(msg["content"]))

    # =========================================================================
    # BARRA DE ENTRADA DO CHAT (CHAT INPUT OU SUGESTÃO CLICADA)
    # =========================================================================
    chat_input = st.chat_input("Digite sua pergunta sobre estoque, vendas ou rentabilidade...")
    user_query = chat_input or prompt_to_send

    if user_query:
        past_history = list(st.session_state.get("copilot_messages", []))
        st.session_state["copilot_messages"].append({"role": "user", "content": user_query})
        chat_store.save_thread(active_thread_id, st.session_state["copilot_messages"])
        with st.chat_message("user"):
            st.markdown(user_query)

        # Executa ciclo ReAct com memória de thread e histórico contextual recente
        with st.chat_message("assistant"):
            with st.spinner("Consultando dados..."):
                response_text = service.ask_copilot(
                    query=user_query,
                    thread_id=active_thread_id,
                    history=past_history,
                )
                safe_response = sanitize_markdown_for_streamlit(response_text)
                st.markdown(safe_response)

        st.session_state["copilot_messages"].append({"role": "assistant", "content": safe_response})
        chat_store.save_thread(active_thread_id, st.session_state["copilot_messages"])
        st.rerun()
