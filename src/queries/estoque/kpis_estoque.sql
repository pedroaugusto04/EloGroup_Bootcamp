-- ==============================================================================
-- Query: KPIs Gerais de Gestão de Estoque e Capital Imobilizado
-- Finalidade: Medir o total de SKUs cadastrados, volume de itens em ruptura (estoque <= ponto_pedido),
--             taxa percentual de ruptura, valor financeiro total do estoque e lead time médio de reposição.
-- Tabela Origem: estoque
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    COUNT(sku_id) AS total_skus,
    SUM(CASE WHEN em_ruptura = true THEN 1 ELSE 0 END) AS skus_ruptura,
    ROUND((SUM(CASE WHEN em_ruptura = true THEN 1.0 ELSE 0.0 END) / NULLIF(COUNT(sku_id), 0)) * 100.0, 1) AS taxa_ruptura,
    SUM(valor_total_estoque) AS capital_parado,
    AVG(lead_time_reposicao) AS lead_time_medio
FROM estoque
{where_sql};
