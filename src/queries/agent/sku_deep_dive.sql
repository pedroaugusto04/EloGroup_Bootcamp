-- Detalha um SKU, separando a posição de Estoque das métricas históricas de Vendas.
WITH period_sales AS (
    SELECT sku_id, COUNT(*) AS pedidos_aprovados, SUM(quantidade) AS unidades_aprovadas,
           SUM(receita_liquida_efetiva) AS receita_efetiva,
           SUM(margem_efetiva) AS margem_efetiva,
           SUM(CASE WHEN devolvido THEN quantidade ELSE 0 END) AS unidades_devolvidas,
           MODE(CASE WHEN devolvido THEN motivo_devolucao END) AS principal_motivo_declarado
    FROM vendas
    WHERE status_pagamento = 'Aprovado' AND CAST(data_pedido AS DATE) BETWEEN ? AND ?
      AND sku_id = ? AND quantidade IS NOT NULL AND quantidade > 0
    GROUP BY sku_id
), weighted_cost AS (
    SELECT sku_id, SUM(custo_produto) / NULLIF(SUM(quantidade), 0) AS custo_unitario_vendas
    FROM vendas
    WHERE status_pagamento = 'Aprovado' AND sku_id = ? AND quantidade > 0
      AND custo_produto IS NOT NULL AND custo_produto >= 0
    GROUP BY sku_id
)
SELECT e.sku_id, e.nome_produto, e.categoria, e.subcategoria, e.fornecedor_id,
       CAST(e.data_ultima_entrada AS DATE) AS data_ultima_entrada,
       e.estoque_fisico, e.estoque_reservado, e.estoque_disponivel, e.ponto_pedido,
       e.lead_time_reposicao AS lead_time_cadastral_dias, e.is_descontinuado,
       p.pedidos_aprovados, p.unidades_aprovadas, p.receita_efetiva, p.margem_efetiva,
       p.unidades_devolvidas, p.principal_motivo_declarado, c.custo_unitario_vendas,
       e.custo_unitario AS custo_unitario_estoque_auditoria,
       e.preco_venda_sugerido AS preco_sugerido_estoque_auditoria
FROM estoque e
LEFT JOIN period_sales p USING (sku_id)
LEFT JOIN weighted_cost c USING (sku_id)
WHERE e.sku_id = ?;
