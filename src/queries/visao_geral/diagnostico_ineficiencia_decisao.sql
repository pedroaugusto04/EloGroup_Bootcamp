-- ==============================================================================
-- Query: Diagnóstico de Ineficiências e Oportunidades de Decisão (Cross-Functional)
-- Finalidade: Consolidar as principais perdas financeiras e gargalos operacionais
--             decorrentes de decisões lentas ou fragmentadas entre áreas.
-- Tabelas Origem: estoque, vendas, atendimento, marketing
-- ==============================================================================

SELECT 
    'Estoque Descontinuado Travado' AS dimensao_ineficiencia,
    'Operações & Estoque' AS area_responsavel,
    ROUND(SUM(capital_travado_descontinuado), 2) AS impacto_financeiro_reais,
    'Capital de giro imobilizado em produtos fora de linha sem liquidação ágil' AS descricao_gargalo,
    'Realizar queima promocional e liberar caixa imediato' AS recomendacao_acao
FROM estoque

UNION ALL

SELECT 
    'Estoque em Risco de Ruptura',
    'Operações & Estoque',
    ROUND(SUM(capital_em_risco_ruptura), 2),
    'SKUs de alta demanda com estoque abaixo do ponto de pedido ameaçando receita',
    'Acionar reposição prioritária e integrar S&OP preditivo'
FROM estoque

UNION ALL

SELECT 
    'Perda com Devoluções e Frete Perdido',
    'Vendas & Qualidade',
    ROUND(SUM(receita_devolvida + custo_frete_perdido), 2),
    'Estorno de receita bruta e custo de frete desperdiçado em pedidos devolvidos',
    'Implantar provador virtual de medidas e controle de qualidade de fornecedores'
FROM vendas
WHERE status_pagamento = 'Aprovado'

UNION ALL

SELECT 
    'Custo Evitável de Atendimento N1',
    'Atendimento & CX',
    ROUND(SUM(custo_evitavel_automacao), 2),
    'Chamados repetitivos de rastreamento de pedidos e dúvidas técnicas triados manualmente',
    'Implantar chatbot e notificações proativas via IA Conversacional'
FROM atendimento

ORDER BY impacto_financeiro_reais DESC;
