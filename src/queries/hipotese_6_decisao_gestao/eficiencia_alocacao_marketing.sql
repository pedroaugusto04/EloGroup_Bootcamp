-- ==============================================================================
-- Query: Eficiência de Alocação de Orçamento de Marketing (Hipótese 6)
-- Finalidade: Analisar retorno sobre investimento (ROAS) e CAC por canal de mídia.
-- Tabela Origem: marketing
-- ==============================================================================

SELECT 
    canal,
    COUNT(campanha_id) AS total_campanhas,
    ROUND(SUM(investimento_reais), 2) AS investimento_total,
    ROUND(SUM(receita_gerada), 2) AS receita_total,
    ROUND(SUM(receita_gerada) / NULLIF(SUM(investimento_reais), 0), 2) AS roas_ponderado,
    ROUND(AVG(cac), 2) AS cac_medio,
    ROUND(AVG(taxa_conversao_pct), 2) AS taxa_conversao_media_pct,
    ROUND(SUM(lucro_bruto_mkt), 2) AS lucro_bruto_midia
FROM marketing
GROUP BY canal
ORDER BY investimento_total DESC;
