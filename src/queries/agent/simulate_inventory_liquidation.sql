-- ==============================================================================
-- Query: simulate_inventory_liquidation.sql
-- Finalidade: Simulação de liquidação e destravamento de caixa com desconto.
-- Métricas: Preço com desconto, receita projetada e margem de contribuição.
-- Parâmetros dinâmicos:
--   - {discount_factor}: Fator multiplicativo de preço (ex: 0.70 para 30% de desconto)
--   - {cat_filter}: Cláusula AND opcional para filtro por categoria
-- ==============================================================================

WITH cost_vendas AS (
    SELECT 
        sku_id,
        ROUND(AVG(receita_liquida / NULLIF(quantidade, 0)), 2) AS preco_venda_medio,
        ROUND(AVG(custo_produto / NULLIF(quantidade, 0)), 2) AS custo_medio_real
    FROM vendas
    WHERE status_pagamento = 'Aprovado'
    GROUP BY sku_id
)
SELECT 
    e.sku_id,
    e.nome_produto,
    e.categoria,
    e.estoque_disponivel,
    e.preco_venda_sugerido AS preco_original,
    ROUND(e.preco_venda_sugerido * {discount_factor}, 2) AS preco_liquidacao,
    e.custo_unitario AS custo_unitario,
    ROUND(e.estoque_disponivel * e.custo_unitario, 2) AS capital_travado_custo,
    ROUND(e.estoque_disponivel * e.preco_venda_sugerido * {discount_factor}, 2) AS receita_caixa_projetada,
    ROUND(
        (e.estoque_disponivel * e.preco_venda_sugerido * {discount_factor}) - 
        (e.estoque_disponivel * e.custo_unitario), 2
    ) AS margem_contribuicao_projetada,
    c.preco_venda_medio AS preco_medio_historico_vendas,
    c.custo_medio_real AS custo_medio_historico_vendas
FROM estoque e
LEFT JOIN cost_vendas c ON e.sku_id = c.sku_id
WHERE e.is_descontinuado = true AND e.estoque_disponivel > 0 {cat_filter}
ORDER BY capital_travado_custo DESC;
