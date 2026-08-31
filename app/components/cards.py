"""
app/components/cards.py
Componentes visuais reutilizáveis para dashboards executivos.
Padrão Corporativo Preto e Branco (EloGroup Business Standard).
"""

import streamlit as st
from typing import Optional


def render_header(title: str, subtitle: str, badge_text: str = "EloGroup Consulting Lab", badge_type: str = "badge-neutral"):
    """Renderiza cabeçalho executivo corporativo da consultoria."""
    st.markdown(
        f"""
        <div class="elo-header">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <h1 class="elo-title">{title}</h1>
                <span class="elo-badge {badge_type}">{badge_text}</span>
            </div>
            <p class="elo-subtitle">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, subtext: str = "", delta: Optional[str] = None, delta_type: str = "badge-neutral"):
    """Renderiza card de KPI executivo com tipografia sóbria e suporte a delta."""
    delta_html = f'<span class="elo-badge {delta_type}" style="margin-left: 8px;">{delta}</span>' if delta else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value} {delta_html}</div>
            <div class="kpi-subtext">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_box(title: str, text: str, icon: str = ""):
    """Renderiza caixa de insight analítico/consultivo com destaque executivo."""
    icon_html = f"{icon} " if icon else ""
    st.markdown(
        f"""
        <div class="insight-box">
            <div class="insight-title">{icon_html}{title}</div>
            <p class="insight-text">{text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
