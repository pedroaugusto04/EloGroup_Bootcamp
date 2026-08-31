-- ==============================================================================
-- Query: Impacto Financeiro de Devoluções na Margem de Contribuição (Hipótese 6)
-- Finalidade: Mensurar estornos de receita e perda com frete de pedidos devolvidos.
-- Tabela Origem: vendas
-- ==============================================================================

SELECT 
    categoria,
    COUNT(order_id) AS total_pedidos,
    SUM(CASE WHEN devolvido = TRUE THEN 1 ELSE 0 END) AS pedidos_devolvidos,
    ROUND(SUM(CASE WHEN devolvido = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(order_id), 2) AS taxa_devolucao_pct,
    ROUND(SUM(receita_liquida), 2) AS receita_bruta_aprovada,
    ROUND(SUM(receita_devolvida), 2) AS receita_estornada,
    ROUND(SUM(custo_frete_perdido), 2) AS custo_frete_desperdicado,
    ROUND(SUM(margem_calculada), 2) AS margem_nominal,
    ROUND(SUM(margem_efetiva), 2) AS margem_efetiva_real
FROM vendas
WHERE status_pagamento = 'Aprovado'
GROUP BY categoria
ORDER BY receita_estornada DESC;
