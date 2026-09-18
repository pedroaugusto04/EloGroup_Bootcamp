"""Contrato factual do copiloto de estoque."""

import json

import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage

from src.agent.inventory_analytics import (
    DataQualityError,
    build_audit_package,
    capital_coverage,
    inventory_health,
    liquidation,
    sku_deep_dive,
    data_quality,
)
from src.agent.periods import resolve_period
from src.agent.service import InventoryAgentService
from src.agent.tools import (
    tool_inventory_health_scan,
    tool_sales_demand_matrix,
    tool_returns_and_quality_risk,
    tool_discontinued_stranded_capital,
    tool_sku_deep_dive,
    tool_simulate_inventory_liquidation,
)
from src.infrastructure.database import DuckDBRepository


@pytest.fixture
def repo():
    return DuckDBRepository()


@pytest.mark.parametrize("tool,args", [
    (tool_inventory_health_scan, {"period_key": "full_history", "limit": 3}),
    (tool_sales_demand_matrix, {"period_key": "calendar_2023", "top_n": 3}),
    (tool_returns_and_quality_risk, {"period_key": "last_90d_observed", "limit": 3}),
    (tool_discontinued_stranded_capital, {"period_key": "full_history", "limit": 3}),
    (tool_sku_deep_dive, {"period_key": "full_history", "sku_id": "SKU-00185"}),
    (tool_simulate_inventory_liquidation, {"period_key": "full_history", "desconto_pct": 30}),
])
def test_all_tools_return_evidence_envelope(tool, args):
    payload = json.loads(tool.invoke(args))
    assert set(("meta", "summary", "items")) <= payload.keys()
    assert payload["meta"]["financial_source"] == "vendas"
    assert payload["meta"]["operational_source"] == "estoque"
    assert payload["meta"]["stock_as_of"] is None
    assert isinstance(payload["items"], list)


def test_periods_are_resolved_by_backend(repo):
    full = resolve_period(repo, "full_history")
    calendar = resolve_period(repo, "calendar_2023")
    last90 = resolve_period(repo, "last_90d_observed")
    assert (full.start.isoformat(), full.end.isoformat(), full.days) == ("2023-01-01", "2024-01-26", 391)
    assert (calendar.start.isoformat(), calendar.end.isoformat(), calendar.days) == ("2023-01-01", "2023-12-31", 365)
    assert last90.days == 90 and last90.end == full.end
    with pytest.raises(ValueError):
        resolve_period(repo, "full_history; DROP TABLE estoque")


def test_calendar_2023_excludes_all_january_2024_sales(repo):
    package = build_audit_package(repo, "calendar_2023")
    expected = repo.execute_sql("""
        SELECT SUM(quantidade) AS units FROM vendas
        WHERE status_pagamento = 'Aprovado'
          AND CAST(data_pedido AS DATE) BETWEEN ? AND ?
    """, ["2023-01-01", "2023-12-31"])["units"].iloc[0]
    january = repo.execute_sql("""
        SELECT SUM(quantidade) AS units FROM vendas
        WHERE status_pagamento = 'Aprovado' AND CAST(data_pedido AS DATE) >= ?
    """, ["2024-01-01"])["units"].iloc[0]
    assert package["summary"]["demand"]["unidades_aprovadas"] == expected
    assert package["summary"]["demand"]["unidades_aprovadas"] + january == pytest.approx(
        build_audit_package(repo, "full_history")["summary"]["demand"]["unidades_aprovadas"]
    )


def test_weighted_sales_cost_and_financial_coverage(repo):
    payload = capital_coverage(repo)
    capital = payload["summary"]
    assert capital["skus_com_custo_vendas"] == 4883
    assert capital["skus_sem_custo_vendas"] == 117
    assert capital["capital_fisico"] == pytest.approx(146_964_262.92, abs=0.02)
    assert capital["capital_reservado"] == pytest.approx(22_017_675.68, abs=0.02)
    assert capital["capital_disponivel"] == pytest.approx(124_946_587.24, abs=0.02)
    assert capital["capital_fisico"] == pytest.approx(
        capital["capital_reservado"] + capital["capital_disponivel"], abs=0.02
    )
    assert capital["descontinuados_valorados"] == 206
    assert capital["descontinuados_excluidos"] == 1
    assert capital["capital_disponivel_descontinuado"] == pytest.approx(6_059_540.14, abs=0.02)
    assert capital["skus_comparacao_custo"] == 4883
    assert capital["correlacao_custo_estoque_vendas"] == pytest.approx(0.005852, abs=1e-6)
    assert capital["skus_divergencia_custo_acima_25pct"] == 4295


def test_operational_queues_use_distinct_definitions(repo):
    package = build_audit_package(repo)
    op = package["summary"]["operational"]
    assert op["ruptura_atual"] == 99
    assert op["ponto_pedido"] == 701  # inclui igualdade e exige saldo positivo
    assert op["investigacao_reposicao"] == 101
    assert op["sem_venda_observada"] == 117
    assert op["alta_cobertura"] == 4549
    assert op["active_skus"] == 4793
    assert op["high_coverage_share_active_pct"] == pytest.approx(94.9092, abs=0.001)
    suppliers = package["summary"]["supplier_exposure_summary"]
    assert sum(row["skus_expostos"] for row in suppliers) == 101
    assert sum(row["margem_potencialmente_exposta"] for row in suppliers) == pytest.approx(
        package["summary"]["lead_time_exposure"]["margem_potencialmente_exposta"]
    )
    assert all(not item["is_descontinuado"] for item in package["queues"]["investigacao_reposicao"])


def test_full_inventory_scan_is_not_capped_at_current_catalog_size(repo):
    stock = repo.execute_sql("SELECT * FROM estoque")
    extra = stock.iloc[0].copy()
    extra["sku_id"] = "SKU-99999"
    stock.loc[len(stock)] = extra
    repo.conn.register("expanded_stock", stock)
    repo.conn.execute("CREATE OR REPLACE VIEW estoque AS SELECT * FROM expanded_stock")

    payload = inventory_health(repo, limit=None)

    assert len(payload["items"]) == 5001
    assert payload["summary"]["sem_venda_observada"] == 118


def test_exposure_is_small_historical_scenario_not_realized_loss(repo):
    exposure = build_audit_package(repo)["summary"]["lead_time_exposure"]
    assert exposure["skus"] == 101
    assert exposure["receita_antes_devolucao"] == pytest.approx(45_022.65, abs=1)
    assert exposure["receita_ajustada_devolucao"] == pytest.approx(38_325.30, abs=1)
    assert exposure["margem_potencialmente_exposta"] == pytest.approx(21_301.57, abs=1)
    assert "risco de ruptura" in exposure["interpretation"]


def test_liquidation_has_four_reconciled_scenarios(repo):
    payload = liquidation(repo, discount_pct=30)
    scenarios = payload["summary"]["scenarios"]
    assert [row["sell_through_pct"] for row in scenarios] == [25, 50, 75, 100]
    assert payload["summary"]["central_scenario"] == scenarios[1]
    assert scenarios[1]["unidades_cenario"] == 2 * scenarios[0]["unidades_cenario"]
    assert scenarios[1]["receita_ajustada_devolucoes"] < scenarios[1]["receita_antes_devolucoes"]
    assert scenarios[1]["capital_historico_envolvido"] == pytest.approx(3_029_770.07, abs=0.02)
    assert scenarios[1]["receita_antes_devolucoes"] - scenarios[1]["ajuste_estimado_devolucoes"] == pytest.approx(
        scenarios[1]["receita_ajustada_devolucoes"], abs=0.02
    )
    assert scenarios[1]["receita_ajustada_devolucoes"] - scenarios[1]["capital_historico_envolvido"] - scenarios[1]["frete_historico_estimado"] == pytest.approx(
        scenarios[1]["contribuicao_estimada"], abs=0.02
    )
    assert scenarios[1]["contribuicao_sobre_receita_pct"] == pytest.approx(
        scenarios[1]["contribuicao_estimada"] / scenarios[1]["receita_ajustada_devolucoes"] * 100
    )
    categories = payload["summary"]["central_by_category"]
    assert categories[0]["categoria"] == "Moda"
    for field in (
        "unidades_cenario", "capital_historico_envolvido", "receita_antes_devolucoes",
        "ajuste_estimado_devolucoes", "receita_ajustada_devolucoes",
        "frete_historico_estimado", "contribuicao_estimada",
    ):
        assert sum(row[field] for row in categories) == pytest.approx(scenarios[1][field], abs=0.02)
    assert payload["summary"]["skus_excluidos_sem_custo_ou_preco"] == 1
    with pytest.raises(ValueError):
        liquidation(repo, discount_pct=90.01)


def test_bound_category_and_sku_parameters_reject_sql(repo):
    with pytest.raises(ValueError):
        inventory_health(repo, category="Beleza'; DROP TABLE estoque; --")
    with pytest.raises(ValueError):
        sku_deep_dive(repo, "SKU-00185' OR 1=1 --")
    assert repo.execute_sql("SELECT COUNT(*) AS n FROM estoque")["n"].iloc[0] == 5000


def test_deep_dive_distinguishes_sources(repo):
    payload = sku_deep_dive(repo, "SKU-00185", "calendar_2023")
    item = payload["items"][0]
    assert item["fornecedor_id"]
    assert item["estoque_fisico"] == item["estoque_reservado"] + item["estoque_disponivel"]
    assert "lead_time_cadastral_dias" in item
    assert "custo_unitario_vendas" in item
    assert "custo_unitario_estoque_auditoria" in item


def test_service_publishes_only_deterministic_recommendations():
    result = InventoryAgentService().run_diagnostic("full_history")
    assert result["deterministic_approved"] is True
    assert result["llm_complement_status"] in ("completed", "not_used")
    assert result["final_report"].startswith("# Predictive Inventory Advisor")
    assert "## 2. Liquidação de descontinuados e liberação de caixa" in result["final_report"]
    assert "Margem de contribuição simulada" in result["final_report"]
    assert "### Sensibilidade ao sell-through" in result["final_report"]
    assert "## 5. Como os valores foram calculados" in result["final_report"]
    assert "## 4. Plano de Ação · Quick Wins e Recomendações Estruturadas" in result["final_report"]
    assert "### Cenário central por categoria" in result["final_report"]
    assert "### Fornecedores com maior margem em risco" in result["final_report"]
    matrix = result["factual_package"]["summary"]["decision_matrix"]
    assert [row["horizon"] for row in matrix] == ["30 dias", "30 dias", "60 dias", "90 dias"]
    assert all(row["evidence"] and row["decision_gate"] for row in matrix)
    if result["llm_complement_status"] == "completed":
        assert len(result["recommendations"]) > 0
        assert "Parecer Executivo do Agente" in result["final_report"] or "Recomendações Estruturadas do Agente" in result["final_report"]



def test_data_quality_registers_malformed_raw_sale(repo):
    quality = build_audit_package(repo)["summary"]["data_quality"]
    assert quality["malformed_raw_sales_rows_excluded"] == 1
    assert quality["blocking_errors"] == 0


@pytest.mark.parametrize("mutation", ["duplicate", "missing_balance", "inconsistent_balance"])
def test_inventory_quality_errors_block_publication(repo, mutation):
    stock = repo.execute_sql("SELECT * FROM estoque")
    if mutation == "duplicate":
        stock.loc[1, "sku_id"] = stock.loc[0, "sku_id"]
    elif mutation == "missing_balance":
        stock.loc[0, "estoque_disponivel"] = None
    else:
        stock.loc[0, "estoque_disponivel"] += 1
    repo.conn.register("invalid_stock", stock)
    repo.conn.execute("CREATE OR REPLACE VIEW estoque AS SELECT * FROM invalid_stock")
    with pytest.raises(DataQualityError):
        data_quality(repo)


def test_empty_typed_period_returns_friendly_warning(repo):
    repo.conn.execute("CREATE TEMP TABLE january_sales AS SELECT * FROM vendas WHERE data_pedido >= TIMESTAMP '2024-01-01'")
    repo.conn.execute("CREATE OR REPLACE VIEW vendas AS SELECT * FROM january_sales")
    payload = build_audit_package(repo, "calendar_2023")
    assert payload["summary"]["demand"]["skus"] == 0
    assert payload["summary"]["operational"]["sem_venda_observada"] == 5000
    assert any("Nenhuma venda" in warning for warning in payload["meta"]["warnings"])


def test_react_executes_a_real_simulated_tool_call(monkeypatch, repo):
    class ToolCallingModel(FakeMessagesListChatModel):
        def bind_tools(self, _tools, **_kwargs):
            return self

    calls = {"repo": 0}
    def tracked_repo():
        calls["repo"] += 1
        return repo

    model = ToolCallingModel(responses=[
        AIMessage(content="", tool_calls=[{
            "name": "tool_sku_deep_dive",
            "args": {"sku_id": "SKU-00185", "period_key": "full_history"},
            "id": "call-deep-dive-1",
            "type": "tool_call",
        }]),
        AIMessage(content="O SKU foi consultado na ferramenta determinística."),
    ])
    monkeypatch.setattr("src.agent.copilot.get_llm", lambda: model)
    monkeypatch.setattr("src.agent.tools._get_repo", tracked_repo)
    from src.agent.copilot import InventoryCopilot
    answer = InventoryCopilot().ask("Investigue o SKU-00185", thread_id="react-tool-test")
    assert calls["repo"] == 1
    assert "consultado" in answer


def test_checkpoint_memory_receives_only_new_message():
    from src.agent.copilot import InventoryCopilot

    class ExistingMemory:
        def get_tuple(self, _config):
            return object()
    class CapturingAgent:
        def __init__(self):
            self.messages = None
        def invoke(self, payload, config):
            self.messages = payload["messages"]
            return {"messages": [AIMessage(content="ok")]}

    copilot = InventoryCopilot.__new__(InventoryCopilot)
    copilot.memory = ExistingMemory()
    copilot.agent = CapturingAgent()
    answer = copilot.ask(
        "nova pergunta", thread_id="checkpoint-existing",
        history=[{"role": "user", "content": "mensagem já persistida"}],
    )
    assert answer == "ok"
    assert len(copilot.agent.messages) == 1
    assert copilot.agent.messages[0].content == "nova pergunta"


def test_critic_reflection_routing():
    from src.agent.graph import should_reflect_or_finish

    # Quando reprovado e ainda não atingiu o limite de revisões, deve refletir (voltar ao consolidator)
    state_revision_0 = {"critic_approved": False, "revision_count": 0, "critic_feedback": "Violação"}
    assert should_reflect_or_finish(state_revision_0) == "consolidator"

    state_revision_1 = {"critic_approved": False, "revision_count": 1, "critic_feedback": "Violação"}
    assert should_reflect_or_finish(state_revision_1) == "consolidator"

    # Quando atinge o limite (2), encerra com finish
    state_revision_2 = {"critic_approved": False, "revision_count": 2, "critic_feedback": "Violação"}
    assert should_reflect_or_finish(state_revision_2) == "finish"

    # Quando aprovado, encerra com finish
    state_approved = {"critic_approved": True, "revision_count": 0}
    assert should_reflect_or_finish(state_approved) == "finish"

