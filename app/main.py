"""
app/main.py
Streamlit entrypoint: Workbench de Análise Exploratória de Dados.
Painel focado exclusivamente em visualização, métricas agregadas e gráficos por temas.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from app.styles.elo_theme import inject_elotarget_css, configure_plotly_theme
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.preprocessor import DataPreprocessor

# Import das visualizações analíticas por tema
from app.views.v_01_visao_geral import show_visao_geral
from app.views.v_02_vendas_margem import show_vendas_margem
from app.views.v_03_marketing import show_marketing
from app.views.v_04_estoque import show_estoque
from app.views.v_05_clientes import show_clientes
from app.views.v_06_atendimento import show_atendimento


st.set_page_config(
    page_title="Data Analytics Vértice",
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

    # Sidebar Simples e Direta
    st.sidebar.markdown("### Análise de Dados")
    st.sidebar.markdown("<p style='font-size: 12px; color: #9CA3AF; margin-top: -10px;'>Painel de Exploração & Gráficos</p>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    paginas = {
        "1. Visão Geral & Métricas": show_visao_geral,
        "2. Vendas & Margem": show_vendas_margem,
        "3. Marketing & Mídia": show_marketing,
        "4. Estoque & Operações": show_estoque,
        "5. Base de Clientes (RFM)": show_clientes,
        "6. Atendimento & Suporte": show_atendimento,
    }

    escolha = st.sidebar.radio("Selecione o Tema:", list(paginas.keys()), index=0)

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size: 11px; color: #71717A;">
            <b>Motor:</b> DuckDB OLAP<br>
            <b>Fonte:</b> Parquet Local<br>
            <b>Status:</b> 5 Tabelas Conectadas
        </div>
        """,
        unsafe_allow_html=True
    )

    view_fn = paginas[escolha]
    view_fn(repo)


if __name__ == "__main__":
    main()
