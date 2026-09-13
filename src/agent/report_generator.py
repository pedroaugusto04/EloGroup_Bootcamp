"""
src/agent/report_generator.py
Geração e formatação do parecer factual executivo em formato Markdown.
"""

from typing import Any, List


def _brl(value: Any) -> str:
    if value is None:
        return "não disponível"
    return "R$ " + f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _number(value: Any, decimals: int = 0) -> str:
    if value is None:
        return "não disponível"
    return f"{float(value):,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(value: Any) -> str:
    return "não disponível" if value is None else f"{_number(value, 1)}%"


def generate_inventory_audit_report(package: dict, recommendations: List[dict]) -> str:
    """Gera o parecer factual estruturado a partir do envelope de evidências reconciliado."""
    meta, summary = package["meta"], package["summary"]
    cap = summary["capital"]
    op = summary["operational"]
    exp = summary["lead_time_exposure"]
    liquidation = summary["liquidation"]
    central = liquidation["central_scenario"]
    discount_label = _pct(liquidation["desconto_pct"])
    sell_through_label = _pct(central["sell_through_pct"])
    top = summary.get("top_attention_category") or {}
    quality = summary["data_quality"]
    liquidation_leader = (liquidation.get("central_by_category") or [{}])[0]
    supplier_leader = (summary.get("supplier_exposure_summary") or [{}])[0]
    liquidation_leader_note = (
        "{} lidera a contribuição modelada do cenário central. Isso define o primeiro recorte para avaliação comercial, não comprova que o desconto de {} seja ótimo.".format(
            liquidation_leader["categoria"], discount_label
        )
        if liquidation_leader else "Nenhuma categoria tem dados financeiros válidos para o cenário selecionado."
    )

    scenario_rows = [
        "| Sell-through | Unidades | Capital envolvido | Receita ajustada | Contribuição estimada | Contrib./receita |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in liquidation["scenarios"]:
        scenario_rows.append(
            "| {sell}% | {units} | {capital} | {revenue} | {contribution} | {ratio} |".format(
                sell=row["sell_through_pct"], units=_number(row["unidades_cenario"]),
                capital=_brl(row["capital_historico_envolvido"]),
                revenue=_brl(row["receita_ajustada_devolucoes"]),
                contribution=_brl(row["contribuicao_estimada"]),
                ratio=_pct(row["contribuicao_sobre_receita_pct"]),
            )
        )

    category_rows = [
        "| Categoria | Ativos | Rupturas | No/abaixo do ponto | Expostos | Margem exposta | Alta cobertura | % dos ativos | Capital excedente |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary.get("category_summary", []):
        coverage_share = row["alta_cobertura"] / row["skus_ativos"] * 100 if row["skus_ativos"] else None
        category_rows.append(
            "| {category} | {active} | {stockout} | {reorder} | {exposed} | {margin} | {coverage} | {share} | {excess_cap} |".format(
                category=row["categoria"], active=row["skus_ativos"], stockout=row["ruptura_atual"],
                reorder=row["ponto_pedido"], exposed=row["exposicao_lead_time"],
                margin=_brl(row["margem_potencialmente_exposta"]),
                coverage=row["alta_cobertura"], share=_pct(coverage_share),
                excess_cap=_brl(row.get("capital_excedente")),
            )
        )

    sku_rows = [
        "| SKU | Produto | Categoria | Disponível | Demanda/dia | Déficit potencial | Margem exposta |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in package.get("items", [])[:10]:
        sku_rows.append(
            "| {sku} | {product} | {category} | {available} | {demand} | {deficit} | {margin} |".format(
                sku=row["sku_id"], product=row["nome_produto"], category=row["categoria"],
                available=_number(row["estoque_disponivel"]),
                demand=_number(row["demanda_diaria_historica"], 2),
                deficit=_number(row["deficit_potencial_unidades"], 2),
                margin=_brl(row["margem_potencialmente_exposta"]),
            )
        )

    overstock_sku_rows = [
        "| SKU | Produto | Categoria | Disponível | Demanda/dia | Cobertura | Capital excedente |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in (summary.get("top_overstock_skus") or [])[:5]:
        overstock_sku_rows.append(
            "| {sku} | {product} | {category} | {available} | {demand} | {coverage} dias | {excess_cap} |".format(
                sku=row["sku_id"], product=row["nome_produto"], category=row["categoria"],
                available=_number(row["estoque_disponivel"]),
                demand=_number(row["demanda_diaria_historica"], 2),
                coverage=_number(row["cobertura_dias_historica"]),
                excess_cap=_brl(row.get("capital_excedente")),
            )
        )
    liquidation_category_rows = [
        "| Categoria | Unidades | Capital envolvido | Receita ajustada | Contribuição estimada |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in liquidation.get("central_by_category", []):
        liquidation_category_rows.append(
            "| {category} | {units} | {capital} | {revenue} | {contribution} |".format(
                category=row["categoria"], units=_number(row["unidades_cenario"], 1),
                capital=_brl(row["capital_historico_envolvido"]),
                revenue=_brl(row["receita_ajustada_devolucoes"]),
                contribution=_brl(row["contribuicao_estimada"]),
            )
        )

    supplier_rows = [
        "| Fornecedor | SKUs expostos | Déficit potencial | Receita exposta | Margem exposta |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in summary.get("supplier_exposure_summary", [])[:10]:
        supplier_rows.append(
            "| {supplier} | {skus} | {deficit} | {revenue} | {margin} |".format(
                supplier=row["fornecedor_id"], skus=row["skus_expostos"],
                deficit=_number(row["deficit_potencial_unidades"], 2),
                revenue=_brl(row["receita_ajustada_exposta"]),
                margin=_brl(row["margem_potencialmente_exposta"]),
            )
        )

    decision_rows = [
        "| Prioridade | Horizonte | Iniciativa | Escopo inicial | Referência financeira |",
        "|---|---|---|---|---:|",
    ]
    decision_details = []
    for row in summary.get("decision_matrix", []):
        financial = _brl(row["financial_value"]) if row.get("financial_value") is not None else "Não estimada com segurança"
        decision_rows.append(
            "| {priority} | {horizon} | {initiative} | {scope} | {financial} |".format(
                priority=row["priority"], horizon=row["horizon"], initiative=row["initiative"],
                scope=row.get("scope") or "A definir", financial=financial,
            )
        )
        decision_details.extend([
            "### {} · {}".format(row["horizon"], row["initiative"]),
            "",
            "- **Decisão recomendada:** {}".format(row["decision"]),
            "- **Gate de decisão:** {}".format(row["decision_gate"]),
            "- **Esforço:** {}".format(row["effort"]),
            "",
        ])

    lines = [
        "# Copiloto de estoque baseado em tendência histórica de vendas",
        "",
        f"> {summary['methodology_banner']}",
        "",
        "## 1. Resumo executivo",
        "",
        f"- Capital físico coberto: **{_brl(cap['capital_fisico'])}**; reservado: **{_brl(cap['capital_reservado'])}**; disponível/liquidável: **{_brl(cap['capital_disponivel'])}**.",
        f"- Cobertura financeira: **{cap['skus_com_custo_vendas']} de {cap['total_skus']} SKUs**; {cap['skus_sem_custo_vendas']} ficaram fora do valuation por ausência de custo válido em Vendas.",
        "- Quantidades fora da cobertura financeira: **{} físicas**, **{} reservadas** e **{} disponíveis**.".format(
            _number(cap["unidades_fisicas_sem_cobertura"]),
            _number(cap["unidades_reservadas_sem_cobertura"]),
            _number(cap["unidades_disponiveis_sem_cobertura"]),
        ),
        f"- Posição operacional: **{op['ruptura_atual']} rupturas imediatas**, **{op['ponto_pedido']}** saldos no/abaixo do ponto e **{op['sem_venda_observada']}** SKUs sem venda recente.",
        "- Alta cobertura histórica (Sobre-estoque): **{} de {} SKUs ativos ({}) acima de {} dias**, imobilizando **{} em capital excedente** ({} unidades excedentes); sinaliza oportunidade primária de liberação de caixa e contenção de novas compras.".format(
            op["alta_cobertura"], op["active_skus"], _pct(op["high_coverage_share_active_pct"]),
            _number(op["coverage_threshold_days"]),
            _brl(op.get("capital_excedente")),
            _number(op.get("unidades_excedentes")),
        ),
        f"- Margem em risco (lead time): **{exp['skus']} SKUs ativos**, totalizando {_brl(exp['receita_ajustada_devolucao'])} de faturamento e {_brl(exp['margem_potencialmente_exposta'])} de margem sob risco de ruptura durante o lead time.",
        f"- Categoria com maior margem em risco: **{top.get('categoria', 'não disponível')}**.",
        "",
        "## 2. Receita, capital e margem de contribuição",
        "",
        "No cenário central de liquidação, a **receita líquida estimada** é de {}. O **custo histórico dos produtos envolvidos** é de {} e o frete estimado é de {}.".format(
            _brl(central["receita_ajustada_devolucoes"]), _brl(central["capital_historico_envolvido"]), _brl(central["frete_historico_estimado"])
        ),
        "A **margem de contribuição simulada** é de {}, correspondendo a {} da receita líquida e {} do capital recuperado.".format(
            _brl(central["contribuicao_estimada"]), _pct(central["contribuicao_sobre_receita_pct"]),
            _pct(central["contribuicao_sobre_capital_pct"]),
        ),
        "",
        "## 3. Simulação de liquidação de descontinuados",
        "",
        "Com **{} de desconto** e **{} de sell-through**:".format(discount_label, sell_through_label),
        "",
        "- Unidades no cenário: **{}**.".format(_number(central["unidades_cenario"])),
        "- Capital histórico envolvido: **{}**.".format(_brl(central["capital_historico_envolvido"])),
        "- Receita bruta simulada: **{}**.".format(_brl(central["receita_antes_devolucoes"])),
        "- Ajuste estimado por devoluções: **-{}**.".format(_brl(central["ajuste_estimado_devolucoes"])),
        "- Receita líquida estimada: **{}**.".format(_brl(central["receita_ajustada_devolucoes"])),
        "- Frete histórico estimado: **-{}**.".format(_brl(central["frete_historico_estimado"])),
        "- Margem de contribuição simulada: **{}**.".format(_brl(central["contribuicao_estimada"])),
        "",
        "### Sensibilidade ao sell-through",
        "",
        *scenario_rows,
        "",
        "### Cenário central por categoria",
        "",
        *liquidation_category_rows,
        "",
        liquidation_leader_note,
        "",
        "## 4. Onde está a atenção operacional",
        "",
        "### Resumo por categoria",
        "",
        *category_rows,
        "",
        "### Dez SKUs ativos com maior margem em risco",
        "",
        *sku_rows,
        "",
        "### Cinco SKUs ativos com maior capital imobilizado em sobre-estoque",
        "",
        *overstock_sku_rows,
        "",
        "### Fornecedores com maior margem em risco",
        "",
        *supplier_rows,
        "",
        f"A visão conjunta contrapõe o risco imediato de perda de margem por sob-estoque ({_brl(exp['margem_potencialmente_exposta'])}) ao custo de carregamento do sobre-estoque ativo ({_brl(op.get('capital_excedente'))}), orientando o autofinanciamento de reposição via congelamento de compras OTB.",
        "",
        "## 5. Como os valores foram calculados",
        "",
        "- **Custo unitário de valuation:** custo ponderado de aquisição apurado no histórico de Vendas.",
        "- **Demanda diária:** média de unidades diárias observadas na janela ({meta_days} dias).".format(meta_days=meta["days"]),
        "- **Déficit potencial:** necessidade estimada no lead time cadastral deduzida do saldo disponível.",
        "- **Liquidação:** preço histórico com desconto, ajustado pela devolução da categoria e deduzido de custos/frete.",
        "- **Auditoria cadastral:** {coverage_skus} SKUs descontinuados elegíveis para o modelo de liquidação.".format(
            coverage_skus=liquidation["skus_elegiveis"],
        ),
        "",
        "## 6. Plano de Ação · Quick Wins e Recomendações",
        "",
        "Ações priorizadas com base nos itens críticos identificados no diagnóstico de estoque:",
        "",
        *decision_rows,
        "",
        *decision_details,
        "## 7. Próximos Passos (Quick Wins & Estrutural)",
        "",
    ]

    agent_next_steps = package.get("agent_next_steps")
    agent_exec_summary = package.get("agent_executive_summary")

    if agent_exec_summary:
        lines.extend([
            f"> **Parecer Executivo do Agente:** {agent_exec_summary}",
            "",
        ])

    if agent_next_steps:
        lines.extend([agent_next_steps.strip(), ""])
    elif recommendations:
        for rec in recommendations:
            horizon = rec.get("horizon", "30 dias")
            init = rec.get("initiative", "Ação Prioritária")
            rec_text = rec.get("recommendation", "")
            lines.append(f"- **{horizon} ({init}):** {rec_text}")
        lines.append("")
    else:
        lines.extend([
            "- **Quick Wins (30 dias):** Iniciar liquidação focada na categoria **{}** ({}) e reposição emergencial dos **{} SKUs ativos em risco** (foco em **{}** e fornecedor **{}**).".format(
                liquidation_leader.get("categoria", "categoria líder"),
                _brl(liquidation_leader.get("contribuicao_estimada")), exp["skus"],
                top.get("categoria", "categoria líder"), supplier_leader.get("fornecedor_id", "líder"),
            ),
            "- **Médio Prazo (60 dias):** Recalibrar regras de ponto de pedido e suspender compras OTB para os {} SKUs ativos com cobertura excessiva (>{} dias), visando liberar até {} em capital imobilizado.".format(
                op["alta_cobertura"], _number(op["coverage_threshold_days"]), _brl(op.get("capital_excedente")),
            ),
            "- **Governança (90 dias):** Implementar snapshots sistemáticos de estoque e rastreamento de lead time real por fornecedor.",
            "",
        ])

    if recommendations:
        lines.extend(["## Hipóteses e Recomendações Estruturadas do Agente", ""])
        for rec in recommendations:
            horizon = rec.get("horizon", "Horizonte não informado")
            rec_body = rec.get("recommendation") or rec.get("decision", "")
            evidence = rec.get("evidence", "Não informada")
            confidence = rec.get("confidence", "Alta")
            caveat = rec.get("caveat", "Ressalva não informada")
            impact = rec.get("financial_impact")
            impact_text = f" | Impacto Financeiro: {_brl(impact) if isinstance(impact, (int, float)) else impact}" if impact else ""
            lines.append(
                f"- **{horizon} — {rec_body}** Evidência: `{evidence}`. "
                f"Confiança: {confidence}. Ressalva: {caveat}{impact_text}"
            )
    return "\n".join(lines)


__all__ = ["generate_inventory_audit_report"]
