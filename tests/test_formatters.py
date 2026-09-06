import pytest
from unittest.mock import patch
from src.utils.formatters import (
    format_currency_brl,
    format_percentage,
    sanitize_markdown_for_streamlit,
    render_message_with_mermaid,
    render_mermaid_diagram,
)


def test_format_currency_brl():
    assert format_currency_brl(1234.56) == "R$ 1.234,56"
    assert format_currency_brl(0) == "R$ 0,00"
    assert format_currency_brl(None) == "R$ 0,00"


def test_format_percentage():
    assert format_percentage(12.5) == "12,5%"
    assert format_percentage(0) == "0,0%"
    assert format_percentage(None) == "0,0%"


@patch("src.utils.formatters.components")
@patch("src.utils.formatters.st")
def test_render_message_with_mermaid_fenced(mock_st, mock_components):
    content = """Aqui está o plano:

```mermaid
timeline
    title Estratégia de Recuperação Vértice Retail
    section 30 Dias: Quick Wins
        Liquidação de Descontinuados : Foco nos Top 5 de Moda para gerar caixa imediato.
        Pedidos de Emergência : Reposição imediata dos 5 SKUs críticos de Beleza.
```

E a conclusão final."""

    render_message_with_mermaid(content)

    assert mock_st.markdown.call_count == 2
    assert mock_components.html.call_count == 1
    html_arg = mock_components.html.call_args[0][0]
    assert "mermaid" in html_arg
    assert "Estratégia de Recuperação" in html_arg


@patch("src.utils.formatters.components")
@patch("src.utils.formatters.st")
def test_render_message_with_mermaid_raw_timeline(mock_st, mock_components):
    content = """timeline
    title Estratégia de Recuperação Vértice Retail
    section 30 Dias: Quick Wins
        Liquidação de Descontinuados : Foco nos Top 5 de Moda para gerar caixa imediato."""

    render_message_with_mermaid(content)

    assert mock_components.html.call_count == 1
    html_arg = mock_components.html.call_args[0][0]
    assert "timeline" in html_arg
    assert "Liquidação de Descontinuados" in html_arg

