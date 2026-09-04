-- ==============================================================================
-- Query: Taxa de Ruptura de Estoque e Lead Time por Categoria
-- Finalidade: Identificar quais categorias sofrem mais com indisponibilidade de produtos
--             e qual a dependência de fornecedores com prazos de entrega mais longos.
-- Tabela Origem: estoque
-- Granularidade: Categoria
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    categoria,
    COUNT(sku_id) AS total_skus,
    SUM(CASE WHEN em_ruptura = true THEN 1 ELSE 0 END) AS skus_ruptura,
    SUM(CASE WHEN is_estoque_critico = true THEN 1 ELSE 0 END) AS skus_estoque_critico,
    SUM(CASE WHEN precisa_reposicao = true THEN 1 ELSE 0 END) AS skus_precisa_reposicao,
    ROUND((SUM(CASE WHEN em_ruptura = true THEN 1.0 ELSE 0.0 END) / COUNT(sku_id)) * 100.0, 1) AS taxa_ruptura_pct,
    ROUND((SUM(CASE WHEN is_estoque_critico = true THEN 1.0 ELSE 0.0 END) / COUNT(sku_id)) * 100.0, 1) AS taxa_critico_pct,
    ROUND((SUM(CASE WHEN precisa_reposicao = true THEN 1.0 ELSE 0.0 END) / COUNT(sku_id)) * 100.0, 1) AS taxa_reposicao_total_pct,
    AVG(lead_time_reposicao) AS lead_time_medio
FROM estoque
{where_sql}
GROUP BY categoria
ORDER BY taxa_reposicao_total_pct DESC;
