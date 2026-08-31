-- ==============================================================================
-- Query: Volume de Atendimentos por Canal de Entrada
-- Finalidade: Identificar onde os clientes buscam suporte (ChatBot, WhatsApp, E-mail, Reclame Aqui).
-- Tabela Origem: atendimento
-- Granularidade: Canal de Entrada
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    canal_entrada,
    COUNT(ticket_id) AS total_tickets
FROM atendimento
{where_sql}
GROUP BY canal_entrada
ORDER BY total_tickets DESC;
