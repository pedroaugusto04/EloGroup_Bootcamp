-- ==============================================================================
-- Query: Perfil Demográfico, Dispositivo e Nível de Fidelidade por Segmento (Hipótese 5)
-- Finalidade: Cruzar segmentos RFM com estado, dispositivo e programa de fidelidade.
-- Tabela Origem: clientes
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    segmento_rfm,
    nivel_fidelidade,
    dispositivo_principal,
    COUNT(customer_id) AS total_clientes,
    ROUND(AVG(ltv_acumulado), 2) AS ltv_medio,
    ROUND(AVG(renda_estimada), 2) AS renda_media
FROM clientes
{where_sql}
GROUP BY segmento_rfm, nivel_fidelidade, dispositivo_principal
ORDER BY total_clientes DESC;
