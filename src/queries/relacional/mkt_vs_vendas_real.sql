-- ==============================================================================
-- Query: Cruzamento Marketing (Mídia Declarada) vs Vendas Reais (ERP)
-- Eixo 1: Análise Relacional Integrada
-- Tabelas: marketing, vendas
-- ==============================================================================

WITH mkt AS (
    SELECT 
        canal,
        SUM(investimento_reais) AS investimento_mkt,
        SUM(receita_gerada) AS receita_declarada_mkt,
        SUM(conversoes) AS conversoes_mkt,
        ROUND(SUM(receita_gerada) / NULLIF(SUM(investimento_reais), 0), 2) AS roas_declarado_mkt,
        ROUND(SUM(investimento_reais) / NULLIF(SUM(conversoes), 0), 2) AS cac_declarado_mkt
    FROM marketing
    GROUP BY canal
),
vendas_real AS (
    SELECT 
        canal,
        COUNT(order_id) AS total_pedidos_real,
        COUNT(DISTINCT customer_id) AS clientes_unicos_real,
        SUM(receita_liquida) AS receita_liquida_real,
        SUM(margem_calculada) AS margem_contribuicao_real,
        ROUND(AVG(receita_liquida), 2) AS ticket_medio_real,
        ROUND(AVG(desconto_reais), 2) AS desconto_medio_reais,
        ROUND(AVG(desconto_pct), 1) AS desconto_medio_pct,
        ROUND(SUM(margem_calculada) / NULLIF(SUM(receita_liquida), 0) * 100.0, 1) AS margem_pct_real,
        ROUND(AVG(CASE WHEN devolvido THEN 1.0 ELSE 0.0 END) * 100.0, 1) AS taxa_devolucao_pct
    FROM vendas
    WHERE status_pagamento = 'Aprovado'
    GROUP BY canal
)
SELECT 
    COALESCE(v.canal, m.canal) AS canal,
    COALESCE(m.investimento_mkt, 0.0) AS investimento_mkt,
    COALESCE(m.receita_declarada_mkt, 0.0) AS receita_declarada_mkt,
    COALESCE(m.roas_declarado_mkt, 0.0) AS roas_declarado_mkt,
    COALESCE(m.cac_declarado_mkt, 0.0) AS cac_declarado_mkt,
    COALESCE(v.total_pedidos_real, 0) AS total_pedidos_real,
    COALESCE(v.receita_liquida_real, 0.0) AS receita_liquida_real,
    COALESCE(v.margem_contribuicao_real, 0.0) AS margem_contribuicao_real,
    COALESCE(v.ticket_medio_real, 0.0) AS ticket_medio_real,
    COALESCE(v.desconto_medio_reais, 0.0) AS desconto_medio_reais,
    COALESCE(v.desconto_medio_pct, 0.0) AS desconto_medio_pct,
    COALESCE(v.margem_pct_real, 0.0) AS margem_pct_real,
    COALESCE(v.taxa_devolucao_pct, 0.0) AS taxa_devolucao_pct,
    ROUND(COALESCE(v.receita_liquida_real, 0.0) / NULLIF(m.investimento_mkt, 0), 2) AS roas_real_erp
FROM vendas_real v
FULL OUTER JOIN mkt m ON v.canal = m.canal
ORDER BY v.receita_liquida_real DESC;
