-- ==============================================================================
-- Query: marketing_stock_mismatch.sql
-- Finalidade: Auditoria de descompasso entre investimento em marketing e nível de ruptura.
-- Métricas: Taxa de ruptura por categoria, pedidos gerados e classificação de risco.
-- ==============================================================================

WITH stock_cat AS (
    SELECT 
        categoria,
        COUNT(sku_id) AS total_skus,
        SUM(CASE WHEN em_ruptura THEN 1 ELSE 0 END) AS skus_em_ruptura,
        ROUND(SUM(CASE WHEN em_ruptura THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(sku_id), 0), 1) AS taxa_ruptura_pct,
        SUM(CASE WHEN is_descontinuado THEN 1 ELSE 0 END) AS skus_descontinuados
    FROM estoque
    GROUP BY categoria
),
mkt_cat AS (
    SELECT 
        v.categoria,
        SUM(m.investimento_reais) AS investimento_estimado,
        COUNT(DISTINCT v.order_id) AS pedidos_gerados,
        SUM(v.receita_liquida) AS receita_gerada
    FROM vendas v
    LEFT JOIN marketing m ON v.canal = m.canal
    WHERE v.status_pagamento = 'Aprovado'
    GROUP BY v.categoria
)
SELECT 
    sc.categoria,
    sc.total_skus,
    sc.skus_em_ruptura,
    sc.taxa_ruptura_pct,
    sc.skus_descontinuados,
    COALESCE(mc.pedidos_gerados, 0) AS pedidos_gerados,
    ROUND(COALESCE(mc.receita_gerada, 0), 2) AS receita_gerada,
    CASE 
        WHEN sc.taxa_ruptura_pct >= 5.0 THEN 'ALERTA_MKT_DESPERDICIO'
        WHEN sc.taxa_ruptura_pct >= 1.0 THEN 'ATENCAO'
        ELSE 'ALINHADO'
    END AS status_alinhamento
FROM stock_cat sc
LEFT JOIN mkt_cat mc ON sc.categoria = mc.categoria
ORDER BY sc.taxa_ruptura_pct DESC;
