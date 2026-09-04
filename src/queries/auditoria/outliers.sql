-- Limites de Tukey usados na documentação (1,5 x IQR).
-- Aplique cada bloco à view correspondente para reproduzir os números.

WITH s AS (
    SELECT quantile_cont(desconto_reais, 0.25) AS q1,
           quantile_cont(desconto_reais, 0.75) AS q3
    FROM vendas
), b AS (SELECT q1, q3, q3 - q1 AS iqr, q3 + 1.5 * (q3 - q1) AS limite_superior FROM s)
SELECT COUNT(*) AS registros, COUNT(*) FILTER (WHERE desconto_reais > limite_superior) AS outliers,
       limite_superior, MAX(desconto_reais) AS maximo
FROM vendas CROSS JOIN b GROUP BY limite_superior;

-- Para as demais métricas, substitua a coluna no bloco acima:
-- atendimento.tempo_resolucao_horas, atendimento.tempo_primeira_resposta_minutos,
-- atendimento.nota_csat, estoque.valor_total_estoque, estoque.estoque_disponivel,
-- clientes.ltv_acumulado, clientes.total_pedidos_historico, marketing.cac e marketing.roas.
