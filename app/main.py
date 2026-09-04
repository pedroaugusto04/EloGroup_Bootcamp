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


st.set_page_config(
    page_title="Vértice Analytics - Workbench & Auditoria",
    page_icon="🔍",
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
    st.sidebar.markdown("### 🔍 Vértice Workbench")
    st.sidebar.markdown("<p style='font-size: 12px; color: #9CA3AF; margin-top: -10px;'>Auditoria & Desenvolvimento</p>", unsafe_allow_html=True)
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

    escolha = st.sidebar.radio("Selecione a Etapa da Análise:", list(paginas.keys()), index=0)

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size: 11px; color: #71717A;">
            <b>Alinhamento:</b> DEVELOPMENT.md<br>
            <b>Motor:</b> DuckDB OLAP (5 Tabelas)<br>
            <b>Modo:</b> Auditoria & Diagnóstico
        </div>
        """,
        unsafe_allow_html=True
    )

    view_fn = paginas[escolha]
    view_fn(repo)


if __name__ == "__main__":
    main()
