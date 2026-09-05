-- src/queries/repository/performance_categorias.sql
-- Rentabilidade, custo de mercadoria, custo de frete e descontos por categoria de produto.

SELECT 
    categoria AS category,
    SUM(receita_liquida) AS net_revenue,
    SUM(custo_produto) AS product_cost,
    SUM(custo_frete) AS shipping_cost,
    SUM(desconto_reais) AS discounts,
    SUM(margem_calculada) AS margin,
    (SUM(margem_calculada) / NULLIF(SUM(receita_liquida), 0)) * 100.0 AS margin_pct,
    COUNT(order_id) AS orders,
    AVG(CASE WHEN devolvido = true THEN 1.0 ELSE 0.0 END) * 100.0 AS return_rate
FROM vendas
WHERE status_pagamento = 'Aprovado'
GROUP BY categoria
ORDER BY net_revenue DESC;
