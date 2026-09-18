# Auditoria de dados e memória de cálculo
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
| Estoque | 207 SKUs descontinuados com saldo | Quantidade disponível de Estoque; valores financeiros valorados por Vendas. |
| Liquidação | R$ 4,14M de receita pós-devoluções | 50% de sell-through, 30% de desconto e devolução de 14,88%. |
| Descontos | R$ 1,80M/ano de margem potencial | Recuperação estimada de 50% dos R$ 3,6M concedidos acima de 20%. |
| Atendimento | R$ 238,5 mil de custo endereçável no período | Rastreio e dúvidas técnicas representam 44,9% dos tickets. |

## Contrato de dados: inconsistências relacionais identificadas

A auditoria cruzada identificou 7 divergências estruturais entre as tabelas fornecidas no Data Room. Essas divergências explicam por que certas análises não devem ser utilizadas para tomadas de decisão causais antes de saneamento cadastral:

1. **Marketing versus Vendas (Atribuição):** as campanhas declaram 38,2 milhões de conversões virtuais em 2023, enquanto o ERP registra 26,5 mil pedidos em 2023. As transações não contêm `campaign_id` ou parâmetros UTM, inviabilizando o cálculo de ROAS causal por canal.
2. **CRM versus Vendas (Cobertura de clientes):** apenas 346 dos 15.000 clientes cadastrados aparecem no histórico transacional de Vendas. A correlação entre o LTV informado no CRM e o faturamento real observado é de −0,003.
3. **Anomalia de concentração em Vendas:** 40,6% dos registros de vendas estão associados a um único identificador de cliente, indicando possível uso de cadastro genérico no checkout.
4. **Descompasso de custos em Estoque:** o custo unitário cadastral em Estoque diverge do custo médio ponderado realizado em Vendas. O motor analítico adotou o custo realizado de Vendas para evitar distorções de valuation.
5. **Temporalidade de Estoque:** a base de estoque é uma posição estática (snapshot) sem carimbo de data. As métricas de giro foram calibradas contra a janela temporal de Vendas (391 dias).
6. **Descompasso em Atendimento:** 65,4% dos chamados de suporte citam números de pedidos ausentes no extrato de Vendas, indicando janelas temporais desacopladas.
7. **Inelasticidade de Descontos:** o teste within-SKU demonstra que conceder descontos superiores a 20% não gera elevação no volume unitário vendido (−0,026 un. por pedido), erodindo a margem de 58% para 39%.

## Memória do cenário-base

### Estoque e liquidação

A simulação combina saldo disponível de Estoque com preço, custo, frete e devoluções históricos de Vendas. O cenário central gera R$ 4,14M de receita estimada pós-devoluções:
- Unidades elegíveis descontinuadas com saldo: 65.052 unidades (206 SKUs).
- Sell-through simulado: 50% (32.526 unidades).
- Preço com 30% de desconto: R$ 4,86M de receita bruta.
- Dedução de devoluções históricas por categoria: −R$ 720 mil.
- Receita líquida ajustada: R$ 4,14M.
- Custo ponderado histórico: R$ 3,03M (+ R$ 143 mil de frete).
- Margem de contribuição gerada: R$ 969 mil (23,4%).

### CX e Atendimento N1

- Custo endereçável no período (391 dias): R$ 159.660 (rastreio) + R$ 78.888 (dúvidas técnicas) = R$ 238.548.
- Custo endereçável anualizado: R$ 238.548 ÷ 391 × 365 = R$ 222.684 (ou R$ 79.516/ano em base contábil de 3 anos).
- Economia anual estimada no cenário-base: R$ 55.724/ano (captura de 80% em rastreio proativo e 50% em triagem N1).

### Retorno consolidado

- Benefício anual recorrente: R$ 1,80M (recuperação de margem) + R$ 55,7 mil (CX) = R$ 1,86M/ano.
- Investimento total no primeiro ano: R$ 350 mil.
- Resultado econômico líquido no primeiro ano: R$ 1,51M.
- ROI líquido no primeiro ano: 4,3x o capital investido.
- Payback estimado do investimento: 2,3 meses.

## Limitações consideradas

- Estoque é uma posição estática sem data de referência.
- Marketing não possui atribuição confiável aos pedidos do ERP.
- O custo cadastral de Estoque diverge do custo histórico de Vendas.
- Os impactos financeiros em descontos e CX são projeções a validar no ciclo de 90 dias.

## Consultas de referência

- `src/queries/visao_geral/kpis_consolidados.sql`
- `src/queries/agent/liquidation.sql`
- `src/queries/atendimento/causas_raiz_e_automacao.sql`
- `src/queries/auditoria/integridade_bases.sql`
- Relatórios exploratórios em `docs/profiling/` (HTML por base de dados).
