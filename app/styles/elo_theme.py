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

        /* Transição em mensagens do chat */
        [data-testid="stChatMessage"] {
            animation: fadeIn 0.15s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        /* Customização de Spinner e Carregamento no Tema da Aplicação */
        [data-testid="stSpinner"] {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 16px 0;
        }

        [data-testid="stSpinner"] i {
            border-top-color: #38BDF8 !important;
        }

        [data-testid="stSpinner"] span {
            color: #94A3B8 !important;
            font-size: 13px !important;
            font-weight: 500 !important;
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
