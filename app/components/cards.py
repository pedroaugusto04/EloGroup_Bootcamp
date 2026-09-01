"""
app/components/cards.py
Componentes visuais reutilizáveis para dashboards executivos.
Padrão Corporativo Preto e Branco (EloGroup Business Standard).
"""

import textwrap
import streamlit as st
from typing import Optional


def render_header(title: str, subtitle: str, badge_text: str = "EloGroup Consulting Lab", badge_type: str = "badge-neutral"):
    """Renderiza cabeçalho executivo corporativo da consultoria."""
    st.markdown(
        textwrap.dedent(f"""
        <div class="elo-header">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <h1 class="elo-title">{title}</h1>
                <span class="elo-badge {badge_type}">{badge_text}</span>
            </div>
            <p class="elo-subtitle">{subtitle}</p>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, subtext: str = "", delta: Optional[str] = None, delta_type: str = "badge-neutral"):
    """Renderiza card de KPI executivo com tipografia sóbria e suporte a delta."""
    delta_html = f'<span class="elo-badge {delta_type}" style="margin-left: 8px;">{delta}</span>' if delta else ""
    st.markdown(
        textwrap.dedent(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value} {delta_html}</div>
            <div class="kpi-subtext">{subtext}</div>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )


def render_insight_box(title: str, text: str, icon: str = ""):
    """Renderiza caixa de insight analítico/consultivo com destaque executivo."""
    icon_html = f"{icon} " if icon else ""
    st.markdown(
        textwrap.dedent(f"""
        <div class="insight-box">
            <div class="insight-title">{icon_html}{title}</div>
            <p class="insight-text">{text}</p>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )


def render_action_card(horizon: str, title: str, content_html: str, dot_color: str = "#10B981"):
    """Renderiza card de recomendação/ação sóbrio com uma discreta bolinha indicadora."""
    clean_body = textwrap.dedent(content_html).strip()
    html = textwrap.dedent(f"""
    <div style="background-color: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 18px; height: 100%;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: {dot_color}; flex-shrink: 0;"></span>
            <span style="font-size: 12px; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;">{horizon}</span>
        </div>
        <div style="font-size: 15px; font-weight: 600; color: #F1F5F9; margin-bottom: 10px;">{title}</div>
        <div style="font-size: 13px; color: #94A3B8; line-height: 1.6;">
            {clean_body}
        </div>
    </div>
    """).strip()
    st.markdown(html, unsafe_allow_html=True)


def render_summary_banner(title: str, content_html: str, dot_color: str = "#94A3B8"):
    """Renderiza banner de síntese executiva com estilo sóbrio corporativo."""
    clean_body = textwrap.dedent(content_html).strip()
    html = textwrap.dedent(f"""
    <div style="background-color: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 16px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: {dot_color}; flex-shrink: 0;"></span>
            <span style="font-size: 12px; font-weight: 600; color: #CBD5E1; text-transform: uppercase; letter-spacing: 0.5px;">{title}</span>
        </div>
        <div style="font-size: 13px; color: #94A3B8; line-height: 1.6;">
            {clean_body}
        </div>
    </div>
    """).strip()
    st.markdown(html, unsafe_allow_html=True)


