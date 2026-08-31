-- ==============================================================================
-- Query: KPIs Gerais de Marketing e Aquisição
-- Finalidade: Calcular os indicadores macro de investimento em mídia, receita gerada,
--             ROAS global (Receita / Investimento), CAC médio (Investimento / Conversões) e total de conversões.
-- Tabela Origem: marketing
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    SUM(investimento_reais) AS invest_total,
    SUM(receita_gerada) AS rec_total,
    SUM(conversoes) AS conv_total,
    SUM(cliques) AS cliques_total,
    SUM(impressoes) AS imp_total,
    SUM(receita_gerada) / NULLIF(SUM(investimento_reais), 0) AS roas_global,
    SUM(investimento_reais) / NULLIF(SUM(conversoes), 0) AS cac_medio
FROM marketing
{where_sql};
