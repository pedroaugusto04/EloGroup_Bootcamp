-- ==============================================================================
-- Query: Volume de Pedidos e Faturamento por Método de Pagamento
-- Finalidade: Identificar a preferência do consumidor (Cartão de Crédito, PIX, Boleto, etc.)
--             e o impacto financeiro de cada meio de pagamento.
-- Tabela Origem: vendas
-- Granularidade: Método de Pagamento
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    metodo_pagamento,
    COUNT(order_id) AS total_pedidos,
    SUM(receita_liquida) AS receita_total
FROM vendas
{where_sql}
GROUP BY metodo_pagamento
ORDER BY total_pedidos DESC;
