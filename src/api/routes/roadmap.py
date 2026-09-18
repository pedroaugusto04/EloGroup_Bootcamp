"""
src/api/routes/roadmap.py
Rotas do Plano Estratégico, Matriz de Priorização Executiva,
Business Case Consolidado, Governança de Riscos e Racional de Sequenciamento.
"""

from fastapi import APIRouter

from src.agent.inventory_analytics import build_audit_package
from src.infrastructure.database import DuckDBRepository

router = APIRouter(prefix="/roadmap", tags=["roadmap"])

# Matriz estritamente alinhada aos Slides Executivos (Slides 06 a 13 e Slides Auxiliares A1-A4)
# e aos Relatórios de Diagnóstico Estratégico e Modelagem Financeira.

TIMELINE_PHASES = [
    {
        "phase": "Dia 30",
        "title": "Dados e Estoque",
        "focus": "Operação assistida, liquidação de descontinuados e ajuste de parâmetros",
        "squad": "Equipe de Dados e Operações",
        "dependencies": "Conexão com DuckDB e conciliação de saldos operacionais",
        "tracking_criteria": "Recomendações válidas, sell-through e receita realizada",
        "deliverables": [
            {
                "agent": "Agente 1 (Estoque)",
                "scope": "Piloto de liquidação dos 206 SKUs descontinuados com meta de 50% de sell-through e trava para novas compras.",
                "badge": "Piloto Operacional"
            },
            {
                "agent": "Agente 2 (Margem)",
                "scope": "Parametrização de tetos de desconto por SKU a partir de custo histórico, frete e devoluções.",
                "badge": "Preparação"
            },
            {
                "agent": "Agente 3 (Atendimento)",
                "scope": "Montagem da base de dúvidas técnicas de produtos e mapeamento dos eventos de entrega das transportadoras.",
                "badge": "Preparação"
            }
        ]
    },
    {
        "phase": "Dia 60",
        "title": "Logística e CX",
        "focus": "Envio de mensagens proativas, teste com teto de desconto e ajuste de lead time",
        "squad": "Equipe Comercial e de CX",
        "dependencies": "Cadastro de tetos no ERP e integração de mensagens por WhatsApp",
        "tracking_criteria": "Descontos acima do teto, volume diário de vendas e redução de chamados de rastreio",
        "deliverables": [
            {
                "agent": "Agente 1 (Estoque)",
                "scope": "Ajuste do ponto de pedido para os 701 SKUs ativos expostos durante o prazo de entrega dos fornecedores.",
                "badge": "Calibração"
            },
            {
                "agent": "Agente 2 (Margem)",
                "scope": "Teste piloto limitando descontos ao teto de 15% para proteger a margem sem perder volume.",
                "badge": "Piloto Operacional"
            },
            {
                "agent": "Agente 3 (Atendimento)",
                "scope": "Início dos alertas automáticos de rastreio via WhatsApp e e-mail e piloto supervisionado de suporte.",
                "badge": "Piloto Operacional"
            }
        ]
    },
    {
        "phase": "Dia 90",
        "title": "IA e Atendimento",
        "focus": "Expansão para todo o catálogo e autoatendimento com suporte humano sob demanda",
        "squad": "Equipe de CX e Tecnologia",
        "dependencies": "Base de dúvidas homologada e regras de contingência ativas",
        "tracking_criteria": "Mais de 60% de dúvidas resolvidas sem recontato em 7 dias e satisfação do cliente estável",
        "deliverables": [
            {
                "agent": "Agente 1 (Estoque)",
                "scope": "Auditoria contínua de compras e relatórios automáticos de estoque.",
                "badge": "Produção"
            },
            {
                "agent": "Agente 2 (Margem)",
                "scope": "Aplicação do teto de desconto de 15% em 100% dos produtos do catálogo.",
                "badge": "Produção"
            },
            {
                "agent": "Agente 3 (Atendimento)",
                "scope": "Autoatendimento com IA para dúvidas técnicas com encaminhamento para equipe humana.",
                "badge": "Produção"
            }
        ]
    }
]

RISK_MATRIX = [
    {
        "front": "Estoque e descontinuados",
        "kpi_target": "≥90% de recomendações válidas e zero recompra de descontinuados.",
        "mitigation_action": "Ajustar regras no banco de dados e bloquear pedidos inválidos automaticamente."
    },
    {
        "front": "Descontos e margem",
        "kpi_target": "Corte de 50% nos descontos acima de 20%, sem queda superior a 5% no volume.",
        "mitigation_action": "Revisar margem líquida por SKU considerando frete e devoluções para calibrar os limites."
    },
    {
        "front": "Rastreio proativo",
        "kpi_target": "Queda de 30% nos chamados sobre localização de pedidos em 30 dias.",
        "mitigation_action": "Verificar se as mensagens estão sendo entregues e tornar o status do pedido mais claro."
    },
    {
        "front": "Atendimento automatizado",
        "kpi_target": "Mais de 60% de chamados resolvidos sem recontato em 7 dias.",
        "mitigation_action": "Ajustar as respostas da IA e direcionar casos duvidosos direto para operadores."
    }
]

SEQUENCING_RATIONALE = {
    "title": "Por que Marketing e CRM ficam para a segunda fase",
    "subtitle": "Antes de investir em campanhas ou réguas de clientes, é preciso corrigir os cadastros de checkout e vendas.",
    "marketing": {
        "title": "Marketing e Mídia Paga",
        "highlight_number": "38,2M",
        "highlight_label": "conversões registradas na mídia em 2023",
        "divergence": "O ERP registra 76,9 mil pedidos faturados no ano, sem identificação de campanha ou rastreamento de canal nos pedidos.",
        "next_step": "Integrar o checkout com as ferramentas de mídia para acompanhar pedidos e margem real antes de mexer na verba."
    },
    "crm": {
        "title": "CRM e Base de Clientes",
        "highlight_number": "346 de 15 mil",
        "highlight_label": "clientes cadastrados aparecem no histórico de vendas",
        "divergence": "40,6% dos pedidos estão atribuídos a um único cliente, e o histórico de compras não bate com o faturamento.",
        "next_step": "Consolidar o cadastro de clientes e recalcular o histórico antes de criar incentivos por segmento."
    },
    "c_level_takeaway": "O diagnóstico aponta os gargalos. A otimização em mídia e CRM só trará retorno seguro quando o cadastro e o checkout estiverem unificados."
}


@router.get("/initiatives")
def get_roadmap_initiatives():
    package = build_audit_package(DuckDBRepository(), "full_history")
    summary = package["summary"]
    capital = summary["capital"]
    exposure = summary["lead_time_exposure"]
    liquidation = summary["liquidation"]["central_scenario"]

    initiatives = [
        {
            "id": "init-01",
            "title": "Liquidação assistida de itens descontinuados",
            "hypothesis": "Hipótese 1 e 6 (Estoque parado)",
            "type": "Quick Win",
            "horizon": "30 Dias",
            "financial_impact_label": f"R$ {liquidation['receita_ajustada_devolucoes']:,.2f} (Receita líquida no cenário central)",
            "financial_impact_value": liquidation["receita_ajustada_devolucoes"],
            "effort_days": 20,
            "category": "Estoque",
            "description": (
                f"Liquidar os {capital['descontinuados_valorados']} SKUs descontinuados com 50% de sell-through "
                f"e desconto de 30%, bloqueando novas recompras no sistema."
            ),
            "metrics_to_watch": ["Sell-through do lote", "Receita líquida realizada", "Zero recompras de descontinuados"],
        },
        {
            "id": "init-02",
            "title": "Definição de tetos de desconto por categoria",
            "hypothesis": "Hipótese 2 (Margem e descontos)",
            "type": "30 Dias",
            "horizon": "30 Dias",
            "financial_impact_label": "Preparação da trava de margem",
            "financial_impact_value": 0,
            "effort_days": 25,
            "category": "Preço e Margem",
            "description": (
                "Calcular os limites de desconto por SKU a partir de custo, frete histórico e taxa de devolução "
                "para apoiar o piloto de controle de margem."
            ),
            "metrics_to_watch": ["Tetos calculados por categoria", "Aderência comercial às regras", "Cobertura de produtos"],
        },
        {
            "id": "init-03",
            "title": "Mapeamento de rastreio e base técnica de produtos",
            "hypothesis": "Hipótese 3 e 4 (Suporte e atendimento)",
            "type": "30 Dias",
            "horizon": "30 Dias",
            "financial_impact_label": "Preparação para reduzir chamados",
            "financial_impact_value": 0,
            "effort_days": 20,
            "category": "Atendimento",
            "description": (
                "Organizar as respostas para as principais dúvidas técnicas de produtos e mapear os eventos "
                "de entrega das transportadoras para envio automático de status."
            ),
            "metrics_to_watch": ["Base de dúvidas homologada", "Alertas de transporte ativos", "Confiabilidade dos eventos"],
        },
        {
            "id": "init-04",
            "title": "Piloto de teto de desconto em 15%",
            "hypothesis": "Hipótese 2 (Margem e descontos)",
            "type": "Quick Win",
            "horizon": "60 Dias",
            "financial_impact_label": "R$ 1.800.000,00/ano (Margem recuperada)",
            "financial_impact_value": 1800000,
            "effort_days": 45,
            "category": "Preço e Margem",
            "description": (
                "Limitar descontos excessivos ao teto de 15% em grupo piloto. "
                "O teste estatístico mostrou que a redução de desconto não afeta o volume de unidades vendidas."
            ),
            "metrics_to_watch": ["Margem cedida acima do teto", "Volume diário de vendas", "Margem de contribuição por SKU"],
        },
        {
            "id": "init-05",
            "title": "Alertas automáticos de rastreio via WhatsApp e e-mail",
            "hypothesis": "Hipótese 4 (Atendimento e CX)",
            "type": "Quick Win",
            "horizon": "60 Dias",
            "financial_impact_label": "R$ 159.660,00 (Custo evitável de rastreio)",
            "financial_impact_value": 159660,
            "effort_days": 30,
            "category": "Atendimento",
            "description": (
                "Enviar o link de rastreamento logo após a compra e a cada mudança de rota. "
                "A ação reduz os 30% de chamados abertos apenas para saber onde está o pedido."
            ),
            "metrics_to_watch": ["Volume de chamados de localização", "Custo operacional de suporte", "Satisfação na entrega"],
        },
        {
            "id": "init-06",
            "title": "Ajuste de ponto de pedido para itens ativos",
            "hypothesis": "Hipótese 6 (Estoque e compras)",
            "type": "60 Dias",
            "horizon": "60 Dias",
            "financial_impact_label": f"R$ {exposure['margem_potencialmente_exposta']:,.2f} (Margem protegida)",
            "financial_impact_value": exposure["margem_potencialmente_exposta"],
            "effort_days": 50,
            "category": "Estoque",
            "description": (
                f"Recalcular o ponto de pedido e o prazo de entrega dos {exposure['skus']} SKUs ativos expostos, "
                "evitando falta de mercadoria com base no histórico de vendas."
            ),
            "metrics_to_watch": ["Ruptura de estoque ativo", "Itens abaixo do ponto de pedido", "Margem protegida"],
        },
        {
            "id": "init-07",
            "title": "Atendimento com IA para dúvidas técnicas de produtos",
            "hypothesis": "Hipótese 4 (Atendimento e CX)",
            "type": "90 Dias",
            "horizon": "90 Dias",
            "financial_impact_label": "R$ 78.888,00 (Custo evitável de dúvidas técnicas)",
            "financial_impact_value": 78888,
            "effort_days": 75,
            "category": "Atendimento",
            "description": (
                "Colocar no ar assistente virtual para responder dúvidas técnicas de produtos (14,8% dos chamados), "
                "com transferência rápida para atendentes quando necessário."
            ),
            "metrics_to_watch": ["Resolução sem recontato em 7 dias", "Tempo de resposta", "Satisfação com o suporte"],
        },
        {
            "id": "init-08",
            "title": "Unificação do cadastro de clientes e rastreamento de mídia",
            "hypothesis": "Qualidade dos dados e sequenciamento",
            "type": "90 Dias",
            "horizon": "90 Dias",
            "financial_impact_label": "Confiabilidade para mídia e CRM",
            "financial_impact_value": 500000,
            "effort_days": 90,
            "category": "Dados",
            "description": (
                "Unificar o cadastro de clientes e incluir tags de campanha no checkout, "
                "garantindo dados confiáveis antes de investir em novas ferramentas de marketing."
            ),
            "metrics_to_watch": ["Taxa de conciliação entre bases", "Cobertura de clientes no ERP", "Atribuição de vendas"],
        },
    ]

    business_case = {
        "investimento_total_ano_1": 350000,
        "investimento_total_label": "R$ 350 mil",
        "payback_meses": 2.3,
        "roi_liquido_ano_1": 4.3,
        "beneficio_anual_recorrente": 1855700,
        "beneficio_anual_recorrente_label": "R$ 1,86M/ano",
        "resultado_economico_liquido_ano_1": 1505700,
        "resultado_economico_liquido_ano_1_label": "+R$ 1,51M",
        "receita_liquidacao_central": liquidation["receita_ajustada_devolucoes"],
        "receita_liquidacao_central_label": f"R$ {liquidation['receita_ajustada_devolucoes'] / 1e6:.2f}M",
        "margem_recuperada_descontos": 1800000,
        "margem_recuperada_descontos_label": "+R$ 1,80M/ano",
        "economia_operacional_cx": 55700,
        "economia_operacional_cx_label": "+R$ 55,7 mil/ano",
        "breakdown_investimento": [
            {"item": "Squad de Dados, Negócios e CX (90 dias)", "valor": 250000, "percentual": 71.4},
            {"item": "Infraestrutura Cloud & DuckDB In-Memory (12 meses)", "valor": 60000, "percentual": 17.1},
            {"item": "Mensageria e WhatsApp de Rastreio", "valor": 20000, "percentual": 5.7},
            {"item": "Gestão de Mudança & Treinamento de Equipes", "valor": 20000, "percentual": 5.7}
        ]
    }

    return {
        "meta": package["meta"],
        "initiatives": initiatives,
        "timeline": TIMELINE_PHASES,
        "business_case": business_case,
        "risk_matrix": RISK_MATRIX,
        "sequencing_rationale": SEQUENCING_RATIONALE,
        "summary": {
            "total_initiatives": len(initiatives),
            "quick_wins_count": len([i for i in initiatives if "Quick Win" in i["type"]]),
            "total_potential_value": sum(i["financial_impact_value"] for i in initiatives),
            "inventory_scenario_value": liquidation["receita_ajustada_devolucoes"] + exposure["margem_potencialmente_exposta"],
        }
    }
