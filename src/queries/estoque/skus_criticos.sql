-- ==============================================================================
-- Query: SKUs em Ruptura ou Nível de Estoque Crítico
-- Finalidade: Listar os produtos onde o estoque disponível está abaixo do ponto de reposição,
--             calculando o déficit exato de unidades necessárias para compra imediata.
-- Tabela Origem: estoque
-- Parâmetros: {crit_where} e {limit}
-- ==============================================================================

SELECT 
    sku_id,
    nome_produto,
    categoria,
    estoque_disponivel,
    ponto_pedido,
    (ponto_pedido - estoque_disponivel) AS deficit_unidades,
    lead_time_reposicao AS lead_time_dias,
    custo_unitario,
    preco_venda_sugerido
FROM estoque
{crit_where}
ORDER BY deficit_unidades DESC
LIMIT {limit};
