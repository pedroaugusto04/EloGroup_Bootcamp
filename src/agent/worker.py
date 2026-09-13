"""Auditoria de estoque reproduzível, executada exclusivamente sob demanda."""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src.agent.service import InventoryAgentService
from src.infrastructure.chat_store import CopilotChatStore
from src.infrastructure.email_service import ResendEmailService, render_executive_email_template

logger = logging.getLogger("vertice.inventory_worker")
SNAPSHOT_FILE_PATH = os.environ.get(
    "AUDIT_SNAPSHOT_PATH", os.path.join("data", "processed", "latest_audit_snapshot.json")
)


def get_deep_link_url(thread_id: Optional[str] = None) -> str:
    base_url = os.environ.get("APP_BASE_URL", "http://localhost:5173").rstrip("/")
    deep_path = os.environ.get("AGENT_DEEP_LINK_PATH", "/?view=copilot&source=email")
    if not deep_path.startswith("/"):
        deep_path = f"/{deep_path}"
    if thread_id:
        deep_path += ("&" if "?" in deep_path else "?") + f"thread_id={thread_id}"
    return base_url + deep_path


def _write_snapshot(snapshot: dict) -> None:
    directory = os.path.dirname(SNAPSHOT_FILE_PATH)
    if directory:
        os.makedirs(directory, exist_ok=True)
    temporary = SNAPSHOT_FILE_PATH + ".tmp"
    with open(temporary, "w", encoding="utf-8") as target:
        json.dump(snapshot, target, ensure_ascii=False, indent=2, allow_nan=False)
    os.replace(temporary, SNAPSHOT_FILE_PATH)


def run_autonomous_inventory_audit(
    period_key: str = "full_history",
    send_email: bool = True,
    to_email: Optional[str] = None,
    publish_chat: bool = True,
) -> Dict[str, Any]:
    """Executa uma vez; não configura cron, compra ou reposição automática."""
    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        service = InventoryAgentService()
        diagnostic = service.run_diagnostic(period_key=period_key)
    except Exception as exc:
        snapshot = {
            "schema_version": 2,
            "timestamp": timestamp,
            "period_key": period_key,
            "analysis_success": False,
            "deterministic_approved": False,
            "email_status": "not_sent",
            "error": str(exc),
        }
        _write_snapshot(snapshot)
        return {
            "success": False, "analysis_success": False, "deterministic_approved": False,
            "timestamp": timestamp, "diagnostic": None, "audit_thread_id": None,
            "messages": [], "deep_link_url": None, "email_result": None,
            "email_status": "not_sent", "snapshot_path": SNAPSHOT_FILE_PATH, "error": str(exc),
        }

    approved = diagnostic.get("deterministic_approved") is True
    report = diagnostic.get("final_report") or ""
    analysis_success = bool(diagnostic.get("factual_package"))
    audit_thread_id: Optional[str] = None
    messages = []
    deep_link: Optional[str] = None

    # Publicação factual só ocorre após todos os checks determinísticos.
    if approved and report and publish_chat:
        audit_thread_id = str(uuid.uuid4())
        deep_link = get_deep_link_url(audit_thread_id)
        context = report + "\n\n---\nAlguma dúvida? Pergunte ao agente."
        messages = [{"role": "assistant", "content": context}]
        try:
            CopilotChatStore().save_thread(
                audit_thread_id, messages,
                title=f"Tendência histórica · {diagnostic['factual_package']['meta']['period_key']}",
            )
            service.seed_copilot(audit_thread_id, context)
        except Exception as exc:
            logger.warning("Relatório aprovado, mas falhou o registro do chat: %s", exc)

    email_result = None
    if not send_email:
        email_status = "not_requested"
    elif not approved:
        email_status = "blocked_by_reconciliation"
    else:
        recipient = to_email or os.environ.get("RESEND_TO_EMAIL", "diretoria@verticeretail.com.br")
        email_result = ResendEmailService().send_email(
            to=recipient,
            subject="[Vértice Analytics] Estoque baseado em tendência histórica",
            html_content=render_executive_email_template(diagnostic, deep_link or get_deep_link_url()),
        )
        email_status = email_result.get("status", "error")

    snapshot = {
        "schema_version": 2,
        "timestamp": timestamp,
        "audit_thread_id": audit_thread_id,
        "analysis_success": analysis_success,
        "deterministic_approved": approved,
        "deterministic_checks": diagnostic.get("deterministic_checks", {}),
        "llm_complement_status": diagnostic.get("llm_complement_status"),
        "email_status": email_status,
        "factual_package": diagnostic.get("factual_package"),
        "recommendations": diagnostic.get("recommendations", []),
        "final_report": report if approved else "",
        "deep_link_url": deep_link,
    }
    _write_snapshot(snapshot)
    return {
        "success": analysis_success,
        "analysis_success": analysis_success,
        "deterministic_approved": approved,
        "timestamp": timestamp,
        "diagnostic": diagnostic,
        "audit_thread_id": audit_thread_id,
        "messages": messages,
        "deep_link_url": deep_link,
        "email_result": email_result,
        "email_status": email_status,
        "snapshot_path": SNAPSHOT_FILE_PATH,
    }


def load_latest_audit_snapshot() -> Optional[Dict[str, Any]]:
    if not os.path.exists(SNAPSHOT_FILE_PATH):
        return None
    try:
        with open(SNAPSHOT_FILE_PATH, "r", encoding="utf-8") as source:
            snapshot = json.load(source)
        return snapshot if snapshot.get("schema_version") == 2 else None
    except Exception as exc:
        logger.warning("Erro ao ler snapshot de auditoria: %s", exc)
        return None
