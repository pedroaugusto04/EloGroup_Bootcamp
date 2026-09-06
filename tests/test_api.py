"""
tests/test_api.py
Testes unitários e de integração para a camada de API FastAPI do Vértice Analytics.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_api_filters():
    response = client.get("/api/analytics/filters")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "sales_channels" in data
    assert len(data["categories"]) > 0


def test_api_executive():
    response = client.get("/api/analytics/executive?status=Aprovado&ano=Todos")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "monthly_trend" in data
    assert "channels" in data
    assert "liquida" in data["kpis"]
    assert data["kpis"]["liquida"] > 0


def test_api_sales():
    response = client.get("/api/analytics/sales")
    assert response.status_code == 200
    data = response.json()
    assert "decomposition" in data
    assert "top_skus" in data
    assert "bruta" in data["decomposition"]


def test_api_marketing():
    response = client.get("/api/analytics/marketing")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "channels" in data
    assert "invest_total" in data["kpis"]


def test_api_inventory():
    response = client.get("/api/analytics/inventory")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "categories_rupture" in data
    assert "critical_skus" in data
    assert "status_breakdown" in data
    assert data["kpis"]["skus_ruptura"] == 99


def test_api_customers():
    response = client.get("/api/analytics/customers")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "segments" in data
    assert "pareto_distribution" in data


def test_api_support():
    response = client.get("/api/analytics/support")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "root_causes_ai" in data
    assert "csat_distribution" in data


def test_api_relational_audit():
    response = client.get("/api/audit/relational")
    assert response.status_code == 200
    data = response.json()
    assert "mkt_vs_sales" in data
    assert "inventory_vs_sales" in data
    assert "audit_findings" in data


def test_api_outliers():
    response = client.get("/api/audit/outliers?table=vendas&metric=desconto_reais")
    assert response.status_code == 200
    data = response.json()
    assert "overall_stats" in data
    assert "by_dimension" in data
    assert data["overall_stats"]["outliers_count"] > 0


def test_api_roadmap():
    response = client.get("/api/roadmap/initiatives")
    assert response.status_code == 200
    data = response.json()
    assert "initiatives" in data
    assert len(data["initiatives"]) > 0
    assert data["summary"]["quick_wins_count"] >= 2


def test_api_copilot_threads_lifecycle():
    # 1. Create thread
    res_create = client.post("/api/copilot/threads", json={"title": "Teste API Thread"})
    assert res_create.status_code == 200
    thread = res_create.json()["thread"]
    tid = thread["id"]

    # 2. Get thread
    res_get = client.get(f"/api/copilot/threads/{tid}")
    assert res_get.status_code == 200
    assert res_get.json()["thread"]["id"] == tid

    # 3. List threads
    res_list = client.get("/api/copilot/threads")
    assert res_list.status_code == 200
    assert any(t["id"] == tid for t in res_list.json()["threads"])

    # 4. Delete thread
    res_del = client.delete(f"/api/copilot/threads/{tid}")
    assert res_del.status_code == 200
