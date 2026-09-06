"""
src/api/routes/roadmap.py
Rotas do Plano Estratégico 30/60/90 Dias e Matriz de Priorização Executiva.
"""

from fastapi import APIRouter

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
        "id": "init-02",
        "title": "Liquidação para Queima de Estoque Descontinuado",
        "hypothesis": "Hipótese 6 (Decisão & Estoque)",
        "type": "Quick Win (Curto Prazo)",
        "horizon": "30 Dias",
        "financial_impact_label": "R$ 14.775.347,64 (Capital Parado)",
        "financial_impact_value": 14775347,
        "effort_days": 20,
        "category": "Estoque",
        "description": "Campanha promocional de liquidação para liberar o capital travado em 207 SKUs descontinuados e convertê-los em liquidez imediata para o fluxo de caixa.",
        "metrics_to_watch": ["Capital liberado (R$)", "Giro de estoque descontinuado", "Espaço em armazém WMS"]
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
        "category": "CRM & Vendas",
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
        "id": "init-05",
        "title": "Priorização de Investimento em Influenciadores",
        "hypothesis": "Hipótese 5 (Segmentação)",
        "type": "Médio Prazo",
        "horizon": "60 Dias",
        "financial_impact_label": "Maior Ticket Médio (R$ 901,91) & Margem 52,3%",
        "financial_impact_value": 1200000,
        "effort_days": 50,
        "category": "Marketing",
        "description": "Realocação do orçamento de mídia para o canal de Influenciadores, que apresenta o maior ticket médio da base e margem saudável, apesar de maior desconto.",
        "metrics_to_watch": ["ROAS real no ERP", "Ticket médio por canal", "LTV dos clientes adquiridos"]
    },
    {
        "id": "init-06",
        "title": "Ajuste no Mecanismo de Compras e Alertas de Ruptura",
        "hypothesis": "Hipótese 6 (Decisão & Estoque)",
        "type": "Médio / Longo Prazo",
        "horizon": "90 Dias",
        "financial_impact_label": "R$ 7.250.310,60 (Risco de Ruptura)",
        "financial_impact_value": 7250310,
        "effort_days": 70,
        "category": "Estoque",
        "description": "Revisão dos parâmetros de ponto de pedido e lead time para os 701 SKUs que operam em nível crítico (especialmente na categoria Beleza), evitando faltas de produtos de alto giro.",
        "metrics_to_watch": ["Taxa de ruptura (%)", "SKUs abaixo do ponto de pedido", "Perdas de vendas por indisponibilidade"]
    },
    {
        "id": "init-07",
        "title": "Auditoria de Integridade & Unificação ERP x CRM",
        "hypothesis": "Integridade das Bases",
        "type": "Médio / Longo Prazo",
        "horizon": "90 Dias",
        "financial_impact_label": "Confiabilidade Decisória C-Level",
        "financial_impact_value": 500000,
        "effort_days": 60,
        "category": "Engenharia de Dados",
        "description": "Estruturação de pipeline de reconciliação de dados entre o ERP de Vendas e o CRM de Clientes/Suporte para sanar discrepâncias de cobertura e clientes desbalanceados.",
        "metrics_to_watch": ["Taxa de conciliação CRM x ERP", "Cobertura de IDs de clientes", "Precisão de LTV"]
    }
]


@router.get("/initiatives")
def get_roadmap_initiatives():
    return {
        "initiatives": STRATEGIC_INITIATIVES,
        "summary": {
            "total_initiatives": len(STRATEGIC_INITIATIVES),
            "quick_wins_count": len([i for i in STRATEGIC_INITIATIVES if "Quick Win" in i["type"]]),
            "total_potential_value": sum(i["financial_impact_value"] for i in STRATEGIC_INITIATIVES)
        }
    }
