-- Checagens reproduzíveis para as inconsistências documentadas.
-- Execute após criar as views DuckDB (src.infrastructure.database.DuckDBRepository).

-- Cobertura temporal e volume por base
SELECT 'vendas' AS tabela, COUNT(*) AS registros, MIN(data_pedido) AS data_min, MAX(data_pedido) AS data_max FROM vendas
UNION ALL SELECT 'marketing', COUNT(*), MIN(data_inicio), MAX(data_fim) FROM marketing
UNION ALL SELECT 'estoque', COUNT(*), MIN(data_ultima_entrada), MAX(data_ultima_entrada) FROM estoque
UNION ALL SELECT 'clientes', COUNT(*), MIN(data_cadastro), MAX(data_cadastro) FROM clientes
UNION ALL SELECT 'atendimento', COUNT(*), MIN(data_abertura), MAX(data_abertura) FROM atendimento;

-- Vínculo Clientes x Vendas e pedidos anteriores ao cadastro
SELECT
    COUNT(DISTINCT v.customer_id) AS clientes_com_venda,
    SUM(CASE WHEN v.data_pedido < c.data_cadastro THEN 1 ELSE 0 END) AS pedidos_antes_cadastro
FROM vendas v
LEFT JOIN clientes c USING (customer_id);

-- Tickets citando pedidos ausentes/presentes em Vendas
SELECT
    COUNT(DISTINCT a.order_id) AS pedidos_citados,
    COUNT(DISTINCT CASE WHEN v.order_id IS NULL THEN a.order_id END) AS pedidos_sem_venda,
    COUNT(DISTINCT CASE WHEN v.order_id IS NOT NULL THEN a.order_id END) AS pedidos_com_venda
FROM atendimento a
LEFT JOIN vendas v USING (order_id);

-- Comparação de custos unitários para SKUs presentes nas duas bases
SELECT corr(v.custo_produto / NULLIF(v.quantidade, 0), e.custo_unitario) AS correlacao_custo_unitario
FROM vendas v
JOIN estoque e USING (sku_id)
WHERE v.quantidade > 0;

-- Totais financeiros que não devem ser misturados entre fontes/períodos
SELECT 'vendas_aprovadas' AS fonte, SUM(receita_liquida_efetiva) AS receita, COUNT(*) AS eventos
FROM vendas WHERE status_pagamento = 'Aprovado'
UNION ALL
SELECT 'marketing_declarado', SUM(receita_gerada), SUM(conversoes) FROM marketing;

-- Concentração de pedidos no maior cliente
SELECT customer_id, COUNT(*) AS pedidos, COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () AS pct_pedidos
FROM vendas
GROUP BY customer_id
ORDER BY pedidos DESC
LIMIT 1;

-- Reconciliação dos campos históricos da base Clientes com a base Vendas (somente clientes com venda)
WITH vendas_resumo AS (
    SELECT customer_id, COUNT(*) AS pedidos_vendas, SUM(receita_liquida) AS receita_vendas
    FROM vendas GROUP BY customer_id
)
SELECT COUNT(*) AS clientes_comparados,
       SUM(CASE WHEN c.total_pedidos_historico <> e.pedidos_vendas THEN 1 ELSE 0 END) AS pedidos_divergentes,
       AVG(c.ltv_acumulado - e.receita_vendas) AS diferenca_media_ltv_receita
FROM clientes c JOIN vendas_resumo e USING (customer_id);
