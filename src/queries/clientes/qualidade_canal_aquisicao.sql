-- ==============================================================================
-- Query: Qualidade de Aquisição de Clientes por Canal de Primeira Compra
-- Finalidade: Avaliar LTV acumulado, CAC estimado, proporção de clientes de alto valor
--             (Campeões/Fiéis) vs clientes em risco/churn por canal de origem.
-- Tabelas Origem: clientes, vendas, marketing
-- Parâmetros: {where_sql}
-- ==============================================================================

WITH first_order AS (
    SELECT 
        customer_id, 
        canal AS canal_aquisicao, 
        MIN(data_pedido) AS data_primeira_compra
    FROM vendas
    WHERE status_pagamento = 'Aprovado'
    GROUP BY customer_id, canal
    QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY data_primeira_compra ASC) = 1
),
mkt_avg AS (
    SELECT 
        canal AS canal_aquisicao, 
        AVG(cac) AS cac_medio,
        AVG(roas) AS roas_medio
    FROM marketing
    GROUP BY canal
)
SELECT 
    f.canal_aquisicao,
    COUNT(c.customer_id) AS total_clientes,
    ROUND(COUNT(c.customer_id) * 100.0 / SUM(COUNT(c.customer_id)) OVER(), 2) AS pct_base_amostral,
    ROUND(AVG(c.ltv_acumulado), 2) AS ltv_medio,
    ROUND(SUM(c.ltv_acumulado), 2) AS ltv_total,
    ROUND(AVG(c.total_pedidos_historico), 1) AS media_pedidos,
    ROUND(m.cac_medio, 2) AS cac_estimado,
    ROUND(AVG(c.ltv_acumulado) / NULLIF(m.cac_medio, 0), 2) AS ltv_cac_ratio,
    SUM(CASE WHEN c.segmento_rfm IN ('Campeão', 'Fiel') THEN 1 ELSE 0 END) AS clientes_alto_valor,
    ROUND(SUM(CASE WHEN c.segmento_rfm IN ('Campeão', 'Fiel') THEN 1 ELSE 0 END) * 100.0 / COUNT(c.customer_id), 1) AS pct_alto_valor,
    SUM(CASE WHEN c.segmento_rfm IN ('Em Risco', 'Hibernando', 'Churn') THEN 1 ELSE 0 END) AS clientes_risco_churn,
    ROUND(SUM(CASE WHEN c.segmento_rfm IN ('Em Risco', 'Hibernando', 'Churn') THEN 1 ELSE 0 END) * 100.0 / COUNT(c.customer_id), 1) AS pct_risco_churn
FROM clientes c
JOIN first_order f ON c.customer_id = f.customer_id
LEFT JOIN mkt_avg m ON f.canal_aquisicao = m.canal_aquisicao
GROUP BY f.canal_aquisicao, m.cac_medio
ORDER BY ltv_total DESC;
