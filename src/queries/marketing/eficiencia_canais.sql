-- ==============================================================================
-- Query: Matriz Completa de Eficiência de Mídia por Canal
-- Finalidade: Avaliar a performance do funil de marketing ponta a ponta:
--             Investimento -> Impressões -> Cliques (CTR %) -> Conversões (Taxa de Conversão %) -> CAC e ROAS.
-- Tabela Origem: marketing
-- Granularidade: Canal de Mídia
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    canal,
    SUM(investimento_reais) AS investimento,
    SUM(receita_gerada) AS receita_gerada,
    SUM(conversoes) AS conversoes,
    SUM(cliques) AS cliques,
    SUM(impressoes) AS impressoes,
    ROUND(SUM(receita_gerada) / NULLIF(SUM(investimento_reais), 0), 2) AS roas,
    ROUND(SUM(investimento_reais) / NULLIF(SUM(conversoes), 0), 2) AS cac,
    ROUND((SUM(cliques) / NULLIF(SUM(impressoes), 0)) * 100.0, 2) AS ctr_pct,
    ROUND((SUM(conversoes) / NULLIF(SUM(cliques), 0)) * 100.0, 2) AS taxa_conversao_pct
FROM marketing
{where_sql}
GROUP BY canal
ORDER BY investimento DESC;
