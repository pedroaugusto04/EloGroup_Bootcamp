-- ==============================================================================
-- Query: Cruzamento Estoque (Posição & Ruptura) vs Vendas (Giro & Demanda Real)
-- Eixo 2: Análise Relacional Integrada
-- Tabelas: estoque, vendas
-- ==============================================================================

WITH est AS (
    SELECT 
        categoria,
        COUNT(sku_id) AS total_skus,
        SUM(valor_total_estoque) AS capital_imobilizado_estoque,
        SUM(CASE WHEN em_ruptura THEN 1 ELSE 0 END) AS skus_em_ruptura,
        SUM(CASE WHEN is_descontinuado THEN 1 ELSE 0 END) AS skus_descontinuados,
        SUM(capital_travado_descontinuado) AS capital_travado_descontinuado,
        ROUND(AVG(lead_time_reposicao), 1) AS lead_time_medio_dias
    FROM estoque
    GROUP BY categoria
),
ven AS (
    SELECT 
        categoria,
        COUNT(order_id) AS total_pedidos,
        SUM(quantidade) AS unidades_vendidas,
        SUM(receita_liquida) AS receita_real,
        SUM(margem_calculada) AS margem_real
    FROM vendas
    WHERE status_pagamento = 'Aprovado'
    GROUP BY categoria
)
SELECT 
    e.categoria,
    e.total_skus,
    e.capital_imobilizado_estoque,
    e.skus_em_ruptura,
    ROUND(e.skus_em_ruptura * 100.0 / NULLIF(e.total_skus, 0), 1) AS taxa_ruptura_pct,
    e.skus_descontinuados,
    e.capital_travado_descontinuado,
    e.lead_time_medio_dias,
    COALESCE(v.unidades_vendidas, 0.0) AS unidades_vendidas,
    COALESCE(v.receita_real, 0.0) AS receita_real,
    COALESCE(v.margem_real, 0.0) AS margem_real,
    ROUND(COALESCE(v.receita_real, 0.0) / NULLIF(e.capital_imobilizado_estoque, 0), 2) AS giro_estoque_ratio
FROM est e
LEFT JOIN ven v ON e.categoria = v.categoria
ORDER BY v.receita_real DESC;
