-- Saúde operacional. Datas, categoria, limite de cobertura e limite de linhas são vinculados.
WITH period_sales AS (
    SELECT
        sku_id,
        SUM(quantidade) AS approved_units,
        SUM(receita_liquida) AS historical_net_revenue,
        SUM(receita_liquida_efetiva) AS effective_revenue,
        SUM(margem_efetiva) AS effective_margin,
        AVG(receita_liquida / NULLIF(quantidade, 0)) AS average_net_unit_price,
        AVG(margem_efetiva / NULLIF(quantidade, 0)) AS average_effective_unit_margin,
        SUM(custo_frete) AS shipping_cost,
        SUM(CASE WHEN devolvido THEN quantidade ELSE 0 END) AS returned_units
    FROM vendas
    WHERE status_pagamento = 'Aprovado'
      AND CAST(data_pedido AS DATE) BETWEEN ? AND ?
      AND sku_id IS NOT NULL AND TRIM(sku_id) <> ''
      AND quantidade IS NOT NULL AND quantidade > 0
    GROUP BY sku_id
),
category_returns AS (
    SELECT
        categoria,
        SUM(CASE WHEN devolvido THEN quantidade ELSE 0 END) / NULLIF(SUM(quantidade), 0) AS return_rate
    FROM vendas
    WHERE status_pagamento = 'Aprovado'
      AND CAST(data_pedido AS DATE) BETWEEN ? AND ?
      AND quantidade IS NOT NULL AND quantidade > 0
    GROUP BY categoria
),
health AS (
    SELECT
        e.sku_id,
        e.nome_produto,
        e.categoria,
        e.fornecedor_id,
        CAST(e.data_ultima_entrada AS DATE) AS data_ultima_entrada,
        e.estoque_fisico,
        e.estoque_reservado,
        e.estoque_disponivel,
        e.ponto_pedido,
        e.lead_time_reposicao AS lead_time_cadastral_dias,
        e.is_descontinuado,
        s.approved_units AS unidades_aprovadas,
        CASE WHEN s.approved_units IS NOT NULL THEN s.approved_units / CAST(? AS DOUBLE) END AS demanda_diaria_historica,
        CASE WHEN s.approved_units > 0 THEN e.estoque_disponivel / (s.approved_units / CAST(? AS DOUBLE)) END AS cobertura_dias_historica,
        CASE WHEN s.approved_units IS NOT NULL THEN (s.approved_units / CAST(? AS DOUBLE)) * e.lead_time_reposicao END AS necessidade_lead_time,
        CASE WHEN s.approved_units IS NOT NULL THEN
            GREATEST((s.approved_units / CAST(? AS DOUBLE)) * e.lead_time_reposicao - e.estoque_disponivel, 0)
        END AS deficit_potencial_unidades,
        s.average_net_unit_price AS preco_liquido_unitario_historico,
        s.average_effective_unit_margin AS margem_efetiva_unitaria_historica,
        COALESCE(cr.return_rate, 0) AS taxa_devolucao_categoria,
        e.estoque_disponivel = 0 AS ruptura_atual,
        e.estoque_disponivel > 0 AND e.estoque_disponivel <= e.ponto_pedido AS abaixo_ou_no_ponto_pedido,
        NOT e.is_descontinuado AND s.approved_units IS NOT NULL
            AND ((s.approved_units / CAST(? AS DOUBLE)) * e.lead_time_reposicao) > e.estoque_disponivel AS exposicao_lead_time,
        s.approved_units IS NOT NULL AND s.approved_units > 0
            AND e.estoque_disponivel / (s.approved_units / CAST(? AS DOUBLE)) > ? AS alta_cobertura_historica,
        s.approved_units IS NULL AS sem_venda_observada,
        CASE WHEN s.approved_units > 0 THEN
            GREATEST((s.approved_units / CAST(? AS DOUBLE)) * e.lead_time_reposicao - e.estoque_disponivel, 0)
            * s.average_net_unit_price
        END AS receita_antes_devolucao_exposta,
        CASE WHEN s.approved_units > 0 THEN
            GREATEST((s.approved_units / CAST(? AS DOUBLE)) * e.lead_time_reposicao - e.estoque_disponivel, 0)
            * s.average_net_unit_price * (1 - COALESCE(cr.return_rate, 0))
        END AS receita_ajustada_exposta,
        CASE WHEN s.approved_units > 0 THEN
            GREATEST((s.approved_units / CAST(? AS DOUBLE)) * e.lead_time_reposicao - e.estoque_disponivel, 0)
            * s.average_effective_unit_margin
        END AS margem_potencialmente_exposta
    FROM estoque e
    LEFT JOIN period_sales s USING (sku_id)
    LEFT JOIN category_returns cr ON cr.categoria = e.categoria
    WHERE (? IS NULL OR e.categoria = ?)
)
SELECT * FROM health
ORDER BY margem_potencialmente_exposta DESC NULLS LAST, demanda_diaria_historica DESC NULLS LAST, sku_id
LIMIT ?;
