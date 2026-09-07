-- ==============================================================================
-- Query: Distribuição de Avaliações por Nota CSAT (1 a 5)
-- Finalidade: Analisar a curva de satisfação dos clientes e a proporção de notas críticas (1 e 2).
-- Tabela Origem: atendimento
-- Granularidade: Nota CSAT
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    nota_csat,
    COUNT(ticket_id) AS total_avaliacoes
FROM atendimento
{where_sql}
GROUP BY nota_csat
ORDER BY nota_csat ASC;
