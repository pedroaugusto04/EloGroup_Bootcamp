"""
src/utils/json_parser.py
Módulo utilitário para extração tolerante e validação de JSON a partir de respostas de LLMs.
"""

import json
import re
from typing import Any, Dict, Optional, List


def extract_json_from_llm_response(text: Any) -> Optional[Dict[str, Any]]:
    """
    Extrai e decodifica um objeto JSON de respostas de LLM de forma resiliente.
    Suporta saídas em markdown (```json ... ```), substrings com chaves balanceadas,
    aspas simples e formatações parciais.
    """
    if not text:
        return None
    if isinstance(text, dict):
        return text
    if isinstance(text, list):
        if len(text) > 0 and isinstance(text[0], dict) and "text" in text[0]:
            text = "".join(p.get("text", "") for p in text if isinstance(p, dict))
        else:
            text = str(text)
    if not isinstance(text, str):
        text = str(text)

    text = text.strip()

    # 1. Tentar json.loads direto
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    # 2. Tentar bloco markdown ```json ... ``` ou ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        try:
            parsed = json.loads(match.group(1).strip())
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    # 3. Tentar substring entre o primeiro "{" e o último "}"
    start_idx = text.find("{")
    end_idx = text.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_candidate = text[start_idx : end_idx + 1]
        try:
            parsed = json.loads(json_candidate)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            try:
                candidate_fixed = json_candidate.replace("'", '"')
                candidate_fixed = re.sub(r",\s*([\]}])", r"\1", candidate_fixed)
                parsed = json.loads(candidate_fixed)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass

    return None


def validate_critic_payload(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Valida o contrato estrito do parecer do revisor para garantir conformidade de tipos.
    Retorna o dict validado ou None se o contrato mínimo não for cumprido.
    """
    if not isinstance(data, dict):
        return None

    approved = data.get("approved")
    score = data.get("score")
    feedback = data.get("feedback")
    corrections = data.get("corrections_needed")

    if (
        type(approved) is not bool
        or type(score) is not int
        or not 1 <= score <= 10
        or not isinstance(feedback, str)
        or not feedback.strip()
        or not isinstance(corrections, list)
        or not all(isinstance(item, str) for item in corrections)
    ):
        return None

    return {
        "approved": approved,
        "score": score,
        "feedback": feedback.strip(),
        "corrections_needed": corrections,
    }
