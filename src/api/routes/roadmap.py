"""
src/api/routes/roadmap.py
Rotas do Plano Estratégico, Matriz de Priorização Executiva,
Business Case Consolidado, Governança de Riscos e Racional de Sequenciamento.
"""

from fastapi import APIRouter

from src.agent.inventory_analytics import build_audit_package
from src.infrastructure.database import DuckDBRepository

router = APIRouter(prefix="/roadmap", tags=["roadmap"])

# Matriz alinhada ao plano estratégico, auditoria e modelagem financeira.

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
                "scope": "Teste piloto do Margin Recovery Advisor limitando descontos ao teto dinâmico por SKU para proteger a margem sem perder volume.",
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
                "scope": "Aplicação contínua da governança de tetos dinâmicos de desconto em 100% dos produtos do catálogo.",
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
    "title": "Integração e Conciliação das Bases de Dados",
    "subtitle": "Ajustes simples para conectar as bases e destravar decisões futuras com dados confiáveis.",
    "items": [
        {
            "title": "Vendas e Marketing",
            "highlight_number": "38,2M vs 26,5k",
            "highlight_label": "conversões de pixel vs pedidos no ERP",
            "divergence": "As plataformas de anúncio medem conversões próprias, sem vínculo direto com os pedidos faturados no ERP.",
            "next_step": "Estabelecer vínculo entre os anúncios e as compras para medir o retorno real de cada canal antes de remanejar verbas."
        },
        {
            "title": "Vendas e Clientes",
            "highlight_number": "40,6% e 346",
            "highlight_label": "vendas anônimas e clientes localizados",
            "divergence": "Apenas 346 dos 15 mil clientes cadastrados constam nas vendas, e 40,6% dos pedidos estão em um usuário genérico.",
            "next_step": "Identificar o cliente na compra para juntar o histórico em um só cadastro antes de planejar ações de fidelização."
        },
        {
            "title": "Vendas e Atendimento",
            "highlight_number": "65,4%",
            "highlight_label": "chamados sem pedido localizado no ERP",
            "divergence": "A maioria dos chamados de suporte cita pedidos que não aparecem no extrato de vendas.",
            "next_step": "Conectar o atendimento às vendas para o operador localizar o histórico de compra do cliente de imediato."
        },
        {
            "title": "Vendas e Estoque",
            "highlight_number": "206 SKUs",
            "highlight_label": "conciliados para liquidação imediata",
            "divergence": "O custo cadastrado no estoque difere do praticado nas vendas, e o inventário reflete apenas uma foto estática.",
            "next_step": "Conectar o sistema de estoque às vendas para atualizar custos e saldos automaticamente após a liquidação."
        }
    ],
    "marketing": {
        "title": "Vendas e Marketing",
        "highlight_number": "38,2M vs 26,5k",
        "highlight_label": "conversões de pixel vs pedidos no ERP",
        "divergence": "As plataformas de anúncio medem conversões próprias, sem vínculo direto com os pedidos faturados no ERP.",
        "next_step": "Estabelecer vínculo entre os anúncios e as compras para medir o retorno real de cada canal antes de remanejar verbas."
    },
    "crm": {
        "title": "Vendas e Clientes",
        "highlight_number": "40,6% e 346",
        "highlight_label": "vendas anônimas e clientes localizados",
        "divergence": "Apenas 346 dos 15 mil clientes cadastrados constam nas vendas, e 40,6% dos pedidos estão em um usuário genérico.",
        "next_step": "Identificar o cliente na compra para juntar o histórico em um só cadastro antes de planejar ações de fidelização."
    },
    "c_level_takeaway": "A priorização foca primeiro em caixa e margem (Estoque e Preço). Ao mesmo tempo, esses alinhamentos organizam as informações para destravar ações de clientes, anúncios e suporte no ciclo seguinte."
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
            "title": "Liquidação de Descontinuados (Predictive Inventory Advisor)",
            "hypothesis": "Hipótese 1 e 6 (Estoque parado)",
            "type": "Quick Win",
            "horizon": "30 Dias",
            "financial_impact_label": f"R$ {liquidation['receita_ajustada_devolucoes']:,.2f} (Receita líquida no cenário central)",
            "financial_impact_value": liquidation["receita_ajustada_devolucoes"],
            "effort_days": 20,
            "category": "Estoque",
            "description": (
                f"Liquidar os {capital['descontinuados_valorados']} SKUs descontinuados (R$ 6,1M imobilizados) com meta de 50% de sell-through "
                f"e desconto médio de 30%, gerando caixa imediato com R$ 969k de margem e bloqueando recompras no ERP."
            ),
            "metrics_to_watch": ["Sell-through do lote", "Receita líquida realizada", "Zero recompra no ERP"],
        },
        {
            "id": "init-02",
            "title": "Proteção contra Ruptura nos Ativos (Predictive Inventory Advisor)",
            "hypothesis": "Hipótese 6 (Estoque e compras)",
            "type": "60 Dias",
            "horizon": "60 Dias",
            "financial_impact_label": f"R$ {exposure['margem_potencialmente_exposta']:,.2f} (Margem protegida)",
            "financial_impact_value": exposure["margem_potencialmente_exposta"],
            "effort_days": 50,
            "category": "Estoque",
            "description": (
                f"Recalcular ponto de pedido e lead time para os {exposure['skus']} SKUs ativos expostos durante o prazo dos fornecedores, "
                "garantindo reposição contínua e prevenindo quebras de estoque."
            ),
            "metrics_to_watch": ["Rupturas evitadas", "Aderência ao ponto de pedido", "Lead time de reposição"],
        },
        {
            "id": "init-03",
            "title": "Governança Dinâmica de Descontos (Margin Recovery Advisor)",
            "hypothesis": "Hipótese 2 (Margem e descontos)",
            "type": "Quick Win",
            "horizon": "60 Dias",
            "financial_impact_label": "R$ 1.800.000,00/ano (Margem recuperada)",
            "financial_impact_value": 1800000,
            "effort_days": 45,
            "category": "Preço e Margem",
            "description": (
                "Implementar piloto do copiloto de precificação aplicando tetos dinâmicos por SKU (cruzando CMV, frete e devoluções), "
                "podando descontos excessivos inelásticos (>20%) sem perda de volume."
            ),
            "metrics_to_watch": ["Margem bruta preservada", "Volume diário de vendas", "Aderência aos tetos por SKU"],
        },
        {
            "id": "init-04",
            "title": "Notificações Proativas de Rastreio (WhatsApp & E-mail)",
            "hypothesis": "Hipótese 4 (Atendimento e CX)",
            "type": "Quick Win",
            "horizon": "60 Dias",
            "financial_impact_label": "R$ 37.254,00/ano (Base histórica: R$ 159,7k)",
            "financial_impact_value": 37254,
            "effort_days": 30,
            "category": "Atendimento",
            "description": (
                "Envio automático de link de rastreamento e eventos de entrega logo após o despacho, "
                "capturando 80% das consultas de localização de pedidos (30% do volume de chamados)."
            ),
            "metrics_to_watch": ["Queda nos chamados de rastreio", "Taxa de entrega no WhatsApp", "CSAT de entrega"],
        },
        {
            "id": "init-05",
            "title": "Autoatendimento N1 para Dúvidas Técnicas (Agente 3 • IA)",
            "hypothesis": "Hipótese 4 (Atendimento e CX)",
            "type": "90 Dias",
            "horizon": "90 Dias",
            "financial_impact_label": "R$ 18.470,00/ano (Base histórica: R$ 78,9k)",
            "financial_impact_value": 18470,
            "effort_days": 75,
            "category": "Atendimento",
            "description": (
                "Assistente virtual supervisionado para resolução de dúvidas técnicas de produtos (14,8% dos chamados; R$ 78,9 mil na base), "
                "com captura estimada de 50% dos chamados e transbordo qualificado para equipe humana."
            ),
            "metrics_to_watch": ["Resolução sem recontato em 7 dias", "Taxa de transbordo humano", "CSAT do autoatendimento"],
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
            {"item": "Infraestrutura Cloud (12 meses)", "valor": 60000, "percentual": 17.1},
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
