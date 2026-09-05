"""
tests/conftest.py
Configuração global de testes: garante execução 100% offline e determinística sem chamadas reais a APIs de LLM.
"""

import pytest
from unittest.mock import patch, MagicMock
from langchain_core.language_models.fake_chat_models import FakeListChatModel


class FakeConsultingLLM(FakeListChatModel):
    """Modelo LLM simulado para testes que gera respostas estruturadas sem custo de tokens."""
    
    def __init__(self):
        default_responses = [
            '# Relatório Executivo: Diagnóstico de Estoque\n\n## 1. Sumário Executivo\nTaxa de ruptura sob controle.\n\n## 2. Matriz de Ações por Horizonte Temporal\n### Quick Wins (30 dias)\n- Saldão controlado de descontinuados.\n- Reposição de SKUs Curva A.\n\n### Médio Prazo (60 dias)\n- Ajuste de lead times.\n\n### Longo Prazo (90 dias)\n- S&OP integrado.\n\n## 3. Top SKUs Críticos\nSKU-00185 em acompanhamento.',
            '{"approved": true, "score": 10, "feedback": "Total conformidade com os guardrails de negócio.", "corrections_needed": []}',
            'O capital total travado em descontinuados é de R$ 38.640,00, com potencial de liberação de caixa de R$ 52.450,00 com 30% de desconto.',
            'O primeiro produto listado possui custo unitário de R$ 45,00 e estoque físico no galpão.',
            'As categorias Moda e Lifestyle apresentam as maiores taxas de ruptura.',
            'Auditoria executada com sucesso no DuckDB.',
        ] * 20
        super().__init__(responses=default_responses)

    def bind_tools(self, tools, **kwargs):
        """Suporte a bind_tools para create_react_agent."""
        return self


@pytest.fixture(autouse=True)
def mock_llm_for_tests(monkeypatch):
    """Garante que nenhum teste faça chamadas remotas reais para LLMs, e-mail ou gaste tokens."""
    monkeypatch.setenv("OPENAI_API_KEY", "mock-test-key")
    monkeypatch.setenv("GEMINI_API_KEY", "mock-test-key")
    
    fake_model = FakeConsultingLLM()
    monkeypatch.setattr("src.agent.graph.get_llm", lambda: fake_model)
    monkeypatch.setattr("src.agent.copilot.get_llm", lambda: fake_model)
    monkeypatch.setattr("src.agent.service.get_llm", lambda: fake_model, raising=False)
