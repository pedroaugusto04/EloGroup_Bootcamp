"""
src/infrastructure/email_service.py
Serviço de envio de e-mail via Resend e utilitários de parsing de destinatários.
"""

import logging
import os
import re
from typing import Any, Dict, List, Optional

import requests

from .email_templates import render_executive_email_template

logger = logging.getLogger("vertice.email_service")


def parse_recipient_emails(to: str) -> List[str]:
    """Extrai e remove duplicatas de uma lista de e-mails separados por vírgula, ponto-e-vírgula ou quebra de linha."""
    recipients = [email.strip() for email in re.split(r"[,;\n]+", to or "") if email.strip()]
    return list(dict.fromkeys(recipients))


class ResendEmailService:
    """Cliente de integração com a API Resend para disparo de comunicados executivos."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
        base_url: str = "https://api.resend.com/emails",
    ):
        self.api_key = api_key if api_key is not None else os.environ.get("RESEND_API_KEY")
        self.from_email = from_email if from_email is not None else os.environ.get(
            "RESEND_FROM_EMAIL", "Vertice Analytics <onboarding@resend.dev>"
        )
        self.base_url = base_url

    def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        recipients = parse_recipient_emails(to)
        if not recipients:
            return {"success": False, "status": "error", "error": "Nenhum destinatário de e-mail foi configurado."}
        if not self.api_key:
            return {
                "success": True,
                "status": "simulated",
                "to": recipients,
                "subject": subject,
                "message": "E-mail processado e simulado com sucesso. Configure RESEND_API_KEY para envio real.",
            }
        payload: Dict[str, Any] = {
            "from": self.from_email,
            "to": recipients,
            "subject": subject,
            "html": html_content,
        }
        if text_content:
            payload["text"] = text_content
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                timeout=10,
            )
            if response.status_code in (200, 201):
                return {
                    "success": True,
                    "status": "sent",
                    "id": response.json().get("id"),
                    "to": recipients,
                    "subject": subject,
                }
            return {
                "success": False,
                "status": "error",
                "error": f"Erro Resend HTTP {response.status_code}: {response.text}",
            }
        except Exception as exc:
            return {
                "success": False,
                "status": "error",
                "error": f"Falha de conexão ao enviar e-mail via Resend: {exc}",
            }


__all__ = ["ResendEmailService", "parse_recipient_emails", "render_executive_email_template"]
