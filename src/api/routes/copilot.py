"""
src/api/routes/copilot.py
Rotas do Copiloto de estoque baseado em tendência histórica.
Permite criação de conversas, envio de mensagens analíticas, gerenciamento de sessões e execução de diagnósticos.
"""

import uuid
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict
from fastapi import APIRouter, HTTPException

from src.infrastructure.chat_store import CopilotChatStore
from src.agent.service import InventoryAgentService
from src.agent.worker import load_latest_audit_snapshot, run_autonomous_inventory_audit
from src.agent.periods import VALID_PERIOD_KEYS, build_meta, resolve_period
from src.infrastructure.database import DuckDBRepository

router = APIRouter(prefix="/copilot", tags=["copilot"])

_service_instance: Optional[InventoryAgentService] = None


def get_service() -> InventoryAgentService:
    global _service_instance
    if _service_instance is None:
        _service_instance = InventoryAgentService()
    return _service_instance


class CreateThreadRequest(BaseModel):
    title: Optional[str] = "Nova Conversa"
    initial_message: Optional[str] = None


class ChatMessageRequest(BaseModel):
    thread_id: str
    message: str


class AuditRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    period_key: Literal["full_history", "calendar_2023", "last_90d_observed"] = "full_history"
    send_email: bool = True
    to_email: Optional[str] = None


# =========================================================================
# 1. GERENCIAMENTO DE THREADS (SESSÕES)
# =========================================================================

@router.get("/threads")
def list_threads():
    chat_store = CopilotChatStore()
    threads = chat_store.list_threads()
    return {"threads": threads}


@router.post("/threads")
def create_thread(req: CreateThreadRequest):
    chat_store = CopilotChatStore()
    new_id = str(uuid.uuid4())
    initial_msgs = []
    if req.initial_message:
        initial_msgs.append({"role": "assistant", "content": req.initial_message})
    
    created = chat_store.create_thread(title=req.title or "Nova Conversa", messages=initial_msgs, thread_id=new_id)
    return {"thread": created}


@router.get("/threads/{thread_id}")
def get_thread(thread_id: str):
    chat_store = CopilotChatStore()
    thread = chat_store.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread não encontrada")
    return {"thread": thread}


@router.delete("/threads/{thread_id}")
def delete_thread(thread_id: str):
    chat_store = CopilotChatStore()
    success = chat_store.delete_thread(thread_id)
    if not success:
        raise HTTPException(status_code=404, detail="Thread não encontrada para exclusão")
    return {"status": "deleted", "thread_id": thread_id}


# =========================================================================
# 2. CHAT & INTERAÇÃO ANALÍTICA
# =========================================================================

@router.post("/chat")
def send_chat_message(req: ChatMessageRequest):
    chat_store = CopilotChatStore()
    service = get_service()

    thread = chat_store.get_thread(req.thread_id)
    if not thread:
        # Cria thread se não existir
        thread = chat_store.create_thread(title=req.message[:30] + "...", messages=[], thread_id=req.thread_id)

    messages = thread.get("messages", [])
    messages.append({"role": "user", "content": req.message})

    # Atualiza o título da thread com base na primeira pergunta do usuário se for o título padrão
    title = thread.get("title", "Nova Conversa")
    if title == "Nova Conversa" or not title:
        title = req.message[:35] + ("..." if len(req.message) > 35 else "")

    try:
        response_text = service.ask_copilot(
            query=req.message,
            thread_id=req.thread_id,
            history=messages[:-1]
        )
    except Exception as e:
        response_text = f"Erro ao processar consulta com o Copiloto: {str(e)}"

    messages.append({"role": "assistant", "content": response_text})
    chat_store.save_thread(req.thread_id, messages, title=title)

    return {
        "thread_id": req.thread_id,
        "response": response_text,
        "messages": messages,
        "title": title
    }


# =========================================================================
# 3. WORKER DE AUDITORIA & SNAPSHOTS
# =========================================================================

@router.get("/periods")
def list_audit_periods():
    repo = DuckDBRepository()
    return {
        "periods": [
            {**build_meta(resolve_period(repo, key)), "label": resolve_period(repo, key).label}
            for key in VALID_PERIOD_KEYS
        ]
    }

@router.get("/audit/latest")
def get_latest_audit():
    snapshot = load_latest_audit_snapshot()
    return {"snapshot": snapshot}


@router.post("/audit/run")
def run_audit(req: AuditRunRequest):
    result = run_autonomous_inventory_audit(
        period_key=req.period_key,
        send_email=req.send_email,
        to_email=req.to_email,
    )
    return result
