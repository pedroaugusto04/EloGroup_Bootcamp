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
        "critic_approved": True,
        "critic_feedback": "[Nota 10/10] Parecer em total conformidade com os guardrails.",
        "structured_data": {
            "total_stranded_cash": 42500.00,
            "ruptura_count": 5,
            "criticos_count": 3,
            "mkt_alert_categories": ["Moda"],
            "top_critical_skus": [
                {
                    "sku_id": "SKU-00185",
                    "nome_produto": "Camisa Social",
                    "categoria": "Moda",
                    "estoque_disponivel": 0,
                    "dias_cobertura": 0.0,
                }
            ],
        },
    }
    deep_link = "http://localhost:8501/?view=agente_consultor"
    html = render_executive_email_template(mock_data, deep_link)

    assert "<!DOCTYPE html>" in html
    assert "Vértice Retail" in html or "VÉRTICE" in html
    assert "R$ 42,500.00" in html or "42.500" in html or "42,500" in html
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
def test_run_autonomous_inventory_audit_worker(mock_send):
    mock_send.return_value = {"success": True, "status": "sent", "id": "re_test_123"}
    
    # Executa o worker
    result = run_autonomous_inventory_audit(send_email=True, to_email="test@vertice.com.br")
    assert result["success"] is True
    assert "timestamp" in result
    assert "diagnostic" in result
    assert "email_result" in result
    assert os.path.exists(SNAPSHOT_FILE_PATH)

    snapshot = load_latest_audit_snapshot()
    assert snapshot is not None
    assert "structured_data" in snapshot
    assert "final_report" in snapshot


@patch("src.agent.worker.InventoryAgentService")
@patch.object(ResendEmailService, "send_email")
def test_worker_does_not_send_unvalidated_report(mock_send, mock_service):
    mock_service.return_value.run_diagnostic.return_value = {
        "critic_approved": False,
        "critic_reviewed": False,
        "final_report": None,
        "structured_data": {"ruptura_count": 2, "criticos_count": 1},
        "critic_feedback": "Revisão indisponível.",
    }

    result = run_autonomous_inventory_audit(send_email=True)

    assert result["success"] is False
    assert result["email_result"] is None
    mock_send.assert_not_called()
