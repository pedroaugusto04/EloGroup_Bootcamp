-- ==============================================================================
-- Query: KPIs Gerais de Suporte e Atendimento ao Cliente
-- Finalidade: Medir o total de tickets recebidos, nota média de satisfação (CSAT),
--             tempo médio de primeira resposta (min), tempo de resolução (h) e custo operacional total.
-- Tabela Origem: atendimento
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    COUNT(ticket_id) AS total_tickets,
    AVG(nota_csat) AS csat_medio,
    AVG(tempo_primeira_resposta_minutos) AS tempo_resposta_min,
    MEDIAN(tempo_primeira_resposta_minutos) AS tempo_resposta_mediana_min,
    ROUND(AVG(CASE WHEN strftime(data_fechamento, '%Y-%m-%d') != '2025-12-31' THEN tempo_resolucao_horas END), 1) AS tempo_resolucao_h,
    SUM(custo_operacional_ticket) AS custo_total
FROM atendimento
{where_sql};

