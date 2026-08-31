-- ==============================================================================
-- Query: Volume de Chamados e CSAT por Categoria de Problema
-- Finalidade: Mapear os principais motivos de contato dos clientes (ex: atraso de entrega,
--             troca de tamanho, defeito, pagamento) e a nota de satisfação associada.
-- Tabela Origem: atendimento
-- Granularidade: Categoria de Problema
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    categoria_problema,
    COUNT(ticket_id) AS total_tickets,
    AVG(nota_csat) AS csat_medio
FROM atendimento
{where_sql}
GROUP BY categoria_problema
ORDER BY total_tickets DESC;
