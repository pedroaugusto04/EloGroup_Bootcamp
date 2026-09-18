"""
tests/test_deliverables.py
Testes unitários e de integração para as rotas de entregáveis (/api/deliverables).
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_list_deliverables():
    response = client.get("/api/deliverables")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5
    # Verifica propriedades do primeiro entregável
    first = data[0]
    assert "id" in first
    assert "title" in first
    assert "filename" in first
    assert "word_count" in first
    assert first["word_count"] > 0


def test_get_deliverable_detail():
    response = client.get("/api/deliverables/01_relatorio_diagnostico_estrategico")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "01_relatorio_diagnostico_estrategico"
    assert "content" in data
    assert "Diagnóstico executivo" in data["content"] or "Vértice Retail" in data["content"]


def test_get_development_deliverable():
    response = client.get("/api/deliverables/05_desenvolvimento_e_metodologia")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "05_desenvolvimento_e_metodologia"
    assert "content" in data
    assert "ETAPAS REALIZADAS" in data["content"] or "Análise Exploratória" in data["content"]


def test_get_deliverable_not_found():
    response = client.get("/api/deliverables/documento_inexistente_123")
    assert response.status_code == 404


def test_update_deliverable_content():
    # Lê conteúdo original
    res_get = client.get("/api/deliverables/01_relatorio_diagnostico_estrategico")
    assert res_get.status_code == 200
    original_content = res_get.json()["content"]

    # Testa salvar mantendo integridade
    res_put = client.put(
        "/api/deliverables/01_relatorio_diagnostico_estrategico",
        json={"content": original_content}
    )
    assert res_put.status_code == 200
    assert res_put.json()["content"] == original_content


def test_download_deliverable_file():
    response = client.get("/api/deliverables/01_relatorio_diagnostico_estrategico/download")
    assert response.status_code == 200
    assert "attachment" in response.headers.get("content-disposition", "")
    assert len(response.content) > 0


def test_download_all_deliverables_zip():
    response = client.get("/api/deliverables/export/zip")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/zip"
    assert "vertice-documentos-executivos.zip" in response.headers.get("content-disposition", "")
    assert len(response.content) > 0
