-- src/queries/repository/resumo_segmentos_clientes.sql
-- Panorama dos segmentos RFM na base de clientes com LTV médio e ticket histórico.

SELECT 
    COALESCE(segmento_rfm, 'Não Definido') AS rfm_segment,
    COUNT(*) AS total_customers,
    (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM clientes)) AS pct_base,
    AVG(ltv_acumulado) AS average_ltv,
    AVG(total_pedidos_historico) AS average_orders,
    AVG(renda_estimada) AS average_income
FROM clientes
GROUP BY segmento_rfm
ORDER BY total_customers DESC;
