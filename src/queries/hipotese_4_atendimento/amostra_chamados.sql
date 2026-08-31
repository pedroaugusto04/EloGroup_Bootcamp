-- ==============================================================================
-- Query: Amostra Recente de Chamados com Texto e Classificação (Hipótese 4)
-- Finalidade: Listar tickets recentes com texto do cliente para auditoria e teste de IA.
-- Tabela Origem: atendimento
-- Parâmetros: {where_sql}, {limit}
-- ==============================================================================

SELECT 
    ticket_id,
    data_abertura,
    canal_entrada,
    categoria_problema,
    texto_cliente,
    nota_csat,
    tempo_primeira_resposta_minutos,
    tempo_resolucao_horas,
    status_atendimento,
    is_automatizavel,
    custo_operacional_ticket
FROM atendimento
{where_sql}
ORDER BY data_abertura DESC
LIMIT {limit};
