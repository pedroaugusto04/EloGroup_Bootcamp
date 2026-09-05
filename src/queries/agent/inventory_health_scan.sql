-- ==============================================================================
-- Query: inventory_health_scan.sql
-- Finalidade: Diagnóstico de saúde física e operacional do estoque por SKU.
-- Métricas: Velocidade diária de vendas, dias de cobertura física e risco de ruptura.
-- Parâmetros dinâmicos:
--   - {cat_filter}: Cláusula WHERE opcional para filtro por categoria
--   - {limit}: Número máximo de registros retornados
-- ==============================================================================

WITH sales_agg AS (
    SELECT 
        sku_id,
        SUM(quantidade) AS total_unidades_ano,
        SUM(receita_liquida) AS receita_real_ano,
        SUM(margem_calculada) AS margem_real_ano,
        ROUND(AVG(receita_liquida / NULLIF(quantidade, 0)), 2) AS preco_medio_real,
        ROUND(AVG(margem_calculada / NULLIF(quantidade, 0)), 2) AS margem_unitaria_real
    FROM vendas
    WHERE status_pagamento = 'Aprovado'
    GROUP BY sku_id
)
SELECT 
    e.sku_id,
    e.nome_produto,
    e.categoria,
    e.estoque_disponivel,
    e.ponto_pedido,
    e.lead_time_reposicao AS lead_time_dias,
    e.em_ruptura,
    e.is_descontinuado,
    COALESCE(s.total_unidades_ano, 0) AS unidades_vendidas_ano,
    ROUND(COALESCE(s.total_unidades_ano, 0) / 365.0, 2) AS velocidade_diaria_vendas,
    CASE 
        WHEN COALESCE(s.total_unidades_ano, 0) = 0 THEN 999.0
        ELSE ROUND(e.estoque_disponivel / (s.total_unidades_ano / 365.0), 1)
    END AS dias_cobertura,
    COALESCE(s.preco_medio_real, 0.0) AS preco_medio_real,
    COALESCE(s.margem_unitaria_real, 0.0) AS margem_unitaria_real,
    CASE 
        WHEN e.em_ruptura THEN 'RUPTURA_ATIVA'
        WHEN e.estoque_disponivel <= (e.lead_time_reposicao * COALESCE(s.total_unidades_ano, 0) / 365.0) THEN 'RISCO_CRITICO'
        WHEN e.estoque_disponivel < e.ponto_pedido THEN 'ABAIXO_PONTO_PEDIDO'
        WHEN (COALESCE(s.total_unidades_ano, 0) > 0 AND (e.estoque_disponivel / (s.total_unidades_ano / 365.0)) > 120.0) THEN 'EXCESSO_ESTOQUE'
        ELSE 'SAUDAVEL'
    END AS diagnostico_operacional
FROM estoque e
LEFT JOIN sales_agg s ON e.sku_id = s.sku_id
{cat_filter}
ORDER BY e.em_ruptura DESC, dias_cobertura ASC
LIMIT {limit};
