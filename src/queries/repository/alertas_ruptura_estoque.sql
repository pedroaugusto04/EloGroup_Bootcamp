-- src/queries/repository/alertas_ruptura_estoque.sql
-- Lista de SKUs em ruptura ordenados pelo déficit de reposição em relação ao ponto de pedido.

SELECT 
    sku_id,
    nome_produto AS product_name,
    categoria AS category,
    estoque_disponivel AS available_stock,
    ponto_pedido AS reorder_point,
    lead_time_reposicao AS lead_time,
    status_disponibilidade AS status,
    custo_unitario AS unit_cost,
    preco_venda_sugerido AS selling_price
FROM estoque
WHERE em_ruptura = true
ORDER BY (ponto_pedido - estoque_disponivel) DESC
LIMIT {limit};
