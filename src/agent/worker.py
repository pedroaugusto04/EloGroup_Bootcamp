"""
src/agent/worker.py
Worker Autônomo de Auditoria Periódica de Estoque (Vértice Retail).
Orquestra o ciclo do LangGraph (Plan + Reflection), gera o e-mail executivo HTML,
dispara notificação via Resend e salva snapshot persistente para o Copiloto ReAct.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from src.agent.service import InventoryAgentService
from src.infrastructure.email_service import ResendEmailService, render_executive_email_template

logger = logging.getLogger("vertice.inventory_worker")

SNAPSHOT_FILE_PATH = os.environ.get(
    "AUDIT_SNAPSHOT_PATH",
    os.path.join("data", "processed", "latest_audit_snapshot.json")
)



def get_deep_link_url() -> str:
    """Resolve a URL de Deep Link para o Copiloto ReAct com base nas variáveis de ambiente."""
    base_url = os.environ.get("APP_BASE_URL", "http://localhost:8501").rstrip("/")
    deep_path = os.environ.get("AGENT_DEEP_LINK_PATH", "/?view=agent&source=email")
    if not deep_path.startswith("/"):
        deep_path = f"/{deep_path}"
    return f"{base_url}{deep_path}"



def run_autonomous_inventory_audit(
    send_email: bool = True,
    to_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executa o ciclo completo de auditoria autônoma de estoque:
    1. Varredura e raciocínio analítico no DuckDB via LangGraph.
    2. Validação contra os 4 guardrails de negócio pelo nó de reflexão.
    3. Renderização do parecer executivo em e-mail HTML corporativo.
    4. Envio de e-mail via Resend (se habilitado).
    5. Persistência do snapshot de auditoria para o Copiloto ReAct.
    """
    logger.info("Iniciando execução do Worker Autônomo de Estoque...")
    
    # 1. Executa auditoria no LangGraph
    service = InventoryAgentService()
    diagnostic_result = service.run_diagnostic()
    
    deep_link = get_deep_link_url()
    
    # 2. Renderiza o e-mail corporativo
    email_html = render_executive_email_template(
        report_data=diagnostic_result,
        deep_link_url=deep_link
    )
    
    # 3. Salva snapshot persistente para o Copiloto
    snapshot_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "critic_approved": diagnostic_result.get("critic_approved", False),
        "critic_feedback": diagnostic_result.get("critic_feedback", ""),
        "structured_data": diagnostic_result.get("structured_data", {}),
        "final_report": diagnostic_result.get("final_report", ""),
        "deep_link_url": deep_link,
    }
    
    try:
        os.makedirs(os.path.dirname(SNAPSHOT_FILE_PATH), exist_ok=True)
        with open(SNAPSHOT_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(snapshot_data, f, ensure_ascii=False, indent=2)
        logger.info("Snapshot de auditoria salvo com sucesso em: %s", SNAPSHOT_FILE_PATH)
    except Exception as e:
        logger.warning("Falha ao salvar snapshot da auditoria: %s", e)

    # 4. Disparo de E-mail via Resend
    email_result = None
    if send_email:
        recipient = to_email or os.environ.get("RESEND_TO_EMAIL", "diretoria@verticeretail.com.br")
        subject = "[Vértice Analytics] Parecer Executivo de Auditoria de Estoque & Rentabilidade"
        
        email_service = ResendEmailService()
        email_result = email_service.send_email(
            to=recipient,
            subject=subject,
            html_content=email_html
        )
        logger.info("Resultado do envio de e-mail via Resend: %s", email_result.get("status"))

    return {
        "success": True,
        "timestamp": snapshot_data["timestamp"],
        "diagnostic": diagnostic_result,
        "deep_link_url": deep_link,
        "email_result": email_result,
        "snapshot_path": SNAPSHOT_FILE_PATH,
    }


def load_latest_audit_snapshot() -> Optional[Dict[str, Any]]:
    """Carrega o último snapshot de auditoria persistido em disco."""
    if os.path.exists(SNAPSHOT_FILE_PATH):
        try:
            with open(SNAPSHOT_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Erro ao ler snapshot de auditoria: %s", e)
    return None
