-- ==============================================================================
-- Query: returns_and_quality_risk.sql
-- Finalidade: Análise de devoluções e atrito logístico/qualidade por SKU.
-- Métricas: Taxa de devolução, frete médio perdido e principal motivo apontado.
-- Parâmetros dinâmicos:
--   - {min_orders}: Volume mínimo de pedidos para relevância estatística
--   - {min_returns}: Volume mínimo de devoluções registradas
--   - {date_filter}: Cláusula AND opcional para filtro temporal em vendas
-- ==============================================================================

SELECT 
    v.sku_id,
    v.produto,
    v.categoria,
    COUNT(v.order_id) AS total_pedidos,
    SUM(CASE WHEN v.devolvido THEN 1 ELSE 0 END) AS total_devolucoes,
    ROUND(SUM(CASE WHEN v.devolvido THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(v.order_id), 0), 1) AS taxa_devolucao_pct,
    MODE(CASE WHEN v.devolvido THEN v.motivo_devolucao ELSE NULL END) AS principal_motivo_devolucao,
    ROUND(AVG(v.custo_frete), 2) AS custo_frete_medio_perdido,
    MAX(e.estoque_disponivel) AS estoque_disponivel
FROM vendas v
LEFT JOIN estoque e ON v.sku_id = e.sku_id
WHERE v.status_pagamento = 'Aprovado' {date_filter}
GROUP BY v.sku_id, v.produto, v.categoria
HAVING COUNT(v.order_id) >= {min_orders} AND SUM(CASE WHEN v.devolvido THEN 1 ELSE 0 END) >= {min_returns}
ORDER BY taxa_devolucao_pct DESC, total_devolucoes DESC
LIMIT 20;
