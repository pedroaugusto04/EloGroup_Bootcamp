-- ==============================================================================
-- Query: KPIs Gerais da Base de Clientes
-- Finalidade: Calcular o tamanho da base, LTV (Lifetime Value) médio acumulado,
--             frequência média histórica de compras, renda estimada e idade média.
-- Tabela Origem: clientes
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    COUNT(customer_id) AS total_clientes,
    AVG(ltv_acumulado) AS ltv_medio,
    AVG(total_pedidos_historico) AS frequencia_media,
    AVG(renda_estimada) AS renda_media,
    AVG(idade) AS idade_media
FROM clientes
{where_sql};
