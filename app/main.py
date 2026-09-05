"""
app/main.py
Streamlit entrypoint: Workbench de Análise Exploratória de Dados.
Painel focado exclusivamente em visualização, métricas agregadas e gráficos por temas.
"""

import sys
import uuid
import logging
from pathlib import Path

# Configuração de logging padrão para saída em stdout (Docker logs)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from app.styles.elo_theme import inject_elotarget_css, configure_plotly_theme
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.preprocessor import DataPreprocessor
from src.infrastructure.chat_store import CopilotChatStore

# Import das visualizações analíticas alinhadas ao DEVELOPMENT.md
from app.views.v_09_dispersao_outliers import show_dispersao_outliers
from app.views.v_01_visao_geral import show_visao_geral
from app.views.v_02_vendas_margem import show_vendas_margem
from app.views.v_03_marketing import show_marketing
from app.views.v_04_estoque import show_estoque
from app.views.v_05_clientes import show_clientes
from app.views.v_06_atendimento import show_atendimento
from app.views.v_10_analise_relacional import show_analise_relacional
from app.views.v_06_hipotese_atendimento import show_hipotese_atendimento
from app.views.v_05_hipotese_clientes import show_hipotese_clientes
from app.views.v_07_hipotese_decisao_gestao import show_hipotese_decisao_gestao
from app.views.v_08_plano_estrategico import show_plano_estrategico
from app.views.v_11_agente_consultor import show_agente_consultor


st.set_page_config(
    page_title="Vértice Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_elotarget_css()
configure_plotly_theme()


@st.cache_resource
def get_repository() -> DuckDBRepository:
    from src.config import PROCESSED_DATA_DIR
    if not (PROCESSED_DATA_DIR / "vendas.parquet").exists():
        preprocessor = DataPreprocessor()
        preprocessor.run_all()
    return DuckDBRepository()


def main():
    repo = get_repository()

    # Sidebar Estruturada e Alinhada com DEVELOPMENT.md
    st.sidebar.markdown("### Vértice Analytics")
    st.sidebar.markdown("<p style='font-size: 12px; color: #9CA3AF; margin-top: -10px;'>Workbench de Análise & Auditoria</p>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    paginas = {
        "2. Outliers & Dispersão (Tukey IQR)": show_dispersao_outliers,
        "3.0 Visão Geral & KPIs Macro": show_visao_geral,
        "3.1 Vendas & Decomposição Margem": show_vendas_margem,
        "3.2 Marketing & Canais de Mídia": show_marketing,
        "3.3 Estoque & Ruptura vs Excesso": show_estoque,
        "3.4 Clientes & Perfil Cadastral": show_clientes,
        "3.5 Atendimento & Canais de Suporte": show_atendimento,
        "4. Integridade entre Bases (Auditoria)": show_analise_relacional,
        "5.1 Hipótese 4: Atendimento & IA": show_hipotese_atendimento,
        "5.2 Hipótese 5: Segmentação de Clientes": show_hipotese_clientes,
        "5.3 Hipótese 6: Decisão de Gestão & Estoque": show_hipotese_decisao_gestao,
        "6. Plano de Ação (30/60/90 Dias)": show_plano_estrategico,
    }

    query_view = st.query_params.get("view", "")

    # Se estiver em modo Copiloto (Deep Link do E-mail ou Botão)
    if query_view in ["agente_consultor", "agent", "copiloto", "estoque", "7"]:
        chat_store = CopilotChatStore()

        st.sidebar.markdown("### Copiloto de Estoque")
        st.sidebar.markdown("<p style='font-size: 12px; color: #38BDF8; margin-top: -10px;'>Consultoria & Diagnóstico</p>", unsafe_allow_html=True)
        
        # Botão Nova Conversa
        if st.sidebar.button("+ Nova Conversa", key="sidebar_new_chat_btn", type="primary", width="stretch", help="Inicia uma nova conversa do zero."):
            new_thread_id = str(uuid.uuid4())
            st.session_state["copilot_thread_id"] = new_thread_id
            st.session_state["copilot_messages"] = []
            st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.markdown("<p style='font-size: 11px; font-weight: 600; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px;'>Histórico de Conversas</p>", unsafe_allow_html=True)

        threads = chat_store.list_threads()
        active_id = st.session_state.get("copilot_thread_id")

        if threads:
            for thread in threads:
                t_id = thread["id"]
                t_title = thread["title"]
                t_count = thread["message_count"]
                is_active = (t_id == active_id)

                prefix = "• " if not is_active else "► "
                btn_label = f"{prefix}{t_title}"
                
                col_thread, col_del = st.sidebar.columns([4, 1])
                with col_thread:
                    if st.button(
                        btn_label,
                        key=f"thread_btn_{t_id}",
                        width="stretch",
                        help=f"Abrir conversa ({t_count} mensagens)"
                    ):
                        st.session_state["copilot_thread_id"] = t_id
                        thread_data = chat_store.get_thread(t_id)
                        st.session_state["copilot_messages"] = thread_data.get("messages", []) if thread_data else []
                        st.rerun()
                with col_del:
                    if st.button("✕", key=f"del_thread_{t_id}", help="Excluir esta conversa"):
                        chat_store.delete_thread(t_id)
                        if t_id == active_id:
                            st.session_state["copilot_thread_id"] = str(uuid.uuid4())
                            st.session_state["copilot_messages"] = []
                        st.rerun()
        else:
            st.sidebar.caption("Nenhuma conversa salva ainda.")

        st.sidebar.markdown("---")
        if st.sidebar.button("Voltar ao Workbench", key="sidebar_back_workbench_btn", width="stretch", help="Retorna ao painel completo de gráficos e auditoria analítica."):
            st.query_params.clear()
            st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.markdown(
            """
            <div style="font-size: 11px; color: #71717A; line-height: 1.6;">
                <b>Arquitetura:</b> ReAct com Memória<br>
                <b>Persistência:</b> Histórico Local (JSON)<br>
                <b>Base de Dados:</b> DuckDB OLAP (2026)<br>
                <b>Status:</b> <span style="color: #10B981;">Conectado</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        show_agente_consultor(repo)
        return

    # Modo Normal do Workbench
    escolha = st.sidebar.radio("Selecione a Etapa da Análise:", list(paginas.keys()), index=0)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Rotinas de Auditoria")
    st.sidebar.caption("Auditoria periódica de estoque e notificação.")

    periodo_opcao = st.sidebar.selectbox(
        "Janela de Vendas Analisada:",
        [
            "Ano Fechado 2023 (12 meses - Recomendado)",
            "Últimos 90 Dias (Q4 2023 - Tático)",
            "Primeiro Semestre 2023 (H1)",
            "Segundo Semestre 2023 (H2)",
            "Todo o Histórico (2023 - 2024)",
        ],
        index=0,
        help="Define o recorte temporal de vendas para cálculo do giro diário, cobertura física e faturamento."
    )

    if "Ano Fechado" in periodo_opcao:
        audit_date_filter = "AND data_pedido >= '2023-01-01' AND data_pedido <= '2023-12-31'"
        audit_days_window = 365.0
        audit_period_label = "Ano Fechado 2023"
    elif "Últimos 90 Dias" in periodo_opcao:
        audit_date_filter = "AND data_pedido >= '2023-10-01' AND data_pedido <= '2023-12-31'"
        audit_days_window = 92.0
        audit_period_label = "Últimos 90 Dias (Q4 2023)"
    elif "Primeiro Semestre" in periodo_opcao:
        audit_date_filter = "AND data_pedido >= '2023-01-01' AND data_pedido <= '2023-06-30'"
        audit_days_window = 181.0
        audit_period_label = "Primeiro Semestre 2023 (H1)"
    elif "Segundo Semestre" in periodo_opcao:
        audit_date_filter = "AND data_pedido >= '2023-07-01' AND data_pedido <= '2023-12-31'"
        audit_days_window = 184.0
        audit_period_label = "Segundo Semestre 2023 (H2)"
    else:
        audit_date_filter = ""
        audit_days_window = 391.0
        audit_period_label = "Todo o Histórico (2023-2024)"

    from src.agent.worker import run_autonomous_inventory_audit

    if st.sidebar.button("Executar Auditoria & Enviar E-mail", type="primary", width="stretch", help="Executa a auditoria de estoque imediatamente e dispara o e-mail executivo via Resend."):
        with st.sidebar.status(f"Auditando estoque ({audit_period_label})...", expanded=True) as status_box:
            status_box.write("Processando cruzamento no DuckDB...")
            res = run_autonomous_inventory_audit(
                send_email=True,
                date_filter=audit_date_filter,
                days_window=audit_days_window,
                period_label=audit_period_label,
            )
            email_res = res.get("email_result") or {}
            if email_res.get("status") == "sent":
                status_box.update(label=f"Auditoria ({audit_period_label}) concluída e e-mail enviado.", state="complete", expanded=False)
                st.sidebar.success(f"E-mail enviado via Resend para `{email_res.get('to')}`.")
            elif email_res.get("status") == "simulated":
                status_box.update(label=f"Auditoria ({audit_period_label}) concluída (Modo Simulação).", state="complete", expanded=False)
                st.sidebar.info(f"{email_res.get('message')}")
            else:
                status_box.update(label="Auditoria finalizada com aviso.", state="error", expanded=False)
                st.sidebar.warning(f"{email_res.get('error', 'Status indefinido')}")

    if st.sidebar.button("Abrir Copiloto de Estoque", width="stretch", help="Abre a interface conversacional do Copiloto de Estoque com memória."):
        st.query_params["view"] = "agent"
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size: 11px; color: #71717A;">
            <b>Alinhamento:</b> DEVELOPMENT.md<br>
            <b>Motor:</b> DuckDB OLAP (5 Tabelas)<br>
            <b>Ano Base:</b> 2026
        </div>
        """,
        unsafe_allow_html=True
    )

    view_fn = paginas[escolha]
    view_fn(repo)


if __name__ == "__main__":
    main()
