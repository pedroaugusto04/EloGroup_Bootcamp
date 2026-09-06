"""
app/styles/elo_theme.py
Estilos simples e limpos para o Workbench de Análise de Dados.
Foco em visualização de gráficos, métricas e tabelas sem elementos excessivos.
"""

import streamlit as st
import plotly.io as pio
import plotly.graph_objects as go


def inject_elotarget_css():
    """Injeta CSS limpo e profissional focado em visualização de dados."""
    css = """
    <style>
        /* Tipografia */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"], .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* Títulos de seção */
        .page-title {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .page-subtitle {
            font-size: 13px;
            color: #9CA3AF;
            margin-bottom: 20px;
        }

        /* Container de métricas */
        [data-testid="stMetricValue"] {
            font-size: 22px !important;
            font-weight: 700 !important;
        }

        /* Espaçamento */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }

        /* Animações e Transições Suaves */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(3px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .fade-in {
            animation: fadeIn 0.18s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        /* Transição e Estilo em mensagens do chat */
        [data-testid="stChatMessage"] {
            animation: fadeIn 0.15s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        /* Tabelas Markdown elegantes no Chat */
        [data-testid="stChatMessage"] table {
            width: 100% !important;
            border-collapse: collapse !important;
            margin: 12px 0 !important;
            font-size: 13px !important;
            background-color: #121215 !important;
            border: 1px solid #27272A !important;
            border-radius: 6px !important;
            overflow: hidden !important;
        }

        [data-testid="stChatMessage"] th {
            background-color: #18181B !important;
            color: #F3F4F6 !important;
            font-weight: 600 !important;
            padding: 9px 12px !important;
            border-bottom: 1px solid #3F3F46 !important;
            text-align: left !important;
        }

        [data-testid="stChatMessage"] td {
            padding: 8px 12px !important;
            border-bottom: 1px solid #27272A !important;
            color: #E2E8F0 !important;
        }

        [data-testid="stChatMessage"] tr:last-child td {
            border-bottom: none !important;
        }

        [data-testid="stChatMessage"] tr:hover {
            background-color: rgba(255, 255, 255, 0.03) !important;
        }

        /* Callouts / Blockquotes no Chat */
        [data-testid="stChatMessage"] blockquote {
            border-left: 3px solid #38BDF8 !important;
            background: rgba(56, 189, 248, 0.05) !important;
            padding: 8px 14px !important;
            margin: 10px 0 !important;
            border-radius: 0 6px 6px 0 !important;
            color: #E2E8F0 !important;
        }

        /* Destaques de código inline (R$ / SKUs) */
        [data-testid="stChatMessage"] code {
            font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
            font-size: 12px !important;
            background-color: #18181B !important;
            color: #38BDF8 !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
            border: 1px solid #27272A !important;
        }

        /* Subtítulos no Chat */
        [data-testid="stChatMessage"] h3 {
            font-size: 15px !important;
            font-weight: 600 !important;
            color: #F9FAFB !important;
            margin-top: 14px !important;
            margin-bottom: 6px !important;
        }

        /* Oculta o indicador padrão 'running...' no canto superior direito */
        [data-testid="stStatusWidget"], .stStatusWidget {
            display: none !important;
            visibility: hidden !important;
        }

        /* Centralização perfeita e alinhamento dos botões de ação e popovers na sidebar */
        [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] {
            align-items: center !important;
            gap: 4px !important;
        }

        [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button,
        [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            min-height: 36px !important;
            height: 36px !important;
            padding: 0 4px !important;
            font-size: 13px !important;
            border-radius: 6px !important;
            box-sizing: border-box !important;
        }

        [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button p,
        [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button p {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1 !important;
            text-align: center !important;
            font-size: 13px !important;
            font-weight: 600 !important;
        }

        /* Botão de Excluir (✕) sutil e harmonizado */
        [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button:has(p:contains("✕")),
        [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
            color: #94A3B8 !important;
        }

        [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button:hover {
            color: #F43F5E !important;
            border-color: rgba(244, 63, 94, 0.4) !important;
            background-color: rgba(244, 63, 94, 0.08) !important;
        }

        /* Spinner Global Centralizado e Elegante */
        [data-testid="stSpinner"] {
            display: flex !important;
            flex-direction: row !important;
            justify-content: center !important;
            align-items: center !important;
            gap: 12px !important;
            padding: 18px 24px !important;
            margin: 16px auto !important;
            max-width: 480px !important;
            background: rgba(15, 23, 42, 0.75) !important;
            border: 1px solid rgba(56, 189, 248, 0.25) !important;
            border-radius: 10px !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35) !important;
            backdrop-filter: blur(8px) !important;
        }

        [data-testid="stSpinner"] i {
            border-color: rgba(56, 189, 248, 0.2) !important;
            border-top-color: #38BDF8 !important;
            width: 20px !important;
            height: 20px !important;
            border-width: 2.5px !important;
        }

        [data-testid="stSpinner"] span {
            color: #E2E8F0 !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            letter-spacing: 0.3px !important;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def configure_plotly_theme():
    """Configura o tema padrão do Plotly para gráficos analíticos com alta legibilidade."""
    template = go.layout.Template()
    template.layout = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(family="Inter, sans-serif", size=12),
        xaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.08)",
            zerolinecolor="rgba(255, 255, 255, 0.15)",
        ),
        yaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.08)",
            zerolinecolor="rgba(255, 255, 255, 0.15)",
        ),
        legend=dict(
            bgcolor="rgba(0, 0, 0, 0.5)",
            borderwidth=0,
        ),
        margin=dict(l=40, r=20, t=35, b=35),
    )
    pio.templates["analytics_theme"] = template
    pio.templates.default = "analytics_theme"
