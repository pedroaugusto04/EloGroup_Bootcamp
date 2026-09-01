-- ==============================================================================
-- Query: Cruzamento Vendas (SLA Logístico & Devoluções) vs Atendimento (CSAT & Custos)
-- Eixo 3: Análise Relacional Integrada
-- Tabelas: vendas, atendimento
-- ==============================================================================

SELECT 
    CASE 
        WHEN v.tempo_entrega_real <= 5 THEN '1. Rápido (1 a 5 dias)'
        WHEN v.tempo_entrega_real <= 10 THEN '2. Normal (6 a 10 dias)'
        WHEN v.tempo_entrega_real <= 15 THEN '3. Moderado (11 a 15 dias)'
        ELSE '4. Crítico (> 15 dias)'
    END AS faixa_entrega,
    COUNT(DISTINCT v.order_id) AS total_pedidos,
    COUNT(DISTINCT a.ticket_id) AS total_chamados_suporte,
    ROUND(COUNT(DISTINCT a.ticket_id) * 100.0 / NULLIF(COUNT(DISTINCT v.order_id), 0), 1) AS taxa_abertura_chamados_pct,
    ROUND(AVG(a.nota_csat), 2) AS csat_medio,
    ROUND(SUM(CASE WHEN a.csat_critico THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(a.ticket_id), 0), 1) AS pct_csat_critico,
    ROUND(SUM(CASE WHEN v.devolvido THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(v.order_id), 0), 1) AS taxa_devolucao_pct,
    ROUND(COALESCE(SUM(a.custo_operacional_ticket), 0.0), 2) AS custo_suporte_total,
    ROUND(COALESCE(SUM(a.custo_evitavel_automacao), 0.0), 2) AS custo_evitavel_automacao
FROM vendas v
LEFT JOIN atendimento a ON v.order_id = a.order_id
WHERE v.status_pagamento = 'Aprovado'
GROUP BY 1
ORDER BY 1;
