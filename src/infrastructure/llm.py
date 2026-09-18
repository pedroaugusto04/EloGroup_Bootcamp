"""
src/infrastructure/llm.py
Fábrica e provedor de clientes de Modelos de Linguagem (LLM) via LiteLLM / LangChain.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger("vertice.llm")


def get_llm():
    """
    Obtém o modelo LLM configurado nas variáveis de ambiente ou retorna None se offline/não configurado.
    """
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        from langchain_litellm import ChatLiteLLM
        model = os.environ.get("LLM_MODEL", "openai/gemini-3-flash-preview")
        api_base = os.environ.get("OPENAI_API_BASE", "https://chat.eloagents.click/api")
        temperature = float(os.environ.get("LLM_TEMPERATURE", "0.1"))
        request_timeout = int(os.environ.get("LLM_REQUEST_TIMEOUT", "120"))
        max_retries = int(os.environ.get("LLM_MAX_RETRIES", "3"))
        return ChatLiteLLM(
            model=model,
            temperature=temperature,
            api_base=api_base,
            request_timeout=request_timeout,
            max_retries=max_retries,
        )
    except Exception as e:
        logger.warning("Falha ao instanciar ChatLiteLLM: %s", e)
        return None
