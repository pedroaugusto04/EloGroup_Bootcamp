-- Resume demanda, receita efetiva e margem efetiva por SKU na janela selecionada.
SELECT sku_id, ANY_VALUE(produto) AS produto, ANY_VALUE(categoria) AS categoria,
       COUNT(*) AS pedidos_aprovados, SUM(quantidade) AS unidades_aprovadas,
       SUM(receita_liquida_efetiva) AS receita_efetiva,
       SUM(margem_efetiva) AS margem_efetiva,
       SUM(CASE WHEN devolvido THEN quantidade ELSE 0 END) AS unidades_devolvidas
FROM vendas
WHERE status_pagamento = 'Aprovado'
  AND CAST(data_pedido AS DATE) BETWEEN ? AND ?
  AND sku_id IS NOT NULL AND TRIM(sku_id) <> ''
  AND quantidade IS NOT NULL AND quantidade > 0
  AND (? IS NULL OR categoria = ?)
GROUP BY sku_id
ORDER BY margem_efetiva DESC, unidades_aprovadas DESC, sku_id
