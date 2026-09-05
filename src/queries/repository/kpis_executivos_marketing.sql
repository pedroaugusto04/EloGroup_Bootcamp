-- src/queries/repository/kpis_executivos_marketing.sql
-- Consolidação de investimento, receita reportada e CAC médio de campanhas de marketing.

SELECT 
    COALESCE(SUM(investimento_reais), 0) AS investment_mkt,
    COALESCE(SUM(receita_gerada), 0) AS revenue_mkt,
    COALESCE(SUM(investimento_reais) / NULLIF(SUM(conversoes), 0), 0) AS average_cac
FROM marketing;
