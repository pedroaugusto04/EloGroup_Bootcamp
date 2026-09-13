WITH weighted_cost AS (
    SELECT sku_id, SUM(custo_produto) / NULLIF(SUM(quantidade), 0) AS custo_unitario_vendas
    FROM vendas
    WHERE status_pagamento = 'Aprovado' AND quantidade > 0
      AND custo_produto IS NOT NULL AND custo_produto >= 0
    GROUP BY sku_id
), period_economics AS (
    SELECT sku_id,
           SUM(receita_liquida) / NULLIF(SUM(quantidade), 0) AS preco_liquido_unitario,
           SUM(custo_frete) / NULLIF(SUM(quantidade), 0) AS frete_unitario
    FROM vendas
    WHERE status_pagamento = 'Aprovado' AND CAST(data_pedido AS DATE) BETWEEN ? AND ?
      AND quantidade > 0 AND receita_liquida IS NOT NULL AND receita_liquida > 0
    GROUP BY sku_id
), category_returns AS (
    SELECT categoria,
           SUM(CASE WHEN devolvido THEN quantidade ELSE 0 END) / NULLIF(SUM(quantidade), 0) AS taxa_devolucao_categoria
    FROM vendas
    WHERE status_pagamento = 'Aprovado' AND CAST(data_pedido AS DATE) BETWEEN ? AND ?
      AND quantidade > 0
    GROUP BY categoria
)
SELECT e.sku_id, e.nome_produto, e.categoria, e.estoque_disponivel,
       c.custo_unitario_vendas, p.preco_liquido_unitario, p.frete_unitario,
       r.taxa_devolucao_categoria
FROM estoque e
LEFT JOIN weighted_cost c USING (sku_id)
LEFT JOIN period_economics p USING (sku_id)
LEFT JOIN category_returns r ON r.categoria = e.categoria
WHERE e.is_descontinuado AND e.estoque_disponivel > 0
  AND (? IS NULL OR e.categoria = ?)
ORDER BY e.sku_id;
