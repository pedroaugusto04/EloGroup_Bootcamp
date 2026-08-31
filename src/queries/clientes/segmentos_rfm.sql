-- ==============================================================================
-- Query: Detalhamento dos Segmentos de Clientes (Matriz RFM)
-- Finalidade: Avaliar a distribuição da base de clientes por clusters RFM (Campeão,
--             Fiel, Promissor, Em Risco, Churn, Hibernando), calculando o LTV total e médio.
-- Tabela Origem: clientes
-- Granularidade: Segmento RFM
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    COALESCE(segmento_rfm, 'Outros') AS segmento,
    COUNT(customer_id) AS total_clientes,
    ROUND((COUNT(customer_id) * 100.0 / (SELECT COUNT(*) FROM clientes)), 1) AS pct_base,
    ROUND(SUM(ltv_acumulado), 2) AS ltv_total,
    ROUND(AVG(ltv_acumulado), 2) AS ltv_medio,
    ROUND(AVG(total_pedidos_historico), 1) AS media_pedidos,
    ROUND(AVG(renda_estimada), 2) AS renda_media
FROM clientes
{where_sql}
GROUP BY segmento_rfm
ORDER BY total_clientes DESC;
