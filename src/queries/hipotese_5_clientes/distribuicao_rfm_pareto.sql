-- ==============================================================================
-- Query: Distribuição RFM e Concentração de Valor (Pareto) (Hipótese 5)
-- Finalidade: Avaliar a concentração de faturamento e LTV entre segmentos de clientes.
-- Tabela Origem: clientes
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    COALESCE(segmento_rfm, 'Não Definido') AS segmento,
    COUNT(customer_id) AS total_clientes,
    ROUND(COUNT(customer_id) * 100.0 / SUM(COUNT(customer_id)) OVER(), 2) AS pct_base,
    ROUND(SUM(ltv_acumulado), 2) AS ltv_total,
    ROUND(SUM(ltv_acumulado) * 100.0 / SUM(SUM(ltv_acumulado)) OVER(), 2) AS pct_ltv_total,
    ROUND(AVG(ltv_acumulado), 2) AS ltv_medio,
    ROUND(AVG(total_pedidos_historico), 1) AS media_pedidos,
    ROUND(AVG(ticket_medio_historico), 2) AS ticket_medio_historico,
    ROUND(AVG(renda_estimada), 2) AS renda_media,
    ROUND(AVG(idade), 1) AS idade_media
FROM clientes
{where_sql}
GROUP BY segmento_rfm
ORDER BY ltv_total DESC;
