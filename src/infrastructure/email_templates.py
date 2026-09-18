"""
src/infrastructure/email_templates.py
Templates e renderizadores HTML para comunicação executiva por e-mail.
"""

import html
from typing import Any, Dict


def _format_currency_brl(value: Any) -> str:
    if value is None:
        return "Não disponível"
    return "R$ " + f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _format_percentage(value: Any) -> str:
    if value is None:
        return "não disponível"
    return f"{float(value):,.1f}%".replace(".", ",")


def render_executive_email_template(report_data: Dict[str, Any], deep_link_url: str) -> str:
    """Renderiza apenas valores reconciliados do envelope de evidências para o e-mail executivo."""
    package = report_data.get("factual_package") or {}
    structured = package.get("summary") or report_data.get("structured_data") or {}
    meta = package.get("meta") or report_data.get("meta") or {}
    capital = structured.get("capital") or {}
    operational = structured.get("operational") or {}
    exposure = structured.get("lead_time_exposure") or {}
    overstock = structured.get("overstock_exposure") or {}
    liquidation = structured.get("liquidation") or {}
    central = liquidation.get("central_scenario") or {}
    discount_pct = liquidation.get("desconto_pct")
    sell_through_pct = central.get("sell_through_pct")
    top = structured.get("top_attention_category") or {}
    banner = structured.get("methodology_banner") or (
        ""
        f"Tendência de vendas observada entre {meta.get('sales_start', '?')} e {meta.get('sales_end', '?')}."
    )
    approved = report_data.get("deterministic_approved") is True
    badge = "RELATÓRIO EXECUTIVO" if approved else "RELATÓRIO EM REVISÃO"

    overstock_val = overstock.get("capital_excedente")
    if overstock_val is None:
        overstock_val = operational.get("capital_excedente")
    overstock_skus = overstock.get("skus")
    if overstock_skus is None:
        overstock_skus = operational.get("alta_cobertura", 0)

    # Tabela 1: Top SKUs em Sobre-estoque (Capital Imobilizado)
    overstock_items = structured.get("top_overstock_skus") or package.get("queues", {}).get("alta_cobertura") or []
    overstock_rows = ""
    for item in overstock_items[:5]:
        cov_val = float(item.get("cobertura_dias_historica") or 0)
        cov_text = f"{cov_val:,.0f} dias".replace(",", ".") if cov_val > 0 else "—"
        overstock_rows += (
            "<tr>"
            f"<td>{html.escape(str(item.get('sku_id', '—')))}</td>"
            f"<td>{html.escape(str(item.get('nome_produto', '—')))}</td>"
            f"<td>{html.escape(str(item.get('categoria', '—')))}</td>"
            f"<td>{html.escape(cov_text)}</td>"
            f"<td>{_format_currency_brl(item.get('capital_excedente'))}</td>"
            "</tr>"
        )
    if not overstock_rows:
        overstock_rows = '<tr><td colspan="5">Nenhum item com sobre-estoque identificado.</td></tr>'

    # Tabela 2: SKUs Críticos com Margem em Risco (Risco de Ruptura)
    rows = ""
    for item in (package.get("items") or [])[:5]:
        rows += (
            "<tr>"
            f"<td>{html.escape(str(item.get('sku_id', '—')))}</td>"
            f"<td>{html.escape(str(item.get('nome_produto', '—')))}</td>"
            f"<td>{html.escape(str(item.get('categoria', '—')))}</td>"
            f"<td>{_format_currency_brl(item.get('margem_potencialmente_exposta'))}</td>"
            "</tr>"
        )
    if not rows:
        rows = '<tr><td colspan="4">Nenhum item elegível no período.</td></tr>'

    decision_items = ""
    recs = report_data.get("recommendations") or []
    if recs:
        for item in recs:
            gate_text = item.get("caveat") or item.get("decision_gate") or item.get("evidence", "—")
            decision_items += (
                '<div class="decision-item">'
                f'<strong>{html.escape(str(item.get("horizon", "—")))} · {html.escape(str(item.get("initiative", "Recomendação do Agente")))}</strong>'
                f'<p>{html.escape(str(item.get("recommendation", item.get("decision", "—"))))}</p>'
                f'<small>Gate: {html.escape(str(gate_text))}</small>'
                "</div>"
            )
    else:
        for item in structured.get("decision_matrix", []):
            decision_items += (
                '<div class="decision-item">'
                f'<strong>{html.escape(str(item.get("horizon", "—")))} · {html.escape(str(item.get("initiative", "—")))}</strong>'
                f'<p>{html.escape(str(item.get("decision", "—")))}</p>'
                f'<small>Gate: {html.escape(str(item.get("decision_gate", "—")))}</small>'
                "</div>"
            )

    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width">
<title>Predictive Inventory Advisor · Vértice Retail</title>
<style>
body{{background:#f3f3f7;color:#131920;font-family:Arial,sans-serif;margin:0;padding:0}}
main{{background:#fff;border:1px solid #dedee3;border-radius:12px;margin:24px auto;max-width:680px;padding:28px}}
h1{{font-size:24px;line-height:1.2;margin:10px 0 18px;color:#18181b}} h2{{color:#2e0854;font-size:17px;margin:22px 0 10px}}
.eyebrow{{color:#4200db;font-size:11px;font-weight:700;letter-spacing:.08em}}
.banner{{background:#f7f5ff;border-left:4px solid #4200db;border-radius:6px;color:#333843;line-height:1.5;padding:12px 14px;font-size:13px}}
.metric-grid{{border-collapse:separate;border-spacing:10px;margin:14px -10px 20px;table-layout:fixed;width:calc(100% + 20px)}}
.metric-grid td{{border:0;padding:0;vertical-align:top;width:50%}}
.card{{background:#fcfcfd;border:1px solid #dedee3;border-radius:10px;box-sizing:border-box;min-height:130px;padding:16px}}
.card h2{{font-size:20px;line-height:1.15;margin:8px 0;color:#2e0854}}.card p{{color:#52525b;font-size:12px;line-height:1.45;margin:0}}
.card-capital{{background:#f7f5ff;border-top:3px solid #4200db}}.card-overstock{{background:#fffbf7;border-top:3px solid #d97706}}
.card-exposure{{background:#faf9ff;border-top:3px solid #8575ff}}.card-liquidation{{background:#f4f0ff;border-top:3px solid #35009e}}
small{{color:#52525b;font-size:11px;font-weight:600}}.priorities{{border-collapse:collapse;width:100%;margin-bottom:15px}}.priorities th,.priorities td{{border-bottom:1px solid #dedee3;padding:9px;text-align:left;font-size:12px}}
.priorities th{{background:#f7f5ff;color:#2e0854;font-weight:700}}.decision-item{{background:#faf9fc;border-left:3px solid #8575ff;margin:10px 0;padding:12px 14px;border-radius:0 6px 6px 0}}.decision-item strong{{color:#2e0854;font-size:13px}}.decision-item p{{font-size:12px;line-height:1.5;margin:5px 0;color:#27272a}}
.cta-btn{{background-color:#2e0854 !important;border:1px solid #1f0538;border-radius:8px;color:#ffffff !important;display:inline-block;font-size:14px;font-weight:700;padding:14px 24px;text-decoration:none;text-align:center;box-shadow:0 2px 4px rgba(0,0,0,0.1)}}
@media only screen and (max-width:600px){{main{{border-radius:0;margin:0;padding:20px}}.metric-grid,.metric-grid tbody,.metric-grid tr,.metric-grid td{{display:block;width:100%}}.metric-grid{{margin:12px 0}}.metric-grid td{{margin-bottom:10px}}.card{{min-height:0}}}}
</style></head>
<body><main>
<div class="eyebrow">VÉRTICE RETAIL · {badge}</div>
<h1>Predictive Inventory Advisor</h1>
<p class="banner">{html.escape(banner)}</p>
<table class="metric-grid" role="presentation"><tbody>
  <tr>
    <td><div class="card card-capital"><small>CAPITAL DISPONÍVEL COBERTO</small><h2>{_format_currency_brl(capital.get("capital_disponivel"))}</h2><p>{capital.get("skus_com_custo_vendas", 0)} SKUs com custo histórico em Vendas.</p></div></td>
    <td><div class="card card-overstock"><small>SOBRE-ESTOQUE ATIVO (ALTA COBERTURA)</small><h2>{_format_currency_brl(overstock_val)}</h2><p>{overstock_skus} SKUs ativos com capital imobilizado (>120 dias).</p></div></td>
  </tr>
  <tr>
    <td><div class="card card-exposure"><small>MARGEM EM RISCO (LEAD TIME)</small><h2>{exposure.get("skus", 0)} SKUs ativos</h2><p>{_format_currency_brl(exposure.get("margem_potencialmente_exposta"))} em risco de ruptura durante o lead time.</p></div></td>
    <td><div class="card card-liquidation"><small>SIMULAÇÃO DE LIQUIDAÇÃO · {_format_percentage(discount_pct)} DESC. · {_format_percentage(sell_through_pct)} SELL-THROUGH</small><h2>{_format_currency_brl(central.get("contribuicao_estimada"))}</h2><p>Margem de contribuição simulada (Receita líq.: {_format_currency_brl(central.get("receita_ajustada_devolucoes"))}; Custo hist.: {_format_currency_brl(central.get("capital_historico_envolvido"))}).</p></div></td>
  </tr>
</tbody></table>
<h2>Top SKUs em Sobre-estoque (Capital Imobilizado)</h2>
<table class="priorities"><thead><tr><th>SKU</th><th>Produto</th><th>Categoria</th><th>Cobertura</th><th>Capital Excedente</th></tr></thead><tbody>{overstock_rows}</tbody></table>
<h2>SKUs Críticos com Margem em Risco (Lead Time)</h2>
<table class="priorities"><thead><tr><th>SKU</th><th>Produto</th><th>Categoria</th><th>Margem em Risco</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Plano de Ação · Quick Wins e Recomendações</h2>
<div class="decision-list">{decision_items}</div>
<p><small>Sinais operacionais: {operational.get('alta_cobertura', 0)} SKUs em sobre-estoque · {operational.get('ruptura_atual', 0)} rupturas imediatas · {operational.get('ponto_pedido', 0)} no/abaixo do ponto de pedido.</small></p>
<div style="margin-top:24px;margin-bottom:8px;text-align:center;">
  <a class="cta-btn" href="{html.escape(deep_link_url, quote=True)}" target="_blank" style="background-color:#2e0854;border:1px solid #1f0538;border-radius:8px;color:#ffffff !important;display:inline-block;font-size:14px;font-weight:700;padding:14px 24px;text-decoration:none;text-align:center;">
    <span style="color:#ffffff !important;font-weight:700;">Ver Relatório Completo na Plataforma →</span>
  </a>
</div>
</main></body></html>"""
