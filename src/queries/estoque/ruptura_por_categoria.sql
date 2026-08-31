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
    ROUND((SUM(CASE WHEN em_ruptura = true THEN 1.0 ELSE 0.0 END) / COUNT(sku_id)) * 100.0, 1) AS taxa_ruptura_pct,
    AVG(lead_time_reposicao) AS lead_time_medio
FROM estoque
{where_sql}
GROUP BY categoria
ORDER BY taxa_ruptura_pct DESC;
