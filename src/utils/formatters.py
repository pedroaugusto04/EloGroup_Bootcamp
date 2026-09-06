"""
src/utils/formatters.py
Funções utilitárias de formatação monetária, percentual e renderização de markdown com suporte a diagramas Mermaid.
"""

import re
from typing import Union, Optional
import streamlit as st
import streamlit.components.v1 as components


def format_currency_brl(value: Union[int, float, None], decimals: int = 2) -> str:
    """Formata um valor numérico para o padrão de moeda brasileira (R$ 1.234,56)."""
    if value is None:
        return "R$ 0,00"
    try:
        val = float(value)
        formatted = f"{val:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"
    except (ValueError, TypeError):
        return "R$ 0,00"


def format_percentage(value: Union[int, float, None], decimals: int = 1) -> str:
    """Formata um valor decimal ou percentual para formato legível (ex: 12,5%)."""
    if value is None:
        return "0,0%"
    try:
        val = float(value)
        formatted = f"{val:.{decimals}f}".replace(".", ",")
        return f"{formatted}%"
    except (ValueError, TypeError):
        return "0,0%"


def sanitize_markdown_for_streamlit(content: str) -> str:
    """
    Higieniza strings de markdown preservando formatações e blocos de código.
    """
    if not isinstance(content, str):
        return ""
    return content.strip()


def render_mermaid_diagram(code: str, height: Optional[int] = None) -> None:
    """
    Renderiza um diagrama Mermaid interativo embutido no Streamlit com tema Dark harmonizado.
    Suporta timelines, diagramas de fluxo, gráficos de Gantt e matrizes.
    """
    clean_code = code.strip()
    # Se o bloco não contiver um comando inicial reconhecido, mas tiver sintaxe de timeline:
    known_keywords = (
        "timeline", "gantt", "graph", "flowchart", "sequenceDiagram",
        "pie", "journey", "classDiagram", "stateDiagram", "erDiagram",
        "mindmap", "quadrantChart", "C4Context"
    )
    if not any(clean_code.startswith(kw) for kw in known_keywords):
        if "section " in clean_code or "title " in clean_code:
            clean_code = f"timeline\n{clean_code}"

    line_count = len(clean_code.splitlines())
    calc_height = height or max(200, min(650, line_count * 36 + 80))
    container_id = f"mermaid_{abs(hash(clean_code)) % 1000000}"

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 8px 4px;
                background-color: transparent;
                color: #F3F4F6;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                overflow: auto;
            }}
            .mermaid-card {{
                width: 100%;
                background: #0B1329;
                border: 1px solid rgba(56, 189, 248, 0.25);
                border-radius: 8px;
                padding: 16px 12px;
                box-sizing: border-box;
                display: flex;
                justify-content: center;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
            }}
            .mermaid {{
                width: 100%;
                display: flex;
                justify-content: center;
            }}
            svg {{
                max-width: 100% !important;
                height: auto !important;
            }}
        </style>
    </head>
    <body>
        <div class="mermaid-card">
            <div class="mermaid" id="{container_id}">
{clean_code}
            </div>
        </div>
        <script>
            try {{
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'dark',
                    securityLevel: 'loose',
                    themeVariables: {{
                        darkMode: true,
                        background: '#0B1329',
                        primaryColor: '#0284C7',
                        primaryTextColor: '#F3F4F6',
                        primaryBorderColor: '#38BDF8',
                        lineColor: '#94A3B8',
                        secondaryColor: '#1E293B',
                        tertiaryColor: '#0F172A'
                    }}
                }});
            }} catch (err) {{
                console.error("Mermaid error:", err);
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=calc_height, scrolling=True)


def render_message_with_mermaid(content: str) -> None:
    """
    Renderiza o conteúdo completo de uma mensagem no Streamlit, identificando e plotando
    visualmente diagramas Mermaid (como timelines de 30/60/90 dias) e textos Markdown adjacentes.
    """
    if not content:
        return

    # 1. Padrão para blocos delimitados ```mermaid ou ```timeline
    pattern = re.compile(r"```(?:mermaid|timeline)\s*([\s\S]*?)\s*```", re.IGNORECASE)
    matches = list(pattern.finditer(content))

    if matches:
        last_end = 0
        for match in matches:
            before_text = content[last_end:match.start()].strip()
            if before_text:
                st.markdown(before_text)

            diagram_code = match.group(1).strip()
            if "timeline" in match.group(0).lower() and not diagram_code.lower().startswith("timeline"):
                diagram_code = f"timeline\n{diagram_code}"

            render_mermaid_diagram(diagram_code)
            last_end = match.end()

        after_text = content[last_end:].strip()
        if after_text:
            st.markdown(after_text)
        return

    # 2. Padrão para diagramas raw iniciados com 'timeline' sem backticks
    raw_timeline_pattern = re.compile(
        r"(?:^|\n)(timeline\s*\n[\s\S]*?)(?=(?:\n\n[A-Z#*])|\Z)",
        re.MULTILINE
    )
    raw_match = raw_timeline_pattern.search(content)
    if raw_match:
        before_text = content[:raw_match.start()].strip()
        diagram_code = raw_match.group(1).strip()
        after_text = content[raw_match.end():].strip()

        if before_text:
            st.markdown(before_text)
        render_mermaid_diagram(diagram_code)
        if after_text:
            st.markdown(after_text)
        return

    # 3. Renderização direta padrão
    st.markdown(content)
