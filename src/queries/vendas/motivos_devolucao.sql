-- ==============================================================================
-- Query: Impacto Financeiro e Contagem por Motivo de Devolução
-- Finalidade: Identificar as principais causas de devolução de pedidos (defeito,
--             tamanho errado, arrependimento, atraso) e a receita comprometida.
-- Tabela Origem: vendas
-- Regra de Negócio: devolvido = true E status_pagamento = 'Aprovado'
-- ==============================================================================

SELECT 
    motivo_devolucao,
    COUNT(order_id) AS total_devolucoes,
    SUM(receita_liquida) AS valor_devolvido
FROM vendas
WHERE devolvido = true AND status_pagamento = 'Aprovado'
GROUP BY motivo_devolucao
ORDER BY total_devolucoes DESC;
