"""
src/utils/formatters.py
Funções utilitárias de formatação monetária, percentual e sanitização de markdown.
"""

import re
from typing import Union


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
    Sanitiza blocos de markdown que possam conter sintaxes propensas a falha no frontend
    (como diagramas mermaid malformados gerados por LLM).
    """
    if not isinstance(content, str):
        return ""
    # Converte blocos ```mermaid para blocos de código ```text seguros
    sanitized = re.sub(r"```mermaid\s*([\s\S]*?)\s*```", r"```text\n\1\n```", content, flags=re.IGNORECASE)
    return sanitized
