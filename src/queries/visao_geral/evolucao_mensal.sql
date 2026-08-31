-- ==============================================================================
-- Query: Evolução Mensal de Vendas e Margem de Contribuição
-- Finalidade: Série temporal para identificação de sazonalidade, tendências de
--             crescimento e comportamento da margem ao longo dos meses.
-- Tabela Origem: vendas
-- Granularidade: Mensal (ano_mes: YYYY-MM)
-- Parâmetros: {where_sql} (Filtros dinâmicos aplicados pelo usuário)
-- ==============================================================================

SELECT 
    ano_mes,
    SUM(receita_liquida) AS receita_liquida,
    SUM(margem_calculada) AS margem_contribuicao,
    COUNT(order_id) AS pedidos
FROM vendas
{where_sql}
GROUP BY ano_mes
ORDER BY ano_mes;
