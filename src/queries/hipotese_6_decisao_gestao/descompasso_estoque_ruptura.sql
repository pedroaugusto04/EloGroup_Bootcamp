-- ==============================================================================
-- Query: Descompasso Operacional de Estoque: Descontinuados vs Rupturas (Hipótese 6)
-- Finalidade: Evidenciar a má alocação de capital de giro no estoque.
-- Tabela Origem: estoque
-- ==============================================================================

SELECT 
    status_disponibilidade,
    COUNT(sku_id) AS total_skus,
    ROUND(COUNT(sku_id) * 100.0 / SUM(COUNT(sku_id)) OVER(), 1) AS pct_skus,
    SUM(estoque_disponivel) AS unidades_disponiveis,
    ROUND(SUM(valor_total_estoque), 2) AS capital_total_estoque,
    ROUND(SUM(capital_travado_descontinuado), 2) AS capital_travado_descontinuado,
    ROUND(SUM(capital_em_risco_ruptura), 2) AS capital_em_risco_ruptura,
    ROUND(AVG(lead_time_reposicao), 1) AS lead_time_medio_dias
FROM estoque
GROUP BY status_disponibilidade
ORDER BY capital_total_estoque DESC;
