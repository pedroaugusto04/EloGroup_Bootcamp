-- ==============================================================================
-- Query: Análise de Margem de Contribuição e Descontos por Categoria
-- Finalidade: Avaliar quais categorias de produtos são mais rentáveis e quais
--             possuem maior agressividade de descontos concedidos.
-- Tabela Origem: vendas
-- Granularidade: Categoria
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    categoria,
    SUM(receita_liquida) AS receita,
    SUM(margem_calculada) AS margem,
    (SUM(margem_calculada) / NULLIF(SUM(receita_liquida), 0)) * 100.0 AS margem_pct,
    AVG(desconto_pct) AS desconto_medio_pct
FROM vendas
{where_sql}
GROUP BY categoria
ORDER BY receita DESC;
