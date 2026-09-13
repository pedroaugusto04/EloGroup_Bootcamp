WITH weighted_cost AS (
    SELECT sku_id, SUM(custo_produto) / NULLIF(SUM(quantidade), 0) AS unit_cost
    FROM vendas
    WHERE status_pagamento = 'Aprovado'
      AND sku_id IS NOT NULL AND TRIM(sku_id) <> ''
      AND quantidade IS NOT NULL AND quantidade > 0
      AND custo_produto IS NOT NULL AND custo_produto >= 0
    GROUP BY sku_id
), valued AS (
    SELECT e.*, c.unit_cost
    FROM estoque e LEFT JOIN weighted_cost c USING (sku_id)
)
SELECT
    COUNT(*) AS total_skus,
    COUNT(unit_cost) AS skus_com_custo_vendas,
    COUNT(*) FILTER (WHERE unit_cost IS NULL) AS skus_sem_custo_vendas,
    SUM(estoque_fisico) FILTER (WHERE unit_cost IS NULL) AS unidades_fisicas_sem_cobertura,
    SUM(estoque_reservado) FILTER (WHERE unit_cost IS NULL) AS unidades_reservadas_sem_cobertura,
    SUM(estoque_disponivel) FILTER (WHERE unit_cost IS NULL) AS unidades_disponiveis_sem_cobertura,
    SUM(estoque_fisico * unit_cost) AS capital_fisico,
    SUM(estoque_reservado * unit_cost) AS capital_reservado,
    SUM(estoque_disponivel * unit_cost) AS capital_disponivel,
    COUNT(*) FILTER (WHERE is_descontinuado) AS skus_descontinuados,
    COUNT(unit_cost) FILTER (WHERE is_descontinuado) AS descontinuados_valorados,
    COUNT(*) FILTER (WHERE is_descontinuado AND unit_cost IS NULL) AS descontinuados_excluidos,
    SUM(estoque_fisico * unit_cost) FILTER (WHERE is_descontinuado) AS capital_fisico_descontinuado,
    SUM(estoque_disponivel * unit_cost) FILTER (WHERE is_descontinuado) AS capital_disponivel_descontinuado
FROM valued;
