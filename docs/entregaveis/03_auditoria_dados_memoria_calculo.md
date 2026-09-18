# Auditoria de dados
**Bootcamp EloGroup 2026 · Grupo 14**  
**Autores:** Pedro Augusto e Pedro Lobo

---

## Objetivo

Registrar os critérios e cálculos que sustentam o diagnóstico e o business case.

## Validações principais

| Tema | Valor validado | Critério |
| --- | ---: | --- |
| Vendas | R$ 16,67M de receita líquida | Pedidos aprovados no período disponível (R$ 14,17M após estorno de devoluções). |
| Margem | 54,2% a 54,9% | Estabilidade mensal da margem de contribuição. |
| Estoque | R$ 6,1M imobilizados (206 SKUs elegíveis) | Saldo de descontinuados com histórico em Vendas (207 no cadastro físico). |
| Liquidação | R$ 4,14M de receita pós-devoluções | 50% de sell-through, 30% de desconto e devolução de 14,88%. |
| Descontos | R$ 1,80M/ano de margem potencial | Recuperação estimada de 50% dos R$ 3,6M concedidos acima de 20%. |
| Atendimento | R$ 238,5 mil de custo endereçável no período | Rastreio e dúvidas técnicas representam 44,9% dos tickets. |

## Contrato de dados: inconsistências relacionais identificadas

A auditoria cruzada identificou 7 divergências estruturais entre as tabelas fornecidas no Data Room. Essas divergências explicam por que certas análises não devem ser utilizadas para tomadas de decisão causais antes de saneamento cadastral:

1. **Marketing versus Vendas (Atribuição):** as campanhas declaram 38,2 milhões de conversões virtuais em 2023, enquanto Vendas registra 26,5 mil pedidos em 2023. As transações não contêm vínculo, inviabilizando o cálculo de ROAS causal por canal.
2. **Base de Clientes versus Vendas (Cobertura de clientes):** apenas 346 dos 15.000 clientes cadastrados aparecem no histórico transacional de Vendas. A correlação entre o LTV informado no cadastro de clientes e o faturamento real observado é de −0,003.
3. **Anomalia de concentração em Vendas:** 40,6% dos registros de vendas estão associados a um único identificador de cliente, indicando possível uso de cadastro genérico no checkout.
4. **Descompasso de custos em Estoque:** o custo unitário cadastral em Estoque diverge do custo médio ponderado realizado em Vendas. O motor analítico adotou o custo realizado de Vendas para evitar distorções de valuation.
5. **Temporalidade de Estoque:** a base de estoque é uma posição estática (snapshot) sem carimbo de data. As métricas de giro foram calibradas contra a janela temporal de Vendas (391 dias).
6. **Descompasso em Atendimento:** 65,4% dos chamados de suporte citam números de pedidos ausentes no extrato de Vendas, indicando janelas temporais desacopladas.
7. **Inelasticidade de Descontos:** o teste within-SKU demonstra que conceder descontos superiores a 20% não gera elevação no volume unitário vendido (−0,026 un. por pedido), erodindo a margem de 58% para 39%.

## Memória do cenário-base

### Estoque e liquidação

A simulação combina saldo disponível de Estoque com preço, custo, frete e devoluções históricos de Vendas. O cenário central gera R$ 4,14M de receita estimada pós-devoluções:
- Unidades elegíveis descontinuadas com saldo: 65.052 unidades (206 SKUs, totalizando R$ 6,1M de custo histórico).
- Sell-through simulado: 50% (32.526 unidades).
- Preço com 30% de desconto: R$ 4,86M de receita bruta.
- Dedução de devoluções históricas por categoria: −R$ 720 mil.
- Receita líquida ajustada: R$ 4,14M.
- Custo ponderado histórico: R$ 3,03M (+ R$ 143 mil de frete).
- Margem de contribuição gerada: R$ 969 mil (23,4%).

### CX e Atendimento N1

- Custo endereçável no período (391 dias): R$ 159.660 (rastreio) + R$ 78.888 (dúvidas técnicas) = R$ 238.548.
- Economia anual estimada no cenário-base: R$ 55.724/ano (captura conservadora de 80% em rastreio proativo e 50% em triagem N1).

### Retorno consolidado

- Benefício anual recorrente: R$ 1,80M (recuperação de margem) + R$ 55,7 mil (CX) = R$ 1,86M/ano.
- Investimento total no primeiro ano: R$ 350 mil.
- Resultado econômico líquido no primeiro ano: R$ 1,51M.
- ROI líquido no primeiro ano: 4,3x o capital investido.
- Payback estimado do investimento: 2,3 meses.

## Limitações consideradas

- Estoque é uma posição estática sem data de referência.
- Marketing não possui atribuição confiável aos pedidos de Vendas.
- O custo cadastral de Estoque diverge do custo histórico de Vendas.
- Os impactos financeiros em descontos e CX são projeções a validar no ciclo de 90 dias.

## Consultas SQL de referência

<details>
<summary><strong>1. KPIs consolidados de vendas e margem</strong> — Calcula faturamento bruto, receita líquida, margem de contribuição, pedidos, ticket médio e taxa de devolução.</summary>

```sql
SELECT 
    COALESCE(SUM(receita_bruta), 0) AS bruta,
    COALESCE(SUM(receita_liquida), 0) AS liquida,
    COALESCE(SUM(margem_calculada), 0) AS margem,
    COALESCE(COUNT(order_id), 0) AS total_pedidos,
    COALESCE(AVG(receita_liquida), 0) AS ticket_medio,
    COALESCE(AVG(CASE WHEN devolvido = true THEN 1.0 ELSE 0.0 END) * 100.0, 0) AS taxa_devolucao
FROM vendas
WHERE status_pagamento = 'Aprovado';
```
</details>

<br/>

<details>
<summary><strong>2. Simulação de liquidação e destravamento de estoque</strong> — Reúne preço, frete, taxa histórica de devolução e custo ponderado de Vendas para simular a liquidação de SKUs descontinuados.</summary>

```sql
WITH weighted_cost AS (
    SELECT sku_id, SUM(custo_produto) / NULLIF(SUM(quantidade), 0) AS custo_unitario_vendas
    FROM vendas
    WHERE status_pagamento = 'Aprovado' AND quantidade > 0
      AND custo_produto IS NOT NULL AND custo_produto >= 0
    GROUP BY sku_id
), period_economics AS (
    SELECT sku_id,
           SUM(receita_liquida) / NULLIF(SUM(quantidade), 0) AS preco_liquido_unitario,
           SUM(custo_frete) / NULLIF(SUM(quantidade), 0) AS frete_unitario
    FROM vendas
    WHERE status_pagamento = 'Aprovado'
      AND quantidade > 0 AND receita_liquida IS NOT NULL AND receita_liquida > 0
    GROUP BY sku_id
), category_returns AS (
    SELECT categoria,
           SUM(CASE WHEN devolvido THEN quantidade ELSE 0 END) / NULLIF(SUM(quantidade), 0) AS taxa_devolucao_categoria
    FROM vendas
    WHERE status_pagamento = 'Aprovado'
      AND quantidade > 0
    GROUP BY categoria
)
SELECT e.sku_id, e.nome_produto, e.categoria, e.estoque_disponivel,
       c.custo_unitario_vendas, p.preco_liquido_unitario, p.frete_unitario,
       r.taxa_devolucao_categoria
FROM estoque e
LEFT JOIN weighted_cost c USING (sku_id)
LEFT JOIN period_economics p USING (sku_id)
LEFT JOIN category_returns r ON r.categoria = e.categoria
WHERE e.is_descontinuado AND e.estoque_disponivel > 0
ORDER BY e.sku_id;
```
</details>

<br/>

<details>
<summary><strong>3. Causas-raiz e potencial de automação no atendimento</strong> — Mensura volume de chamados por categoria, CSAT médio, tempo de resposta/resolução e custos evitáveis por automação N1.</summary>

```sql
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
GROUP BY categoria_problema, is_automatizavel
ORDER BY total_tickets DESC;
```
</details>

<br/>

<details>
<summary><strong>4. Integridade relacional e auditoria cruzada de bases</strong> — Executa checagens de cobertura temporal, vínculo transacional, pedidos órfãos e reconciliação entre tabelas.</summary>

```sql
-- Cobertura temporal e volume por base
SELECT 'vendas' AS tabela, COUNT(*) AS registros, MIN(data_pedido) AS data_min, MAX(data_pedido) AS data_max FROM vendas
UNION ALL SELECT 'marketing', COUNT(*), MIN(data_inicio), MAX(data_fim) FROM marketing
UNION ALL SELECT 'estoque', COUNT(*), MIN(data_ultima_entrada), MAX(data_ultima_entrada) FROM estoque
UNION ALL SELECT 'clientes', COUNT(*), MIN(data_cadastro), MAX(data_cadastro) FROM clientes
UNION ALL SELECT 'atendimento', COUNT(*), MIN(data_abertura), MAX(data_abertura) FROM atendimento;

-- Vínculo Clientes x Vendas
SELECT
    COUNT(DISTINCT v.customer_id) AS clientes_com_venda,
    SUM(CASE WHEN v.data_pedido < c.data_cadastro THEN 1 ELSE 0 END) AS pedidos_antes_cadastro
FROM vendas v
LEFT JOIN clientes c USING (customer_id);

-- Tickets citando pedidos ausentes/presentes em Vendas
SELECT
    COUNT(DISTINCT a.order_id) AS pedidos_citados,
    COUNT(DISTINCT CASE WHEN v.order_id IS NULL THEN a.order_id END) AS pedidos_sem_venda,
    COUNT(DISTINCT CASE WHEN v.order_id IS NOT NULL THEN a.order_id END) AS pedidos_com_venda
FROM atendimento a
LEFT JOIN vendas v USING (order_id);
```
</details>

