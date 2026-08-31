-- ==============================================================================
-- Query: Desempenho de Receita e Margem por Canal de Venda
-- Finalidade: Avaliar quais canais de aquisição geram maior volume financeiro
--             e qual a margem percentual entregue por cada canal.
-- Tabela Origem: vendas
-- Granularidade: Canal de Venda
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    canal,
    SUM(receita_liquida) AS receita_liquida,
    SUM(margem_calculada) AS margem_contribuicao,
    (SUM(margem_calculada) / NULLIF(SUM(receita_liquida), 0)) * 100.0 AS margem_pct
FROM vendas
{where_sql}
GROUP BY canal
ORDER BY receita_liquida DESC;
