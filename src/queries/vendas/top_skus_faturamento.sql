-- ==============================================================================
-- Query: Top SKUs por Faturamento e Eficiência de Margem
-- Finalidade: Listar os produtos com maior receita líquida e analisar o comportamento
--             de volume vendido, margem total e percentual de desconto médio por SKU.
-- Tabela Origem: vendas
-- Granularidade: SKU (sku_id, produto, categoria)
-- Parâmetros: {where_sql} e {limit}
-- ==============================================================================

SELECT 
    sku_id,
    produto,
    categoria,
    SUM(quantidade) AS unidades_vendidas,
    ROUND(SUM(receita_liquida), 2) AS receita_total,
    ROUND(SUM(margem_calculada), 2) AS margem_total,
    ROUND((SUM(margem_calculada) / NULLIF(SUM(receita_liquida), 0)) * 100.0, 1) AS margem_pct,
    ROUND(AVG(desconto_pct), 1) AS desconto_medio_pct
FROM vendas
{where_sql}
GROUP BY sku_id, produto, categoria
ORDER BY receita_total DESC
LIMIT {limit};
