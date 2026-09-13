"""
tests/test_email_and_worker.py
Suíte de testes para o Serviço de E-mail Resend, Renderizador HTML e Worker Autônomo de Auditoria.
"""

import os
import json
from unittest.mock import patch, MagicMock
import pytest

from src.infrastructure.email_service import ResendEmailService, render_executive_email_template
from src.agent.worker import (
    run_autonomous_inventory_audit,
    get_deep_link_url,
    load_latest_audit_snapshot,
    SNAPSHOT_FILE_PATH,
)


def test_render_executive_email_template():
    mock_data = {
        "deterministic_approved": True,
        "factual_package": {
            "meta": {"sales_start": "2023-01-01", "sales_end": "2024-01-26"},
            "summary": {
                "methodology_banner": "Posição de estoque fornecida — data de referência não informada. Tendência de vendas observada entre 01/01/2023 e 26/01/2024.",
                "capital": {"capital_disponivel": 42500, "skus_com_custo_vendas": 10, "total_skus": 11},
                "operational": {"ruptura_atual": 5, "ponto_pedido": 3},
                "lead_time_exposure": {"skus": 1, "margem_potencialmente_exposta": 123.45},
                "liquidation": {"central_scenario": {"receita_ajustada_devolucoes": 1000, "capital_historico_envolvido": 800}},
                "top_attention_category": {"categoria": "Moda"},
            },
            "items": [{"sku_id": "SKU-00185", "nome_produto": "Camisa Social", "categoria": "Moda", "margem_potencialmente_exposta": 123.45}],
        },
    }
    deep_link = "http://localhost:8501/?view=agente_consultor"
    html = render_executive_email_template(mock_data, deep_link)

    assert "<!DOCTYPE html>" in html
    assert "Vértice Retail" in html or "VÉRTICE" in html
    assert "R$ 42.500,00" in html
    assert "SKU-00185" in html
    assert deep_link in html
    assert "Acessar Copiloto de Estoque no App" in html


def test_resend_email_service_simulation_mode():
    service = ResendEmailService(api_key="")
    res = service.send_email(
        to="diretoria@vertice.com.br",
        subject="Teste de Simulação",
        html_content="<p>Conteúdo de teste</p>"
    )
    assert res["success"] is True
    assert res["status"] == "simulated"
    assert "simulado" in res["message"].lower()


@patch("requests.post")
def test_resend_email_service_accepts_multiple_recipients(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": "re_msg_multiple"}
    mock_post.return_value = mock_resp

    service = ResendEmailService(api_key="re_test_key_123")
    service.send_email(
        to="ceo@vertice.com.br, diretoria@vertice.com.br; ceo@vertice.com.br",
        subject="Parecer Executivo",
        html_content="<p>Relatório</p>",
    )

    called_payload = mock_post.call_args[1]["json"]
    assert called_payload["to"] == ["ceo@vertice.com.br", "diretoria@vertice.com.br"]


@patch("requests.post")
def test_resend_email_service_http_call(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": "re_msg_123456789"}
    mock_post.return_value = mock_resp

    service = ResendEmailService(api_key="re_test_key_123")
    res = service.send_email(
        to="ceo@vertice.com.br",
        subject="Parecer Executivo Semanal",
        html_content="<p>Relatório de Estoque</p>"
    )

    assert res["success"] is True
    assert res["status"] == "sent"
    assert res["id"] == "re_msg_123456789"
    mock_post.assert_called_once()
    called_payload = mock_post.call_args[1]["json"]
    assert called_payload["to"] == ["ceo@vertice.com.br"]
    assert "Bearer re_test_key_123" in mock_post.call_args[1]["headers"]["Authorization"]


def test_deep_link_resolution():
    url = get_deep_link_url()
    assert "http" in url
    assert "agente_consultor" in url or "view=" in url


@patch.object(ResendEmailService, "send_email")
def test_run_autonomous_inventory_audit_worker(mock_send, tmp_path):
    mock_send.return_value = {"success": True, "status": "sent", "id": "re_test_123"}
    test_snap_path = str(tmp_path / "test_snapshot.json")
    
    with patch("src.agent.worker.SNAPSHOT_FILE_PATH", test_snap_path):
        result = run_autonomous_inventory_audit(send_email=True, to_email="test@vertice.com.br")
        assert result["success"] is True
        assert "timestamp" in result
        assert "diagnostic" in result
        assert "email_result" in result
        assert os.path.exists(test_snap_path)

        with patch("src.agent.worker.SNAPSHOT_FILE_PATH", test_snap_path):
            snapshot = load_latest_audit_snapshot()
            assert snapshot is not None
            assert snapshot["schema_version"] == 2
            assert "factual_package" in snapshot
            assert "final_report" in snapshot


@patch("src.agent.worker.InventoryAgentService")
@patch.object(ResendEmailService, "send_email")
def test_worker_does_not_send_unvalidated_report(mock_send, mock_service, tmp_path):
    test_snap_path = str(tmp_path / "test_snapshot_invalid.json")
    mock_service.return_value.run_diagnostic.return_value = {
        "deterministic_approved": False,
        "final_report": None,
        "factual_package": None,
    }

    with patch("src.agent.worker.SNAPSHOT_FILE_PATH", test_snap_path):
        result = run_autonomous_inventory_audit(send_email=True)

        assert result["success"] is False
        assert result["email_result"] is None
        mock_send.assert_not_called()
        assert os.path.exists(test_snap_path)
