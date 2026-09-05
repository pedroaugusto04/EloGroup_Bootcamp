-- src/queries/repository/amostra_tickets_suporte.sql
-- Amostra recente de chamados de atendimento ao cliente.

SELECT * FROM atendimento
ORDER BY data_abertura DESC
LIMIT {limit};
