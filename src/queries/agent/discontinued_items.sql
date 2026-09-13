-- Lista itens descontinuados e valora seus saldos físico e disponível com custo histórico de Vendas.
WITH weighted_cost AS (
    SELECT sku_id, SUM(custo_produto) / NULLIF(SUM(quantidade), 0) AS custo_unitario_vendas
    FROM vendas
    WHERE status_pagamento = 'Aprovado' AND quantidade > 0
      AND custo_produto IS NOT NULL AND custo_produto >= 0
    GROUP BY sku_id
)
SELECT e.sku_id, e.nome_produto, e.categoria, e.fornecedor_id,
       e.estoque_fisico, e.estoque_reservado, e.estoque_disponivel,
       c.custo_unitario_vendas,
       e.estoque_fisico * c.custo_unitario_vendas AS capital_fisico,
       e.estoque_disponivel * c.custo_unitario_vendas AS capital_disponivel
FROM estoque e
LEFT JOIN weighted_cost c USING (sku_id)
WHERE e.is_descontinuado AND (? IS NULL OR e.categoria = ?)
ORDER BY capital_disponivel DESC NULLS LAST, e.sku_id
