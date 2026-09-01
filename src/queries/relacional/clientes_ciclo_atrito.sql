-- ==============================================================================
-- Query: Cruzamento Clientes (Segmento RFM & LTV) vs Vendas & Atendimento (Atrito nos VIPs)
-- Eixo 4: Análise Relacional Integrada
-- Tabelas: clientes, vendas, atendimento
-- ==============================================================================

WITH cli_tickets AS (
    SELECT 
        customer_id, 
        COUNT(ticket_id) AS total_tickets,
        AVG(nota_csat) AS csat_medio,
        SUM(CASE WHEN csat_critico THEN 1 ELSE 0 END) AS tickets_criticos,
        SUM(custo_operacional_ticket) AS custo_suporte_cliente
    FROM atendimento 
    GROUP BY customer_id
),
cli_vendas AS (
    SELECT 
        customer_id, 
        COUNT(order_id) AS pedidos_aprovados,
        SUM(receita_liquida) AS gasto_total,
        SUM(margem_calculada) AS margem_total,
        SUM(CASE WHEN devolvido THEN 1 ELSE 0 END) AS total_devolucoes,
        AVG(desconto_reais) AS desconto_medio_cliente
    FROM vendas 
    WHERE status_pagamento = 'Aprovado' 
    GROUP BY customer_id
)
SELECT 
    c.segmento_rfm,
    COUNT(c.customer_id) AS total_clientes,
    ROUND(AVG(c.ltv_acumulado), 2) AS ltv_medio,
    ROUND(SUM(c.ltv_acumulado), 2) AS ltv_total_segmento,
    ROUND(AVG(c.total_pedidos_historico), 1) AS media_pedidos_historico,
    ROUND(AVG(COALESCE(t.total_tickets, 0)), 2) AS chamados_medios_por_cliente,
    ROUND(AVG(COALESCE(t.csat_medio, 3.0)), 2) AS csat_medio_atendimento,
    SUM(CASE WHEN COALESCE(t.tickets_criticos, 0) > 0 THEN 1 ELSE 0 END) AS clientes_com_csat_critico,
    ROUND(SUM(CASE WHEN COALESCE(t.tickets_criticos, 0) > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(c.customer_id), 1) AS pct_clientes_com_csat_critico,
    ROUND(SUM(COALESCE(v.total_devolucoes, 0)) * 100.0 / NULLIF(SUM(COALESCE(v.pedidos_aprovados, 0)), 0), 1) AS taxa_devolucao_pedidos_pct,
    ROUND(SUM(COALESCE(t.custo_suporte_cliente, 0)), 2) AS custo_suporte_segmento
FROM clientes c
LEFT JOIN cli_tickets t ON c.customer_id = t.customer_id
LEFT JOIN cli_vendas v ON c.customer_id = v.customer_id
GROUP BY c.segmento_rfm
ORDER BY ltv_medio DESC;
