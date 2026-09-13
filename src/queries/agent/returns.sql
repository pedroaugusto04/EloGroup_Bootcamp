-- Resume devoluções aprovadas por SKU e o motivo declarado na janela selecionada.
SELECT sku_id, ANY_VALUE(produto) AS produto, ANY_VALUE(categoria) AS categoria,
       COUNT(*) AS pedidos_aprovados,
       SUM(CASE WHEN devolvido THEN 1 ELSE 0 END) AS pedidos_devolvidos,
       SUM(CASE WHEN devolvido THEN quantidade ELSE 0 END) AS unidades_devolvidas,
       SUM(CASE WHEN devolvido THEN quantidade ELSE 0 END) / NULLIF(SUM(quantidade), 0) AS taxa_devolucao,
       MODE(CASE WHEN devolvido THEN motivo_devolucao END) AS principal_motivo_declarado
FROM vendas
WHERE status_pagamento = 'Aprovado'
  AND CAST(data_pedido AS DATE) BETWEEN ? AND ?
  AND sku_id IS NOT NULL AND TRIM(sku_id) <> ''
  AND quantidade IS NOT NULL AND quantidade > 0
GROUP BY sku_id
HAVING COUNT(*) >= ? AND SUM(CASE WHEN devolvido THEN 1 ELSE 0 END) >= ?
ORDER BY taxa_devolucao DESC, pedidos_devolvidos DESC, sku_id
