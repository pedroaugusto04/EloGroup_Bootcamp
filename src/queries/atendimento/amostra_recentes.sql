-- ==============================================================================
-- Query: Amostra Recente de Chamados com Texto Original de Clientes
-- Finalidade: Permitir a inspeção qualitativa das queixas e relatos dos consumidores.
-- Tabela Origem: atendimento
-- Parâmetros: {where_sql} e {limit}
-- ==============================================================================

SELECT 
    ticket_id,
    canal_entrada,
    categoria_problema,
    status_atendimento,
    nota_csat,
    tempo_primeira_resposta_minutos AS resp_min,
    texto_cliente
FROM atendimento
{where_sql}
ORDER BY data_abertura DESC
LIMIT {limit};
