"""Envio e renderização do parecer factual de estoque."""

import html
import logging
import os
import re
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger("vertice.email_service")


def parse_recipient_emails(to: str) -> List[str]:
    recipients = [email.strip() for email in re.split(r"[,;\n]+", to or "") if email.strip()]
    return list(dict.fromkeys(recipients))


class ResendEmailService:
    def __init__(self, api_key: Optional[str] = None, from_email: Optional[str] = None,
                 base_url: str = "https://api.resend.com/emails"):
        self.api_key = api_key if api_key is not None else os.environ.get("RESEND_API_KEY")
        self.from_email = from_email if from_email is not None else os.environ.get(
            "RESEND_FROM_EMAIL", "Vertice Analytics <onboarding@resend.dev>"
        )
        self.base_url = base_url

    def send_email(self, to: str, subject: str, html_content: str,
                   text_content: Optional[str] = None) -> Dict[str, Any]:
        recipients = parse_recipient_emails(to)
        if not recipients:
            return {"success": False, "status": "error", "error": "Nenhum destinatário de e-mail foi configurado."}
        if not self.api_key:
            return {
                "success": True, "status": "simulated", "to": recipients, "subject": subject,
                "message": "E-mail processado e simulado com sucesso. Configure RESEND_API_KEY para envio real.",
            }
        payload: Dict[str, Any] = {
            "from": self.from_email, "to": recipients, "subject": subject, "html": html_content,
        }
        if text_content:
            payload["text"] = text_content
        try:
            response = requests.post(
                self.base_url, json=payload,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                timeout=10,
            )
            if response.status_code in (200, 201):
                return {
                    "success": True, "status": "sent", "id": response.json().get("id"),
                    "to": recipients, "subject": subject,
                }
            return {"success": False, "status": "error", "error": f"Erro Resend HTTP {response.status_code}: {response.text}"}
        except Exception as exc:
            return {"success": False, "status": "error", "error": f"Falha de conexão ao enviar e-mail via Resend: {exc}"}


def _brl(value: Any) -> str:
    if value is None:
        return "Não disponível"
    return "R$ " + f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render_executive_email_template(report_data: Dict[str, Any], deep_link_url: str) -> str:
    """Renderiza apenas valores reconciliados do envelope de evidências."""
    package = report_data.get("factual_package") or {}
    structured = package.get("summary") or report_data.get("structured_data") or {}
    meta = package.get("meta") or report_data.get("meta") or {}
    capital = structured.get("capital") or {}
    operational = structured.get("operational") or {}
    exposure = structured.get("lead_time_exposure") or {}
    liquidation = structured.get("liquidation") or {}
    central = liquidation.get("central_scenario") or {}
    top = structured.get("top_attention_category") or {}
    banner = structured.get("methodology_banner") or (
        "Posição de estoque fornecida — data de referência não informada. "
        f"Tendência de vendas observada entre {meta.get('sales_start', '?')} e {meta.get('sales_end', '?')}."
    )
    approved = report_data.get("deterministic_approved") is True
    badge = "APROVAÇÃO DETERMINÍSTICA" if approved else "RECONCILIAÇÃO REPROVADA"

    rows = ""
    for item in (package.get("items") or [])[:5]:
        rows += (
            "<tr>"
            f"<td>{html.escape(str(item.get('sku_id', '—')))}</td>"
            f"<td>{html.escape(str(item.get('nome_produto', '—')))}</td>"
            f"<td>{html.escape(str(item.get('categoria', '—')))}</td>"
            f"<td>{_brl(item.get('margem_potencialmente_exposta'))}</td>"
            "</tr>"
        )
    if not rows:
        rows = '<tr><td colspan="4">Nenhum item elegível no período.</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width">
<title>Copiloto de estoque baseado em tendência histórica</title>
<style>body{{background:#f2f4f7;color:#17202a;font-family:Arial,sans-serif;margin:0}}main{{background:white;border:1px solid #d9dee5;margin:24px auto;max-width:680px;padding:28px}}.banner{{background:#f8fafc;border-left:4px solid #2f6f5e;padding:14px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}.card{{border:1px solid #d9dee5;padding:14px}}small{{color:#667085}}table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid #d9dee5;padding:9px;text-align:left;font-size:12px}}a{{background:#17202a;color:white;display:inline-block;padding:12px 18px;text-decoration:none}}</style></head>
<body><main>
<small>VÉRTICE RETAIL · {badge}</small>
<h1>Copiloto de estoque baseado em tendência histórica</h1>
<p class="banner">{html.escape(banner)}</p>
<div class="grid">
  <div class="card"><small>Capital disponível coberto</small><h2>{_brl(capital.get('capital_disponivel'))}</h2><p>{capital.get('skus_com_custo_vendas', 0)} SKUs com custo válido em Vendas</p></div>
  <div class="card"><small>Exposição no lead time cadastral</small><h2>{exposure.get('skus', 0)} SKUs ativos</h2><p>{_brl(exposure.get('margem_potencialmente_exposta'))} de margem potencialmente exposta; não é perda realizada.</p></div>
  <div class="card"><small>Liquidação central · 30% desconto · 50% sell-through</small><h2>{_brl(central.get('receita_ajustada_devolucoes'))}</h2><p>Receita estimada ajustada por devoluções; capital envolvido: {_brl(central.get('capital_historico_envolvido'))}.</p></div>
  <div class="card"><small>Cobertura financeira e atenção</small><h2>{capital.get('skus_com_custo_vendas', 0)} / {capital.get('total_skus', 0)} SKUs</h2><p>Top categoria de atenção: {html.escape(str(top.get('categoria', 'Não disponível')))}.</p></div>
</div>
<h2>Prioridades de investigação</h2><table><thead><tr><th>SKU</th><th>Produto</th><th>Categoria</th><th>Margem exposta</th></tr></thead><tbody>{rows}</tbody></table>
<p><small>Ruptura atual: {operational.get('ruptura_atual', 0)} · No/abaixo do ponto: {operational.get('ponto_pedido', 0)}. Lead time é cadastral. Impostos, comissões, logística reversa e elasticidade de preço não estão disponíveis.</small></p>
<p><a href="{html.escape(deep_link_url, quote=True)}">Acessar Copiloto de Estoque no App →</a></p>
</main></body></html>"""
