-- ==============================================================================
-- Query: discontinued_stranded_capital.sql
-- Finalidade: Mensuração de capital de giro imobilizado em itens descontinuados.
-- Métricas: Custo unitário avaliado, unidades paradas e total de capital travado.
-- Parâmetros dinâmicos:
--   - {limit}: Número máximo de registros retornados
-- ==============================================================================

WITH cost_vendas AS (
    SELECT 
        sku_id, 
        ROUND(AVG(custo_produto / NULLIF(quantidade, 0)), 2) AS custo_medio_real
    FROM vendas
    WHERE status_pagamento = 'Aprovado'
    GROUP BY sku_id
),
raw_stranded AS (
    SELECT 
        e.sku_id,
        e.nome_produto,
        e.categoria,
        e.estoque_disponivel,
        COALESCE(c.custo_medio_real, e.custo_unitario) AS custo_unitario_avaliado,
        ROUND(e.estoque_disponivel * COALESCE(c.custo_medio_real, e.custo_unitario), 2) AS capital_travado_real,
        e.lead_time_reposicao AS lead_time_dias
    FROM estoque e
    LEFT JOIN cost_vendas c ON e.sku_id = c.sku_id
    WHERE e.is_descontinuado = true AND e.estoque_disponivel > 0
)
SELECT 
    *,
    ROUND(SUM(capital_travado_real) OVER (), 2) AS total_stranded_cash_global,
    COUNT(*) OVER () AS total_skus_descontinuados_global
FROM raw_stranded
ORDER BY capital_travado_real DESC
LIMIT {limit};
