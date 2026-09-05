-- src/queries/repository/kpis_executivos_vendas.sql
-- Consolidação de métricas financeiras macro do ERP de Vendas (Pedidos Aprovados).

SELECT 
    COALESCE(SUM(receita_bruta), 0) AS gross_revenue,
    COALESCE(SUM(receita_liquida), 0) AS net_revenue,
    COALESCE(SUM(margem_calculada), 0) AS contribution_margin,
    COALESCE(COUNT(order_id), 0) AS total_orders,
    COALESCE(AVG(receita_liquida), 0) AS average_ticket,
    COALESCE(AVG(CASE WHEN devolvido = true THEN 1.0 ELSE 0.0 END) * 100.0, 0) AS return_rate_pct
FROM vendas
WHERE status_pagamento = 'Aprovado';
