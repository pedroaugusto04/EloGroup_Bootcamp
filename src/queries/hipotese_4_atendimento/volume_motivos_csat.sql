-- ==============================================================================
-- Query: Volume de Chamados, CSAT e Tempo de Resposta por Motivo (Hipótese 4)
-- Finalidade: Avaliar a distribuição de motivos e o impacto no índice de satisfação.
-- Tabela Origem: atendimento
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    categoria_problema,
    COUNT(ticket_id) AS total_tickets,
    ROUND(AVG(nota_csat), 2) AS csat_medio,
    ROUND(AVG(tempo_primeira_resposta_minutos), 1) AS tempo_resposta_min,
    ROUND(AVG(tempo_resolucao_horas), 1) AS tempo_resolucao_h,
    ROUND(SUM(custo_operacional_ticket), 2) AS custo_total
FROM atendimento
{where_sql}
GROUP BY categoria_problema
ORDER BY total_tickets DESC;
