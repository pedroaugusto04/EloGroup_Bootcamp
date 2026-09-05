-- ==============================================================================
-- Query: sku_deep_dive.sql
-- Finalidade: Investigação 360° de um SKU específico cruzando estoque e vendas.
-- Métricas: Pedidos totais, receita líquida, margem média, taxa de devolução e posição física.
-- Parâmetros dinâmicos:
--   - {sku_id}: Identificador único do SKU (ex: 'SKU-00185')
-- ==============================================================================

WITH v AS (
    SELECT 
        sku_id,
        COUNT(order_id) AS pedidos_totais,
        SUM(quantidade) AS unidades_vendidas,
        ROUND(SUM(receita_liquida), 2) AS receita_liquida,
        ROUND(SUM(margem_calculada), 2) AS margem_calculada,
        ROUND(AVG(receita_liquida / NULLIF(quantidade, 0)), 2) AS preco_liq_unit_medio,
        ROUND(AVG(custo_produto / NULLIF(quantidade, 0)), 2) AS custo_unit_medio,
        ROUND(AVG(margem_calculada / NULLIF(quantidade, 0)), 2) AS margem_unit_media,
        SUM(CASE WHEN devolvido THEN 1 ELSE 0 END) AS devolucoes,
        ROUND(AVG(CASE WHEN devolvido THEN 1.0 ELSE 0.0 END) * 100.0, 1) AS taxa_devolucao_pct,
        MODE(CASE WHEN devolvido THEN motivo_devolucao ELSE NULL END) AS principal_motivo_devolucao
    FROM vendas
    WHERE sku_id = '{sku_id}' AND status_pagamento = 'Aprovado'
    GROUP BY sku_id
)
SELECT 
    e.sku_id,
    e.nome_produto,
    e.categoria,
    e.subcategoria,
    e.estoque_disponivel,
    e.ponto_pedido,
    e.lead_time_reposicao,
    e.em_ruptura,
    e.is_descontinuado,
    COALESCE(v.pedidos_totais, 0) AS pedidos_totais,
    COALESCE(v.unidades_vendidas, 0) AS unidades_vendidas,
    COALESCE(v.receita_liquida, 0.0) AS receita_liquida,
    COALESCE(v.margem_calculada, 0.0) AS margem_calculada,
    COALESCE(v.preco_liq_unit_medio, 0.0) AS preco_liq_unit_medio,
    COALESCE(v.custo_unit_medio, e.custo_unitario) AS custo_unit_medio,
    COALESCE(v.margem_unit_media, 0.0) AS margem_unit_media,
    COALESCE(v.devolucoes, 0) AS devolucoes,
    COALESCE(v.taxa_devolucao_pct, 0.0) AS taxa_devolucao_pct,
    COALESCE(v.principal_motivo_devolucao, 'N/A') AS principal_motivo_devolucao
FROM estoque e
LEFT JOIN v ON e.sku_id = v.sku_id
WHERE e.sku_id = '{sku_id}';
