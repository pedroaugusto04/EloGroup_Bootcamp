-- ==============================================================================
-- Query: Volume e Performance por Canal de Entrada (Hipótese 4)
-- Finalidade: Analisar canais de suporte (WhatsApp, E-mail, Chatbot, Telefone)
-- Tabela Origem: atendimento
-- Parâmetros: {where_sql}
-- ==============================================================================

SELECT 
    canal_entrada,
    COUNT(ticket_id) AS total_tickets,
    ROUND(COUNT(ticket_id) * 100.0 / SUM(COUNT(ticket_id)) OVER(), 2) AS pct_canal,
    ROUND(AVG(nota_csat), 2) AS csat_medio,
    ROUND(AVG(tempo_primeira_resposta_minutos), 1) AS tempo_resposta_min,
    ROUND(AVG(tempo_resolucao_horas), 1) AS tempo_resolucao_h,
    ROUND(SUM(custo_operacional_ticket), 2) AS custo_total
FROM atendimento
{where_sql}
GROUP BY canal_entrada
ORDER BY total_tickets DESC;
