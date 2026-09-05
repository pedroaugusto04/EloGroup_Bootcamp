-- ==============================================================================
-- Query: sales_demand_matrix.sql
-- Finalidade: Matriz de faturamento, margem e giro por produto da base transacional.
-- Métricas: Receita líquida total, margem calculada e estoque disponível associado.
-- Parâmetros dinâmicos:
--   - {cat_filter}: Cláusula AND opcional para filtro por categoria
--   - {date_filter}: Cláusula AND opcional para filtro por data em vendas
--   - {top_n}: Limite de produtos retornados ordenados por receita líquida
-- ==============================================================================

SELECT 
    v.sku_id,
    v.produto,
    v.categoria,
    COUNT(v.order_id) AS total_pedidos,
    SUM(v.quantidade) AS unidades_vendidas,
    ROUND(SUM(v.receita_liquida), 2) AS receita_liquida_total,
    ROUND(SUM(v.margem_calculada), 2) AS margem_total,
    ROUND(AVG(v.receita_liquida / NULLIF(v.quantidade, 0)), 2) AS preco_liquido_unit_medio,
    ROUND(AVG(v.margem_calculada / NULLIF(v.quantidade, 0)), 2) AS margem_unit_media,
    MAX(e.estoque_disponivel) AS estoque_atual,
    MAX(e.em_ruptura) AS em_ruptura,
    MAX(e.is_descontinuado) AS is_descontinuado,
    MAX(e.lead_time_reposicao) AS lead_time_dias
FROM vendas v
LEFT JOIN estoque e ON v.sku_id = e.sku_id
WHERE v.status_pagamento = 'Aprovado' {date_filter} {cat_filter}
GROUP BY v.sku_id, v.produto, v.categoria
ORDER BY receita_liquida_total DESC
LIMIT {top_n};
