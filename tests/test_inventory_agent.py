"""
tests/test_inventory_agent.py
Suíte de testes automatizados para o Agente de Estoque (LangGraph: Planejamento + Reflexão).
"""

import json
import pytest
from src.infrastructure.database import DuckDBRepository
from src.agent.tools import (
    tool_inventory_health_scan,
    tool_sales_demand_matrix,
    tool_marketing_stock_mismatch,
    tool_returns_and_quality_risk,
    tool_discontinued_stranded_capital,
    tool_sku_deep_dive,
    tool_simulate_inventory_liquidation,
)
from src.agent.graph import (
    _extract_json,
    _validate_critic_payload,
    build_inventory_agent_graph,
    critic_node,
    InventoryAgentState,
)
from src.agent.service import InventoryAgentService


def test_tool_inventory_health_scan():
    raw = tool_inventory_health_scan.invoke({"limit": 10})
    data = json.loads(raw)
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "sku_id" in first
    assert "estoque_disponivel" in first
    assert "dias_cobertura" in first
    assert "diagnostico_operacional" in first


def test_tool_sales_demand_matrix():
    raw = tool_sales_demand_matrix.invoke({"top_n": 5})
    data = json.loads(raw)
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "receita_liquida_total" in first
    assert "margem_unit_media" in first
    assert "unidades_vendidas" in first


def test_tool_marketing_stock_mismatch():
    raw = tool_marketing_stock_mismatch.invoke({})
    data = json.loads(raw)
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "categoria" in first
    assert "taxa_ruptura_pct" in first
    assert "status_alinhamento" in first


def test_tool_returns_and_quality_risk():
    raw = tool_returns_and_quality_risk.invoke({"min_orders": 5, "min_returns": 1})
    data = json.loads(raw)
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "taxa_devolucao_pct" in first
    assert "principal_motivo_devolucao" in first


def test_tool_discontinued_stranded_capital():
    raw = tool_discontinued_stranded_capital.invoke({"limit": 5})
    data = json.loads(raw)
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "capital_travado_real" in first
    assert "custo_unitario_avaliado" in first


def test_tool_sku_deep_dive():
    raw_ok = tool_sku_deep_dive.invoke({"sku_id": "SKU-00185"})
    data_ok = json.loads(raw_ok)
    assert data_ok["sku_id"] == "SKU-00185"
    assert "estoque_disponivel" in data_ok

    raw_err = tool_sku_deep_dive.invoke({"sku_id": "SKU-INEXISTENTE-999"})
    data_err = json.loads(raw_err)
    assert "error" in data_err


def test_inventory_agent_graph_execution():
    graph = build_inventory_agent_graph()
    initial_state: InventoryAgentState = {
        "mission": "Auditar a saúde de estoque da Vértice Retail e gerar recomendações 30/60/90 dias.",
        "plan": [],
        "current_step_index": 0,
        "observations": [],
        "draft_report": None,
        "critic_feedback": None,
        "critic_approved": False,
        "critic_reviewed": False,
        "revision_count": 0,
        "final_report": None,
        "structured_data": None,
    }
    result = graph.invoke(initial_state)
    assert len(result["plan"]) == 4
    assert all(step["status"] == "completed" for step in result["plan"])
    assert result["final_report"] is not None
    assert len(result["final_report"]) > 20



def test_critic_payload_requires_complete_schema():
    valid = {
        "approved": True,
        "score": 9,
        "feedback": "Relatório consistente.",
        "corrections_needed": [],
    }
    assert _validate_critic_payload(valid) == valid
    assert _validate_critic_payload({"approved": True, "score": 9}) is None
    assert _validate_critic_payload({**valid, "approved": "true"}) is None
    assert _extract_json("Resposta: {\"approved\": true}") == {"approved": True}


def test_critic_repairs_invalid_json_once(monkeypatch):
    class FakeResponse:
        def __init__(self, content):
            self.content = content

    class FakeLLM:
        def __init__(self):
            self.responses = [
                FakeResponse("Aprovo a minuta."),
                FakeResponse("{\"approved\": true, \"score\": 9, \"feedback\": \"Guardrails atendidos.\", \"corrections_needed\": []}"),
            ]
            self.calls = 0

        def invoke(self, _messages):
            self.calls += 1
            return self.responses.pop(0)

    llm = FakeLLM()
    monkeypatch.setattr("src.agent.graph.get_llm", lambda: llm)
    monkeypatch.setattr("src.agent.nodes.get_llm", lambda: llm)
    monkeypatch.setattr("src.infrastructure.llm.get_llm", lambda: llm)
    state = {
        "draft_report": "## Quick Wins\nAção em 30 dias.",
        "structured_data": {"ruptura_count": 1},
        "revision_count": 0,
    }

    result = critic_node(state)

    assert llm.calls == 2
    assert result["critic_reviewed"] is True
    assert result["critic_approved"] is True
    assert result["final_report"] == state["draft_report"]


def test_critic_guardrail_rejection():
    # Minuta simulada com violação de guardrail (sugerindo compra de descontinuado)
    state: InventoryAgentState = {
        "mission": "Teste de Guardrails",
        "plan": [],
        "current_step_index": 4,
        "observations": [],
        "draft_report": "Recomendamos comprar descontinuado SKU-00185 imediatamente.",
        "critic_feedback": None,
        "critic_approved": False,
        "critic_reviewed": False,
        "revision_count": 0,
        "final_report": None,
        "structured_data": {},
    }
    critic_res = critic_node(state)
    assert critic_res["critic_approved"] is False
    assert "Violação Guardrail 1" in critic_res["critic_feedback"]



def test_inventory_agent_service():
    service = InventoryAgentService()
    result = service.run_diagnostic()
    assert "structured_data" in result
    assert result["structured_data"]["total_stranded_cash"] > 0
    assert result["final_report"] is not None


def test_tool_simulate_inventory_liquidation():
    raw_all = tool_simulate_inventory_liquidation.invoke({"desconto_pct": 30.0})
    data_all = json.loads(raw_all)
    assert "total_skus_descontinuados" in data_all
    assert data_all["total_skus_descontinuados"] > 0
    assert data_all["capital_imobilizado_custo_total"] > 0
    assert data_all["caixa_destravado_projetado_total"] > 0

    raw_moda = tool_simulate_inventory_liquidation.invoke({"categoria": "Moda", "desconto_pct": 40.0})
    data_moda = json.loads(raw_moda)
    assert data_moda["categoria"] == "Moda"
    assert data_moda["desconto_aplicado_pct"] == 40.0


def test_inventory_copilot_queries():
    from src.agent.copilot import InventoryCopilot
    copilot = InventoryCopilot()

    ans = copilot.ask("Quais categorias possuem maior taxa de ruptura de estoque?", thread_id="t_query_1")
    assert len(ans) > 20


def test_inventory_copilot_react_multiturn_memory():
    from src.agent.copilot import InventoryCopilot
    copilot = InventoryCopilot()
    thread_id = "test_memory_session_123"

    # Turno 1
    r1 = copilot.ask("Quais são os 3 SKUs com maior capital travado em descontinuados?", thread_id=thread_id)
    assert len(r1) > 20

    # Turno 2 (Follow-up contextual utilizando memória do Turno 1)
    r2 = copilot.ask("Qual o custo unitário do primeiro deles?", thread_id=thread_id)
    assert len(r2) > 10


def test_service_ask_copilot_integration():
    service = InventoryAgentService()
    resp = service.ask_copilot("Qual o capital travado em descontinuados?", thread_id="t_integration_1")
    assert len(resp) > 20


def test_copilot_seed_conversation_memory():
    service = InventoryAgentService()
    thread_id = "test_seeded_thread_999"
    email_context = "Auditoria Semanal: O capital travado em descontinuados é de R$ 38.640,00 e o potencial de caixa é de R$ 52.450,00."
    service.seed_copilot(thread_id=thread_id, initial_message=email_context)

    # Pergunta de follow-up que depende diretamente do e-mail inicial semeado
    followup_resp = service.ask_copilot("Qual foi o capital travado citado no relatório?", thread_id=thread_id)
    assert len(followup_resp) > 10



