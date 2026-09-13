"""
src/api/routes/roadmap.py
Rotas do Plano Estratégico 30/60/90 Dias e Matriz de Priorização Executiva.
"""

from fastapi import APIRouter

from src.agent.inventory_analytics import build_audit_package
from src.infrastructure.database import DuckDBRepository

router = APIRouter(prefix="/roadmap", tags=["roadmap"])

# Matriz estritamente alinhada às conclusões de DEVELOPMENT.md
STRATEGIC_INITIATIVES = [
    {
        "id": "init-01",
        "title": "Notificações de Status do Pedido via WhatsApp/E-mail",
        "hypothesis": "Hipótese 4 (Atendimento)",
        "type": "Quick Win (Curto Prazo)",
        "horizon": "30 Dias",
        "financial_impact_label": "R$ 159.660,00 (Custo Evitável)",
        "financial_impact_value": 159660,
        "effort_days": 15,
        "category": "Suporte & IA",
        "description": "Uma única mensagem proativa de WhatsApp após a compra com link de rastreamento direto para sanar a ansiedade do cliente e evitar chamadas de 'Onde está meu pedido' (30% dos chamados).",
        "metrics_to_watch": ["Volume de chamados 'Onde está meu pedido'", "Custo operacional de suporte", "CSAT inicial"]
    },
    {
        "id": "init-03",
        "title": "Ação Rápida de Reativação para Clientes 'Em Risco'",
        "hypothesis": "Hipótese 5 (Segmentação)",
        "type": "Curto / Médio Prazo",
        "horizon": "60 Dias",
        "financial_impact_label": "Proteção de Recompra (46,7% da base)",
        "financial_impact_value": 650000,
        "effort_days": 30,
        "category": "Clientes & Vendas",
        "description": "Disparo automatizado de e-mails com cupons segmentados para incentivar segunda e terceira compras em clientes das faixas 'Em Risco' e 'Hibernando'.",
        "metrics_to_watch": ["Taxa de recompra", "Conversão de cupons", "Taxa de retenção RFM"]
    },
    {
        "id": "init-04",
        "title": "Melhorias de FAQ / Páginas de Produto & Atendimento IA",
        "hypothesis": "Hipótese 4 (Atendimento)",
        "type": "Médio Prazo",
        "horizon": "60 Dias",
        "financial_impact_label": "R$ 78.888,00 (Custo Evitável)",
        "financial_impact_value": 78888,
        "effort_days": 45,
        "category": "Suporte & IA",
        "description": "Enriquecimento das páginas de produtos com especificações detalhadas e implantação de agente de triagem por IA generativa via WhatsApp para resolução de dúvidas técnicas.",
        "metrics_to_watch": ["Volume de chamados técnicos", "Taxa de resolução no primeiro contato (FCR)", "CSAT de suporte"]
    },
    {
        "id": "init-06",
        "title": "Governança & Unificação das 5 Bases de Dados (MDM / Lakehouse)",
        "hypothesis": "Integridade das Bases",
        "type": "Médio / Longo Prazo",
        "horizon": "90 Dias",
        "financial_impact_label": "Confiabilidade Decisória C-Level",
        "financial_impact_value": 500000,
        "effort_days": 60,
        "category": "Engenharia de Dados",
        "description": "Estruturação de pipeline unificado (Single Source of Truth) integrando as 5 fontes do ecossistema (Vendas, Clientes, Atendimento, Estoque e Marketing), sanando descompassos de atribuição de mídia, custos de catálogo e conciliação de clientes.",
        "metrics_to_watch": [
            "Taxa de conciliação global entre bases (%)",
            "Precisão do ROAS e LTV contábil",
            "Cobertura unificada de IDs de clientes e SKUs"
        ]
    }
]


@router.get("/initiatives")
def get_roadmap_initiatives():
    package = build_audit_package(DuckDBRepository(), "full_history")
    summary = package["summary"]
    capital = summary["capital"]
    exposure = summary["lead_time_exposure"]
    liquidation = summary["liquidation"]["central_scenario"]
    dynamic_inventory = [
        {
            "id": "init-02",
            "title": "Análise de Liquidação de Estoque Descontinuado",
            "hypothesis": "Hipótese 6 (Decisão & Estoque)",
            "type": "Quick Win (Curto Prazo)",
            "horizon": "30 Dias",
            "financial_impact_label": f"R$ {liquidation['receita_ajustada_devolucoes']:,.2f} (Receita no cenário central)",
            "financial_impact_value": liquidation["receita_ajustada_devolucoes"],
            "effort_days": 20,
            "category": "Estoque",
            "description": (
                f"Avaliar liquidação dos {capital['descontinuados_valorados']} SKUs descontinuados valorados. "
                "O cenário central usa 30% de desconto e 50% de sell-through; não representa caixa realizado."
            ),
            "metrics_to_watch": ["Receita estimada no cenário", "Capital disponível envolvido", "Sell-through"],
        },
        {
            "id": "init-05",
            "title": "Revisão de Parâmetros e Exposição no Lead Time",
            "hypothesis": "Hipótese 6 (Decisão & Estoque)",
            "type": "Médio / Longo Prazo",
            "horizon": "90 Dias",
            "financial_impact_label": f"R$ {exposure['margem_potencialmente_exposta']:,.2f} (Cenário de margem exposta)",
            "financial_impact_value": exposure["margem_potencialmente_exposta"],
            "effort_days": 70,
            "category": "Estoque",
            "description": (
                f"Revisar pontos de pedido e lead times cadastrais dos {exposure['skus']} SKUs ativos expostos. "
                "A métrica usa tendência histórica e prioriza investigação, sem emitir ordens de compra."
            ),
            "metrics_to_watch": ["Ruptura atual", "SKUs no/abaixo do ponto", "Margem potencialmente exposta"],
        },
    ]
    initiatives = [*STRATEGIC_INITIATIVES, *dynamic_inventory]
    return {
        "meta": package["meta"],
        "initiatives": initiatives,
        "summary": {
            "total_initiatives": len(initiatives),
            "quick_wins_count": len([i for i in initiatives if "Quick Win" in i["type"]]),
            "total_potential_value": sum(i["financial_impact_value"] for i in initiatives),
            "inventory_scenario_value": liquidation["receita_ajustada_devolucoes"] + exposure["margem_potencialmente_exposta"],
        }
    }
