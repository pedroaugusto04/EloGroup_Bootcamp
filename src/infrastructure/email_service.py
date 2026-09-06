"""
src/infrastructure/email_service.py
Serviço de Notificação Executiva e Provedor de E-mail via Resend.
Permite o envio de pareceres executivos e alertas de estoque diretamente para a diretoria,
com template HTML corporativo responsivo e Deep Link para o Copiloto ReAct.
"""

import os
import logging
import re
import textwrap
from typing import Dict, Any, Optional, List
import requests

logger = logging.getLogger("vertice.email_service")


def parse_recipient_emails(to: str) -> List[str]:
    """Converte uma configuração de destinatários em uma lista para o Resend."""
    recipients = [email.strip() for email in re.split(r"[,;\n]+", to or "") if email.strip()]

    # Preserva a ordem configurada, evitando enviar duas vezes ao mesmo endereço.
    return list(dict.fromkeys(recipients))


class ResendEmailService:
    """Provedor de E-mails Executivos via API REST do Resend."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
        base_url: str = "https://api.resend.com/emails"
    ):
        self.api_key = api_key if api_key is not None else os.environ.get("RESEND_API_KEY")
        self.from_email = from_email if from_email is not None else os.environ.get("RESEND_FROM_EMAIL", "Vertice Analytics <onboarding@resend.dev>")
        self.base_url = base_url


    def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia e-mail via Resend API.
        Caso a API Key não esteja configurada, opera em modo de simulação com log transparente.
        """
        recipients = parse_recipient_emails(to)
        if not recipients:
            return {
                "success": False,
                "status": "error",
                "error": "Nenhum destinatário de e-mail foi configurado.",
            }

        if not self.api_key:
            logger.info("RESEND_API_KEY não configurada. Operação executada em modo simulação (Mock).")
            return {
                "success": True,
                "status": "simulated",
                "to": recipients,
                "subject": subject,
                "message": "E-mail processado e simulado com sucesso. Configure RESEND_API_KEY no .env para envio real."
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload: Dict[str, Any] = {
            "from": self.from_email,
            "to": recipients,
            "subject": subject,
            "html": html_content
        }
        if text_content:
            payload["text"] = text_content

        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                res_data = response.json()
                logger.info("E-mail enviado com sucesso via Resend para '%s' (ID: %s)", recipients, res_data.get("id"))
                return {
                    "success": True,
                    "status": "sent",
                    "id": res_data.get("id"),
                    "to": recipients,
                    "subject": subject
                }
            else:
                err_msg = f"Erro Resend HTTP {response.status_code}: {response.text}"
                logger.error(err_msg)
                return {
                    "success": False,
                    "status": "error",
                    "error": err_msg
                }
        except Exception as e:
            err_msg = f"Falha de conexão ao enviar e-mail via Resend: {str(e)}"
            logger.error(err_msg)
            return {
                "success": False,
                "status": "error",
                "error": err_msg
            }


def render_executive_email_template(
    report_data: Dict[str, Any],
    deep_link_url: str
) -> str:
    """
    Renderiza um parecer executivo enxuto, com foco em decisão e próximos passos.
    """
    structured = report_data.get("structured_data") or {}
    critic_feedback = report_data.get("critic_feedback")
    critic_approved = report_data.get("critic_approved") is True
    logger.info("Renderizando e-mail executivo (Aprovado=%s, Parecer do Crítico='%s')", critic_approved, critic_feedback)
    
    total_stranded = structured.get("total_stranded_cash")
    ruptura_count = structured.get("ruptura_count")
    criticos_count = structured.get("criticos_count")
    mkt_cats = structured.get("mkt_alert_categories", [])
    
    # Projeção de destravamento com 30% de desconto
    caixa_destravado = total_stranded * 1.35 if total_stranded is not None else None
    total_stranded_label = f"R$ {total_stranded:,.2f}" if total_stranded is not None else "Não disponível"
    risco_label = (
        f"{ruptura_count + criticos_count} SKUs"
        if ruptura_count is not None and criticos_count is not None
        else "Não disponível"
    )
    risco_detail = (
        f"{ruptura_count} em ruptura + {criticos_count} em risco"
        if ruptura_count is not None and criticos_count is not None
        else "Sem dados suficientes"
    )
    caixa_label = f"R$ {caixa_destravado:,.2f}" if caixa_destravado is not None else "Não disponível"

    badge_color = "#2F6F5E" if critic_approved else "#9A6700"
    badge_text = "ANÁLISE CONCLUÍDA" if critic_approved else "REVISÃO NECESSÁRIA"

    # Linhas dos top alertas
    top_critical_skus = structured.get("top_critical_skus", [])[:4]
    skus_rows_html = ""
    for s in top_critical_skus:
        skus_rows_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #D9DEE5; font-family: monospace; font-size: 13px; color: #2F6F5E;">{s.get('sku_id', 'SKU')}</td>
            <td style="padding: 10px; border-bottom: 1px solid #D9DEE5; font-size: 13px; color: #344054;">{s.get('nome_produto', 'Produto')}</td>
            <td style="padding: 10px; border-bottom: 1px solid #D9DEE5; font-size: 13px; color: #667085;">{s.get('categoria', '-')}</td>
            <td style="padding: 10px; border-bottom: 1px solid #D9DEE5; font-size: 13px; text-align: center; color: #B42318; font-weight: bold;">{s.get('estoque_disponivel', 0)} un.</td>
            <td style="padding: 10px; border-bottom: 1px solid #D9DEE5; font-size: 13px; text-align: right; color: #9A6700;">{s.get('dias_cobertura', 0)} dias</td>
        </tr>
        """

    if not skus_rows_html:
        skus_rows_html = """
        <tr>
            <td colspan="5" style="padding: 12px; text-align: center; color: #667085; font-size: 13px;">Nenhuma ruptura imediata detectada no fechamento.</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vértice Analytics — Parecer Executivo de Estoque</title>
</head>
<body style="margin: 0; padding: 0; background-color: #F2F4F7; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #17202A;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #F2F4F7; padding: 30px 10px;">
        <tr>
            <td align="center">
                <table width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: #FFFFFF; border: 1px solid #D9DEE5;">
                    
                    <!-- Cabeçalho -->
                    <tr>
                        <td style="padding: 28px 32px; background-color: #FFFFFF; border-bottom: 1px solid #D9DEE5;">
                            <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td>
                                        <div style="font-size: 11px; font-weight: 700; color: #667085; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 8px;">VÉRTICE RETAIL</div>
                                        <div style="font-size: 21px; font-weight: 650; color: #17202A;">Parecer executivo de estoque</div>
                                    </td>
                                    <td align="right">
                                <span style="display: inline-block; padding: 5px 9px; font-size: 10px; font-weight: 700; color: {badge_color}; border: 1px solid {badge_color};">{badge_text}</span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Corpo Principal -->
                    <tr>
                        <td style="padding: 30px 32px;">
                            <p style="font-size: 14px; line-height: 1.6; color: #344054; margin-top: 0; margin-bottom: 24px;">
                                Prezada Diretoria e Gestão de Supply Chain,<br><br>
                                Este parecer consolida os principais pontos de atenção identificados no fechamento de estoque e indica as prioridades para decisão.
                            </p>

                            <!-- Síntese executiva -->
                            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 28px;">
                                <tr>
                                    <td width="48%" style="background-color: #F8FAFC; border: 1px solid #D9DEE5; padding: 16px; vertical-align: top;">
                                        <div style="font-size: 11px; font-weight: 600; color: #667085; text-transform: uppercase;">Capital imobilizado</div>
                                        <div style="font-size: 22px; font-weight: 700; color: #17202A; margin: 4px 0;">{total_stranded_label}</div>
                                        <div style="font-size: 12px; color: #667085;">Em SKUs descontinuados</div>
                                    </td>
                                    <td width="4%"></td>
                                    <td width="48%" style="background-color: #F8FAFC; border: 1px solid #D9DEE5; padding: 16px; vertical-align: top;">
                                        <div style="font-size: 11px; font-weight: 600; color: #667085; text-transform: uppercase;">Ruptura e risco</div>
                                        <div style="font-size: 22px; font-weight: 700; color: #9A6700; margin: 4px 0;">{risco_label}</div>
                                        <div style="font-size: 12px; color: #667085;">{risco_detail}</div>
                                    </td>
                                </tr>
                                <tr><td height="12" colspan="3"></td></tr>
                                <tr>
                                    <td width="48%" style="background-color: #F8FAFC; border: 1px solid #D9DEE5; padding: 16px; vertical-align: top;">
                                        <div style="font-size: 11px; font-weight: 600; color: #667085; text-transform: uppercase;">Caixa potencial</div>
                                        <div style="font-size: 22px; font-weight: 700; color: #2F6F5E; margin: 4px 0;">{caixa_label}</div>
                                        <div style="font-size: 12px; color: #667085;">Com liquidação de 30%</div>
                                    </td>
                                    <td width="4%"></td>
                                    <td width="48%" style="background-color: #F8FAFC; border: 1px solid #D9DEE5; padding: 16px; vertical-align: top;">
                                        <div style="font-size: 11px; font-weight: 600; color: #667085; text-transform: uppercase;">Categorias em alerta</div>
                                        <div style="font-size: 17px; font-weight: 650; color: #17202A; margin: 7px 0;">{", ".join(mkt_cats) or "Nenhuma"}</div>
                                        <div style="font-size: 12px; color: #667085;">Marketing ativo com risco de estoque</div>
                                    </td>
                                </tr>
                            </table>

                            <!-- Seção de Alertas -->
                            <div style="font-size: 14px; font-weight: 700; color: #17202A; margin-bottom: 12px;">Prioridades de estoque</div>
                            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="border: 1px solid #D9DEE5; overflow: hidden; margin-bottom: 28px; background-color: #FFFFFF;">
                                <tr style="background-color: #F8FAFC;">
                                    <th align="left" style="padding: 10px; font-size: 11px; color: #667085; border-bottom: 1px solid #D9DEE5;">SKU</th>
                                    <th align="left" style="padding: 10px; font-size: 11px; color: #667085; border-bottom: 1px solid #D9DEE5;">PRODUTO</th>
                                    <th align="left" style="padding: 10px; font-size: 11px; color: #667085; border-bottom: 1px solid #D9DEE5;">CATEGORIA</th>
                                    <th align="center" style="padding: 10px; font-size: 11px; color: #667085; border-bottom: 1px solid #D9DEE5;">ESTOQUE</th>
                                    <th align="right" style="padding: 10px; font-size: 11px; color: #667085; border-bottom: 1px solid #D9DEE5;">COBERTURA</th>
                                </tr>
                                {skus_rows_html}
                            </table>

                            <!-- Botão CTA Deep Link -->
                            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 10px;">
                                <tr>
                                    <td align="center">
                                        <a href="{deep_link_url}" target="_blank" style="display: inline-block; background-color: #17202A; color: #FFFFFF; font-size: 14px; font-weight: 650; text-decoration: none; padding: 12px 24px;">
                                            Acessar Copiloto de Estoque no App &rarr;
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="padding-top: 10px;">
                                        <span style="font-size: 11px; color: #667085;">Abrir o contexto completo no aplicativo.</span>
                                    </td>
                                </tr>
                            </table>

                        </td>
                    </tr>

                    <!-- Rodapé -->
                    <tr>
                        <td style="padding: 20px 32px; background-color: #F8FAFC; border-top: 1px solid #D9DEE5; text-align: center;">
                            <div style="font-size: 11px; color: #667085; line-height: 1.5;">
                                Vértice Retail Analytics &bull; 2026<br>
                            </div>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
    return textwrap.dedent(html).strip()
