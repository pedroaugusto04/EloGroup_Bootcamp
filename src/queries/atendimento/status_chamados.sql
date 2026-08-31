-- ==============================================================================
-- Query: Status dos Atendimentos
-- Finalidade: Acompanhar o percentual de chamados Resolvidos, Em Análise, Abertos ou Escalados.
-- Tabela Origem: atendimento
-- Granularidade: Status de Atendimento
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    status_atendimento,
    COUNT(ticket_id) AS total_tickets
FROM atendimento
{where_sql}
GROUP BY status_atendimento
ORDER BY total_tickets DESC;
