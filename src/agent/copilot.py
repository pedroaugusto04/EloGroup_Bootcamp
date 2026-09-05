"""
src/agent/copilot.py
Copiloto Interativo de Estoque & Estratégia Comercial (Vértice Retail).
Implementado com a estratégia ReAct (Reasoning + Acting) e Memória Conversacional Persistente (LangGraph MemorySaver).
Permite aos tomadores de decisão (C-Level e Gerentes de Categoria) realizar
perguntas ad-hoc, investigações de SKU e simulações financeiras em tempo real com raciocínio multi-hop.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from src.infrastructure.llm import get_llm
from src.agent.tools import (
    tool_inventory_health_scan,
    tool_sales_demand_matrix,
    tool_returns_and_quality_risk,
    tool_discontinued_stranded_capital,
    tool_sku_deep_dive,
    tool_simulate_inventory_liquidation,
)

logger = logging.getLogger("vertice.inventory_copilot")

COPILOT_SYSTEM_PROMPT = """Você é o **Copiloto Estratégico de Estoque & Rentabilidade da Vértice Retail** (Bootcamp EloGroup 2026).
Seu papel é atuar como um consultor analítico sênior no diagnóstico de estoque, rentabilidade e estratégia comercial para o C-Level e Gerentes de Categoria.

Ano Base de Referência: 2026.

Diretrizes de Raciocínio (ReAct):
1. **Rigor e Factualidade**: Sempre que o usuário fizer uma pergunta sobre estoque, vendas, produtos, SKUs, categorias, fornecedores ou devoluções, utilize suas ferramentas determinísticas do DuckDB para buscar os dados reais. NUNCA invente números, SKUs ou estatísticas.
2. **Impacto em R$ e Visão Executiva**: Sempre quantifique o impacto financeiro (R$), o capital de giro imobilizado (baseado no custo contábil oficial de estoque, R$ 14,77M em descontinuados), a margem de contribuição e o risco operacional.
3. **Guardrail de Descontinuados**: NUNCA sugira comprar ou repor itens marcados como 'descontinuados'. Para estes itens, recomende queima controlada/liquidação ou renegociação.
4. **Itens sem Giro / Obsolescência**: Produtos com estoque disponível positivo mas com zero vendas registradas no período anualizado são diagnosticados como 'SEM_GIRO_OBSOLETO'. Recomende auditoria de catálogo e desova antes de novas compras.
5. **Memória de Contexto**: Mantenha a continuidade da conversa. Se o usuário fizer uma pergunta de follow-up (ex: 'E qual o lead time do primeiro produto citado?'), utilize o contexto das mensagens e ferramentas anteriores para responder com precisão.
6. **Formatação Limpa**: Estruture suas respostas em Markdown profissional, com bullet points, tabelas comparativas e destaques em negrito.
7. **Sem Diagramas Mermaid**: NUNCA utilize blocos de código mermaid (```mermaid). Use exclusivamente tabelas Markdown estruturadas e listas analíticas para sintetizar fluxos e etapas.
"""

OFFLINE_FALLBACK_NOTICE = (
    "**[Serviço Temporariamente Indisponível]**\n\n"
    "Tente novamente mais tarde. "
)


class InventoryCopilot:
    """Copiloto Conversacional ReAct com Memória de Sessão (LangGraph MemorySaver)."""

    def __init__(self, memory: Optional[MemorySaver] = None):
        self.tools = [
            tool_inventory_health_scan,
            tool_sales_demand_matrix,
            tool_returns_and_quality_risk,
            tool_discontinued_stranded_capital,
            tool_sku_deep_dive,
            tool_simulate_inventory_liquidation,
        ]
        self.memory = memory or MemorySaver()
        self._build_agent()

    def _build_agent(self):
        """Constrói o agente ReAct compilado com o checkpointer em memória."""
        llm = get_llm()
        if llm:
            try:
                self.agent = create_react_agent(
                    model=llm,
                    tools=self.tools,
                    checkpointer=self.memory,
                    prompt=COPILOT_SYSTEM_PROMPT,
                )
                logger.info("Agente ReAct compilado com sucesso com %d ferramentas.", len(self.tools))
            except Exception as e:
                logger.warning("Falha ao compilar create_react_agent: %s", e)
                self.agent = None
        else:
            self.agent = None

    def ask(
        self,
        query: str,
        thread_id: str = "vertice_default_session",
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Executa o ciclo ReAct (Thought -> Action -> Observation -> Final Answer)
        mantendo a esteira de memória associada ao thread_id e janela deslizante de histórico recente.
        """
        logger.info("Copilot ReAct recebeu query para thread '%s': %s", thread_id, query[:80])

        if self.agent is None:
            self._build_agent()

        if self.agent is None:
            return OFFLINE_FALLBACK_NOTICE

        try:
            recursion_limit = int(os.environ.get("COPILOT_RECURSION_LIMIT", "15"))
            history_window = int(os.environ.get("COPILOT_HISTORY_WINDOW", "6"))
            config = {
                "configurable": {"thread_id": thread_id},
                "recursion_limit": recursion_limit,
            }

            input_messages = []
            if history:
                # Recorta as últimas N mensagens
                recent_history = history[-history_window:]
                for msg in recent_history:
                    role = msg.get("role")
                    content = msg.get("content", "")
                    if role == "user" and content:
                        input_messages.append(HumanMessage(content=content))
                    elif role == "assistant" and content:
                        input_messages.append(AIMessage(content=content))

            input_messages.append(HumanMessage(content=query))

            result = self.agent.invoke(
                {"messages": input_messages},
                config=config,
            )

            messages = result.get("messages", [])
            if messages:
                last_msg = messages[-1]
                content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
                return content
            return OFFLINE_FALLBACK_NOTICE
        except Exception as e:
            logger.warning("Erro durante execução do ciclo ReAct: %s", e)
            return f"Erro ao processar a consulta via ReAct: {str(e)}"

    def seed_conversation(self, thread_id: str, initial_assistant_message: str):
        """Inicializa a memória do agente ReAct com uma mensagem de contexto prévia (ex: e-mail de auditoria)."""
        if self.agent is None:
            self._build_agent()
        if self.agent:
            try:
                config = {"configurable": {"thread_id": thread_id}}
                self.agent.update_state(config, {"messages": [AIMessage(content=initial_assistant_message)]})
                logger.info("Memória ReAct da thread '%s' inicializada com contexto de e-mail/auditoria.", thread_id)
            except Exception as e:
                logger.warning("Falha ao semear memória do agente: %s", e)

