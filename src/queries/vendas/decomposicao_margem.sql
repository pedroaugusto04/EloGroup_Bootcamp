-- ==============================================================================
-- Query: Decomposição da Cascata de Valor e Rentabilidade (Ponte de Margem)
-- Finalidade: Rastrear exatamente onde a receita bruta sofre deduções e custos:
--             Receita Bruta -> Descontos -> Receita Líquida -> Custo Produto (CMV) -> Frete -> Margem Líquida.
-- Tabela Origem: vendas
-- Regra de Negócio: Apenas pedidos com status_pagamento = 'Aprovado'
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    SUM(receita_bruta) AS bruta,
    SUM(desconto_reais) AS descontos,
    SUM(receita_liquida) AS liquida,
    SUM(custo_produto) AS custo_prod,
    SUM(custo_frete) AS custo_frete,
    SUM(margem_calculada) AS margem_final
FROM vendas
{where_sql};
