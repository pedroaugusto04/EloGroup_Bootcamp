-- src/queries/repository/kpis_executivos_atendimento.sql
-- Média global de CSAT (Satisfação do Cliente) no canal de suporte.

SELECT 
    COALESCE(AVG(nota_csat), 0) AS average_csat 
FROM atendimento;
