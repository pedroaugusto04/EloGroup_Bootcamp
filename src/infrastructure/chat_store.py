"""
src/infrastructure/chat_store.py
Gerenciamento de persistência local para histórico de conversas e threads do Copiloto de Estoque.
Permite criação de threads, restauração de conversas passadas, auto-título e deleção.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.config import DATA_DIR

logger = logging.getLogger("vertice.chat_store")

DEFAULT_CHAT_STORE_PATH = DATA_DIR / "copilot_chats.json"


class CopilotChatStore:
    """Gerenciador de histórico de sessões do Copiloto de Estoque."""

    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or DEFAULT_CHAT_STORE_PATH
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Garante que o diretório e o arquivo de persistência existam."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.file_path.exists():
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump({"threads": {}}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("Erro ao inicializar arquivo de histórico de chat: %s", e)

    def _read_data(self) -> Dict[str, Any]:
        """Lê o arquivo de histórico com fallback seguro."""
        try:
            if not self.file_path.exists():
                return {"threads": {}}
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Falha ao ler dados de histórico do chat (%s): %s", self.file_path, e)
            return {"threads": {}}

    def _write_data(self, data: Dict[str, Any]) -> None:
        """Escreve os dados no arquivo JSON de forma segura."""
        try:
            temp_path = self.file_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            temp_path.replace(self.file_path)
        except Exception as e:
            logger.error("Falha ao salvar dados de histórico de chat: %s", e)

    @staticmethod
    def _generate_title(messages: List[Dict[str, str]]) -> str:
        """Gera um título conciso e analítico para a conversa com base na primeira mensagem do usuário."""
        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "").strip()
                clean = " ".join(content.split())
                if len(clean) > 38:
                    return clean[:35] + "..."
                return clean or "Nova Conversa"
        return "Nova Conversa"

    def list_threads(self) -> List[Dict[str, Any]]:
        """
        Retorna a lista de conversas ordenadas da mais recente para a mais antiga.
        Formato de cada item:
        {
            "id": "uuid",
            "title": "...",
            "created_at": "...",
            "updated_at": "...",
            "message_count": int,
            "preview": "..."
        }
        """
        data = self._read_data()
        threads = data.get("threads", {})
        result = []

        for thread_id, info in threads.items():
            msgs = info.get("messages", [])
            last_msg = msgs[-1]["content"] if msgs else ""
            clean_preview = " ".join(last_msg.split())
            if len(clean_preview) > 50:
                clean_preview = clean_preview[:47] + "..."

            result.append({
                "id": thread_id,
                "title": info.get("title") or self._generate_title(msgs),
                "created_at": info.get("created_at", datetime.now().isoformat()),
                "updated_at": info.get("updated_at", datetime.now().isoformat()),
                "message_count": len(msgs),
                "preview": clean_preview
            })

        # Ordenar por updated_at descendente
        result.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return result

    def get_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Retorna o objeto completo da conversa (incluindo array de mensagens)."""
        data = self._read_data()
        return data.get("threads", {}).get(thread_id)

    def save_thread(
        self,
        thread_id: str,
        messages: List[Dict[str, str]],
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cria ou atualiza uma conversa com suas mensagens e metadados."""
        data = self._read_data()
        threads = data.setdefault("threads", {})

        now_iso = datetime.now().isoformat()
        existing = threads.get(thread_id, {})

        created_at = existing.get("created_at", now_iso)
        current_title = title or existing.get("title") or self._generate_title(messages)

        thread_obj = {
            "id": thread_id,
            "title": current_title,
            "created_at": created_at,
            "updated_at": now_iso,
            "messages": messages,
        }

        threads[thread_id] = thread_obj
        self._write_data(data)
        return thread_obj

    def delete_thread(self, thread_id: str) -> bool:
        """Exclui uma conversa do histórico."""
        data = self._read_data()
        threads = data.get("threads", {})
        if thread_id in threads:
            del threads[thread_id]
            self._write_data(data)
            return True
        return False

    def clear_all(self) -> None:
        """Limpa todo o histórico de conversas."""
        self._write_data({"threads": {}})
