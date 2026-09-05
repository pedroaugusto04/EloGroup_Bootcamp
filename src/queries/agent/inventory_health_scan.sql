-- ==============================================================================
-- Query: inventory_health_scan.sql
-- Finalidade: Diagnóstico de saúde física e operacional do estoque por SKU.
-- Métricas: Velocidade diária de vendas, dias de cobertura física e risco de ruptura.
-- Parâmetros dinâmicos:
--   - {cat_filter}: Cláusula WHERE opcional para filtro por categoria
--   - {date_filter}: Cláusula AND opcional para filtro temporal em vendas
--   - {days_window}: Janela de dias para velocidade diária (padrão: 365.0)
--   - {limit}: Número máximo de registros detalhados retornados
-- ==============================================================================

WITH sales_agg AS (
    SELECT 
        sku_id,
        SUM(quantidade) AS total_unidades_periodo,
        SUM(receita_liquida) AS receita_real_periodo,
        SUM(margem_calculada) AS margem_real_periodo,
        ROUND(AVG(receita_liquida / NULLIF(quantidade, 0)), 2) AS preco_medio_real,
        ROUND(AVG(margem_calculada / NULLIF(quantidade, 0)), 2) AS margem_unitaria_real
    FROM vendas
    WHERE status_pagamento = 'Aprovado' {date_filter}
    GROUP BY sku_id
),
raw_health AS (
    SELECT 
        e.sku_id,
        e.nome_produto,
        e.categoria,
        e.estoque_disponivel,
        e.ponto_pedido,
        e.lead_time_reposicao AS lead_time_dias,
        e.em_ruptura,
        e.is_descontinuado,
        COALESCE(s.total_unidades_periodo, 0) AS unidades_vendidas_ano,
        ROUND(COALESCE(s.total_unidades_periodo, 0) / {days_window}, 2) AS velocidade_diaria_vendas,
        CASE 
            WHEN COALESCE(s.total_unidades_periodo, 0) = 0 THEN 999.0
            ELSE ROUND(e.estoque_disponivel / (s.total_unidades_periodo / {days_window}), 1)
        END AS dias_cobertura,
        COALESCE(s.preco_medio_real, 0.0) AS preco_medio_real,
        COALESCE(s.margem_unitaria_real, 0.0) AS margem_unitaria_real,
        CASE 
            WHEN e.em_ruptura THEN 'RUPTURA_ATIVA'
            WHEN e.estoque_disponivel <= (e.lead_time_reposicao * COALESCE(s.total_unidades_periodo, 0) / {days_window}) THEN 'RISCO_CRITICO'
            WHEN e.estoque_disponivel < e.ponto_pedido THEN 'ABAIXO_PONTO_PEDIDO'
            WHEN (COALESCE(s.total_unidades_periodo, 0) > 0 AND (e.estoque_disponivel / (s.total_unidades_periodo / {days_window})) > 120.0) THEN 'EXCESSO_ESTOQUE'
            ELSE 'SAUDAVEL'
        END AS diagnostico_operacional
    FROM estoque e
    LEFT JOIN sales_agg s ON e.sku_id = s.sku_id
    {cat_filter}
)
SELECT 
    *,
    COUNT(CASE WHEN em_ruptura THEN 1 END) OVER () AS total_rupturas_global,
    COUNT(CASE WHEN diagnostico_operacional = 'RISCO_CRITICO' THEN 1 END) OVER () AS total_criticos_global,
    COUNT(CASE WHEN diagnostico_operacional IN ('RUPTURA_ATIVA', 'RISCO_CRITICO', 'ABAIXO_PONTO_PEDIDO') THEN 1 END) OVER () AS total_reposicao_global
FROM raw_health
ORDER BY em_ruptura DESC, dias_cobertura ASC
LIMIT {limit};
