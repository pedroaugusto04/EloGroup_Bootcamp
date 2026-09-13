"""
src/agent/constants.py
Constantes, mensagens padronizadas e templates do Agente de Estoque.
Centraliza todos os textos para evitar strings hardcoded na lógica do grafo.
"""

from typing import List, Dict, Any


# ============================================================================
# PLANO PADRÃO DE ETAPAS (FALLBACK DO PLANNER)
# ============================================================================

DEFAULT_PLAN_STEPS: List[Dict[str, Any]] = [
    {
        "step_id": 1,
        "name": "Diagnóstico de Ruptura & Cobertura Física",
        "description": "Scan completo de SKUs em ruptura, abaixo do ponto de pedido e cálculo de dias de cobertura.",
        "status": "pending",
        "result": None,
    },
    {
        "step_id": 2,
        "name": "Cruzamento com Demanda e Capital Travado",
        "description": "Cruzar demanda histórica, receita e margem efetivas e valorar capital com custo de Vendas.",
        "status": "pending",
        "result": None,
    },
    {
        "step_id": 3,
        "name": "Auditoria de Qualidade e Devoluções",
        "description": "Mapear motivos declarados de devolução sem inferir causalidade.",
        "status": "pending",
        "result": None,
    },
    {
        "step_id": 4,
        "name": "Síntese e Recomendações Executivas",
        "description": "Consolidar matriz de Quick Wins (30d), Médio Prazo (60d) e Longo Prazo (90d).",
        "status": "pending",
        "result": None,
    }
]


# ============================================================================
# MENSAGENS DO SISTEMA E AVISOS DE DISPONIBILIDADE
# ============================================================================

LLM_UNAVAILABLE_MESSAGE = "Complemento do LLM indisponível; fatos determinísticos preservados."

CRITIC_UNAVAILABLE_FEEDBACK = (
    "[Indisponível] Auditoria de reflexão não executada devido à indisponibilidade do serviço."
)

CRITIC_APPROVAL_SUCCESS_FEEDBACK = (
    "Relatório aprovado integralmente nos 4 guardrails operacionais e financeiros."
)

# ============================================================================
# MENSAGENS DE VIOLAÇÃO DE GUARDRAILS
# ============================================================================

VIOLATION_DISCONTINUED_MSG = "Violação Guardrail 1: Recomendada compra/reposição indevida de SKU descontinuado."
VIOLATION_TEMPORAL_MSG = "Violação Guardrail 4: Faltou estruturação clara de Quick Wins (30 dias) e iniciativas estruturais (60/90 dias)."


# ============================================================================
# MISSÃO PADRÃO DO WORKER AUTÔNOMO
# ============================================================================

DEFAULT_INVENTORY_AUDIT_MISSION = (
    "Executar sob demanda a auditoria de estoque da Vértice Retail: "
    "diagnosticar rupturas ativas e iminentes (cobertura vs. lead time), mapear capital "
    "imobilizado em descontinuados a custo real, filtrar riscos de devolução e consolidar "
    "as recomendações de compras e gestão em 30, 60 e 90 dias."
)


# ============================================================================
# MISSÕES PRÉ-CONFIGURADAS (PRESETS DA UI)
# ============================================================================

PRESET_MISSIONS = {
    "1. Auditoria Geral de Estoque": DEFAULT_INVENTORY_AUDIT_MISSION,
    "2. Foco em Capital de Giro: Desova de Descontinuados": (
        "Investigar todos os produtos descontinuados com estoque físico ativo, calcular o capital imobilizado a custo real "
        "e propor estratégia de liquidação imediata para liberação de caixa."
    ),
    "3. Foco em Curva A: Prevenção de Rupturas e Lead Time": (
        "Identificar os top produtos em faturamento que estão com cobertura abaixo do lead time de fornecedores "
        "e priorizar investigação de reposição, sem emitir ordens ou quantidades."
    )
}
