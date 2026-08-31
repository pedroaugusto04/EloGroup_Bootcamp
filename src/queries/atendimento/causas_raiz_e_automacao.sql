-- ==============================================================================
-- Query: Diagnóstico de Causas-Raiz e Potencial de Automação no Atendimento
-- Finalidade: Avaliar volume, CSAT, tempo de resposta/resolução, custo operacional
--             e economia estimada por automação inteligente (N1 / IA Conversacional).
-- Tabela Origem: atendimento
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    categoria_problema,
    COUNT(ticket_id) AS total_tickets,
    ROUND(COUNT(ticket_id) * 100.0 / SUM(COUNT(ticket_id)) OVER(), 2) AS pct_total,
    ROUND(AVG(nota_csat), 2) AS csat_medio,
    SUM(CASE WHEN csat_critico = TRUE THEN 1 ELSE 0 END) AS tickets_detratores,
    ROUND(AVG(tempo_primeira_resposta_minutos), 1) AS tempo_resposta_medio_min,
    ROUND(AVG(tempo_resolucao_horas), 1) AS tempo_resolucao_medio_h,
    ROUND(SUM(custo_operacional_ticket), 2) AS custo_operacional_total,
    is_automatizavel,
    ROUND(SUM(custo_evitavel_automacao), 2) AS custo_evitavel_automacao
FROM atendimento
{where_sql}
GROUP BY categoria_problema, is_automatizavel
ORDER BY total_tickets DESC;
