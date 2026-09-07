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
from src.agent.constants import LLM_UNAVAILABLE_MESSAGE
from src.infrastructure.email_service import ResendEmailService, render_executive_email_template

logger = logging.getLogger("vertice.inventory_worker")

SNAPSHOT_FILE_PATH = os.environ.get(
    "AUDIT_SNAPSHOT_PATH",
    os.path.join("data", "processed", "latest_audit_snapshot.json")
)



def get_deep_link_url(thread_id: Optional[str] = None) -> str:
    """Resolve a URL de Deep Link para o Copiloto ReAct com base nas variáveis de ambiente e thread_id."""
    base_url = os.environ.get("APP_BASE_URL", "http://localhost:5173").rstrip("/")
    deep_path = os.environ.get("AGENT_DEEP_LINK_PATH", "/?view=copilot&source=email")
    if not deep_path.startswith("/"):
        deep_path = f"/{deep_path}"
    
    if thread_id:
        separator = "&" if "?" in deep_path else "?"
        deep_path = f"{deep_path}{separator}thread_id={thread_id}"
        
    return f"{base_url}{deep_path}"



def run_autonomous_inventory_audit(
    send_email: bool = True,
    to_email: Optional[str] = None,
    date_filter: str = "",
    days_window: float = 365.0,
    period_label: str = "Ano Fechado 2023",
) -> Dict[str, Any]:
    """
    Executa o ciclo completo de auditoria autônoma de estoque:
    1. Varredura e raciocínio analítico no DuckDB via LangGraph considerando a janela temporal selecionada.
    2. Validação contra os 4 guardrails de negócio pelo nó de reflexão.
    3. Criação automática de card de chat no histórico persistente (CopilotChatStore).
    4. Renderização do parecer executivo em e-mail HTML corporativo.
    5. Envio de e-mail via Resend (se habilitado).
    6. Persistência do snapshot de auditoria para o Copiloto ReAct.
    """
    import uuid
    from src.infrastructure.chat_store import CopilotChatStore

    logger.info("Iniciando execução do Worker Autônomo de Estoque (%s)...", period_label)
    
    # 1. Executa auditoria no LangGraph
    service = InventoryAgentService()
    diagnostic_result = service.run_diagnostic(
        date_filter=date_filter,
        days_window=days_window,
        period_label=period_label,
    )
    report = diagnostic_result.get("final_report") or ""
    report_is_valid = (
        diagnostic_result.get("critic_approved") is True
        and diagnostic_result.get("critic_reviewed") is True
        and LLM_UNAVAILABLE_MESSAGE not in report
    )

    # 2. Criação automática do card de chat na base de histórico
    audit_thread_id = str(uuid.uuid4())
    audit_title = f"Auditoria: {period_label}"
    
    if report:
        initial_context = (
            f"{report}\n\n"
            "---\n"
            "**Como posso apoiar a sua análise?** Você pode solicitar simulações detalhadas, aprofundamento em SKUs específicos ou estratégias de liquidação e reposição."
        )
    else:
        structured = diagnostic_result.get("structured_data") or {}
        total_stranded = structured.get("total_stranded_cash")
        ruptura_count = structured.get("ruptura_count")
        criticos_count = structured.get("criticos_count")
        mkt_cats = structured.get("mkt_alert_categories", [])
        summary = []
        if total_stranded is not None:
            summary.append(f"- **Capital imobilizado**: `R$ {total_stranded:,.2f}`")
        if ruptura_count is not None and criticos_count is not None:
            summary.append(f"- **Ruptura e risco**: `{ruptura_count + criticos_count} SKUs`")
        if mkt_cats:
            summary.append(f"- **Categorias em alerta**: `{', '.join(mkt_cats)}`")
        initial_context = (
            f"**Parecer de Auditoria de Estoque ({period_label}):**\n\n"
            + ("\n".join(summary) if summary else "Auditoria finalizada com dados calculados.")
            + "\n\n**Como posso apoiar a sua análise?** Você pode solicitar simulações, investigações de SKUs específicos ou estratégias de abastecimento."
        )

    chat_messages = [{"role": "assistant", "content": initial_context}]
    
    try:
        chat_store = CopilotChatStore()
        chat_store.save_thread(
            thread_id=audit_thread_id,
            messages=chat_messages,
            title=audit_title
        )
        service.seed_copilot(thread_id=audit_thread_id, initial_message=initial_context)
        logger.info("Card de auditoria salvo no histórico (thread_id: %s, título: '%s')", audit_thread_id, audit_title)
    except Exception as e:
        logger.warning("Falha ao registrar card de auditoria no chat_store: %s", e)

    deep_link = get_deep_link_url(thread_id=audit_thread_id)
    
    # 3. Renderiza o e-mail corporativo
    email_html = render_executive_email_template(
        report_data=diagnostic_result,
        deep_link_url=deep_link
    )
    
    # 4. Salva snapshot persistente para o Copiloto
    snapshot_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "audit_thread_id": audit_thread_id,
        "critic_approved": diagnostic_result.get("critic_approved", False),
        "critic_feedback": diagnostic_result.get("critic_feedback", ""),
        "structured_data": diagnostic_result.get("structured_data", {}),
        "final_report": report if report_is_valid else "",
        "deep_link_url": deep_link,
    }
    
    try:
        os.makedirs(os.path.dirname(SNAPSHOT_FILE_PATH), exist_ok=True)
        with open(SNAPSHOT_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(snapshot_data, f, ensure_ascii=False, indent=2)
        logger.info("Snapshot de auditoria salvo com sucesso em: %s", SNAPSHOT_FILE_PATH)
    except Exception as e:
        logger.warning("Falha ao salvar snapshot da auditoria: %s", e)

    # 5. Disparo de E-mail via Resend
    email_result = None
    if send_email and report_is_valid:
        recipient = to_email or os.environ.get("RESEND_TO_EMAIL", "diretoria@verticeretail.com.br")
        subject = "[Vértice Analytics] Parecer Executivo de Auditoria de Estoque & Rentabilidade"
        
        email_service = ResendEmailService()
        email_result = email_service.send_email(
            to=recipient,
            subject=subject,
            html_content=email_html
        )
        logger.info("Resultado do envio de e-mail via Resend: %s", email_result.get("status"))
    elif send_email:
        logger.warning("E-mail executivo não enviado: parecer não foi validado.")

    return {
        "success": report_is_valid,
        "timestamp": snapshot_data["timestamp"],
        "diagnostic": diagnostic_result,
        "audit_thread_id": audit_thread_id,
        "messages": chat_messages,
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
