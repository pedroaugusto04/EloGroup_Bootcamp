-- ==============================================================================
-- Query: KPIs Agregados da Base de Clientes (Hipótese 5)
-- Finalidade: Total de clientes, LTV médio, frequência e ticket médio histórico.
-- Tabela Origem: clientes
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    COUNT(customer_id) AS total_clientes,
    COALESCE(AVG(ltv_acumulado), 0) AS ltv_medio,
    COALESCE(AVG(total_pedidos_historico), 0) AS frequencia_media,
    COALESCE(AVG(renda_estimada), 0) AS renda_media,
    COALESCE(AVG(idade), 0) AS idade_media,
    COALESCE(AVG(ticket_medio_historico), 0) AS ticket_medio_historico
FROM clientes
{where_sql};
