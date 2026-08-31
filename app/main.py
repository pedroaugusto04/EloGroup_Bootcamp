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
from app.views.v_05_hipotese_clientes import show_hipotese_clientes
from app.views.v_06_hipotese_atendimento import show_hipotese_atendimento
from app.views.v_07_hipotese_decisao_gestao import show_hipotese_decisao_gestao
from app.views.v_08_plano_estrategico import show_plano_estrategico


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

    # Sidebar Estruturada e Executiva
    st.sidebar.markdown("### Vértice Analytics")
    st.sidebar.markdown("<p style='font-size: 12px; color: #9CA3AF; margin-top: -10px;'>Diagnóstico Estratégico & Decisão</p>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    paginas = {
        "1. Visão Geral & Métricas": show_visao_geral,
        "2. Vendas & Margem": show_vendas_margem,
        "3. Marketing & Mídia": show_marketing,
        "4. Estoque & Operações": show_estoque,
        "5. Hipótese 4: Atendimento & Sintomas": show_hipotese_atendimento,
        "6. Hipótese 5: Segmentação de Clientes": show_hipotese_clientes,
        "7. Hipótese 6: Decisão Baseada em Dados": show_hipotese_decisao_gestao,
        "8. Matriz Priorização & Roadmap 30-60-90": show_plano_estrategico,
    }

    escolha = st.sidebar.radio("Navegue pelos Módulos:", list(paginas.keys()), index=0)

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
