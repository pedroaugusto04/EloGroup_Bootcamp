-- ==============================================================================
-- Query: KPIs Consolidados de Vendas e Margem
-- Finalidade: Calcula os principais indicadores executivos de faturamento,
--             lucratividade direta, volume de pedidos, ticket médio e devoluções.
-- Tabela Origem: vendas (Parquet/DuckDB)
-- Métricas Calculadas:
--   - receita_bruta: Total faturado antes de descontos
--   - receita_liquida: Receita efetiva faturada (Base de cálculo de margem)
--   - margem: Margem de Contribuição Líquida (Receita Líquida - Custo Produto - Custo Frete)
--   - ticket_medio: Média de receita líquida por pedido
--   - taxa_devolucao: % de pedidos devolvidos sobre o total de pedidos aprovados
-- Parâmetros: {where_sql} (Filtros de status de pagamento, categoria e ano)
-- ==============================================================================

SELECT 
    COALESCE(SUM(receita_bruta), 0) AS bruta,
    COALESCE(SUM(receita_liquida), 0) AS liquida,
    COALESCE(SUM(margem_calculada), 0) AS margem,
    COALESCE(COUNT(order_id), 0) AS total_pedidos,
    COALESCE(AVG(receita_liquida), 0) AS ticket_medio,
    COALESCE(AVG(CASE WHEN devolvido = true THEN 1.0 ELSE 0.0 END) * 100.0, 0) AS taxa_devolucao
FROM vendas
{where_sql};
