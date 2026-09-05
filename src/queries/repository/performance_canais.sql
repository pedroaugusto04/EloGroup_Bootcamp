-- src/queries/repository/performance_canais.sql
-- Desempenho agregado de vendas por canal cruzado com investimentos de marketing, ROAS e devoluções.

WITH v AS (
    SELECT 
        canal AS channel,
        SUM(receita_liquida) AS net_revenue,
        SUM(margem_calculada) AS margin,
        COUNT(order_id) AS orders,
        AVG(receita_liquida) AS average_ticket,
        AVG(CASE WHEN devolvido = true THEN 1.0 ELSE 0.0 END) * 100.0 AS return_rate
    FROM vendas
    WHERE status_pagamento = 'Aprovado'
    GROUP BY canal
),
m AS (
    SELECT 
        canal AS channel,
        SUM(investimento_reais) AS investment,
        SUM(receita_gerada) AS rec_mkt,
        SUM(conversoes) AS conversions
    FROM marketing
    GROUP BY canal
)
SELECT 
    v.channel,
    v.net_revenue,
    v.margin,
    (v.margin / NULLIF(v.net_revenue, 0)) * 100.0 AS margin_pct,
    v.orders,
    v.average_ticket,
    COALESCE(m.investment, 0) AS investment,
    COALESCE(m.investment / NULLIF(m.conversions, 0), 0) AS cac,
    COALESCE(m.rec_mkt / NULLIF(m.investment, 0), 0) AS roas,
    v.return_rate
FROM v
LEFT JOIN m ON v.channel = m.channel
ORDER BY v.net_revenue DESC;
