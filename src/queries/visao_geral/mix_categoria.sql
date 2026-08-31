-- ==============================================================================
-- Query: Mix de Faturamento por Categoria de Produto
-- Finalidade: Medir a representatividade de cada categoria na receita líquida total.
-- Tabela Origem: vendas
-- Granularidade: Categoria
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    categoria,
    SUM(receita_liquida) AS receita_liquida
FROM vendas
{where_sql}
GROUP BY categoria
ORDER BY receita_liquida DESC;
