-- ==============================================================================
-- Query: Distribuição Geográfica dos Clientes por Estado (UF)
-- Finalidade: Identificar as unidades federativas com maior concentração de clientes
--             e maior valor de LTV acumulado.
-- Tabela Origem: clientes
-- Granularidade: Estado (UF)
-- Parâmetros: {uf_where} e {limit}
-- ==============================================================================

SELECT 
    estado,
    COUNT(customer_id) AS total_clientes,
    SUM(ltv_acumulado) AS ltv_total
FROM clientes
{uf_where}
GROUP BY estado
ORDER BY total_clientes DESC
LIMIT {limit};
