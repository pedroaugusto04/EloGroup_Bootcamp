-- ==============================================================================
-- Query: Diagnóstico dos Gargalos Financeiros e Ineficiências de Decisão (Hipótese 6)
-- Finalidade: Consolidar perdas geradas por falta de integração de dados em tempo real.
-- Tabelas Origem: estoque, vendas, atendimento, marketing
-- ==============================================================================

SELECT 
    'Estoque Descontinuado Travado' AS dimensao_ineficiencia,
    'Operações & Estoque' AS area_responsavel,
    ROUND(SUM(capital_travado_descontinuado), 2) AS impacto_financeiro_reais,
    'R$ 14,8M imobilizados em SKUs fora de linha sem queima promocional ágil' AS descricao_gargalo,
    'Realizar queima flash com desconto controlado e liberar capital de giro' AS recomendacao_acao
FROM estoque

UNION ALL

SELECT 
    'Estoque em Risco de Ruptura',
    'Operações & Estoque',
    ROUND(SUM(capital_em_risco_ruptura), 2),
    'SKUs de alta demanda com estoque abaixo do ponto de pedido ameaçando faturamento',
    'Acionar reposição prioritária e implantar S&OP preditivo'
FROM estoque

UNION ALL

SELECT 
    'Perda com Devoluções e Frete Perdido',
    'Vendas & Qualidade',
    ROUND(SUM(receita_devolvida + custo_frete_perdido), 2),
    'Estorno de receita bruta e custo de frete desperdiçado em devoluções',
    'Implantar provador virtual de medidas e homologação rigorosa de fornecedores'
FROM vendas
WHERE status_pagamento = 'Aprovado'

UNION ALL

SELECT 
    'Custo Evitável de Atendimento N1',
    'Atendimento & CX',
    ROUND(SUM(custo_evitavel_automacao), 2),
    'Chamados repetitivos de rastreamento e dúvidas simples com triagem manual',
    'Implantar chatbot/notificações proativas via IA Conversacional'
FROM atendimento

ORDER BY impacto_financeiro_reais DESC;
