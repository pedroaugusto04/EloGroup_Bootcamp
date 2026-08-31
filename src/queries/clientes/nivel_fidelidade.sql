-- ==============================================================================
-- Query: Volume de Clientes por Nível de Fidelidade (Loyalty Tiers)
-- Finalidade: Analisar a participação de clientes nos níveis de fidelidade (Bronze, Silver, Gold, Platinum).
-- Tabela Origem: clientes
-- Granularidade: Nível de Fidelidade
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    nivel_fidelidade,
    COUNT(customer_id) AS total_clientes
FROM clientes
{where_sql}
GROUP BY nivel_fidelidade
ORDER BY total_clientes DESC;
