# Auditoria de dados e memória de cálculo
**Bootcamp EloGroup 2026 · Grupo 14**  
**Autores:** Pedro Augusto e Pedro Lobo

---

## Objetivo

Registrar os critérios e cálculos que sustentam o diagnóstico e o business case.

## Validações principais

| Tema | Valor validado | Critério |
| --- | ---: | --- |
| Vendas | R$ 16,67M de receita líquida | Pedidos aprovados no período disponível. |
| Margem | 54,2% a 54,9% | Estabilidade mensal da margem de contribuição. |
| Estoque | 207 SKUs descontinuados com saldo | Quantidade disponível de Estoque; valores financeiros de Vendas. |
| Liquidação | R$ 4,14M de receita pós-devoluções | 50% de sell-through, 30% de desconto e devolução de 14,88%. |
| Descontos | R$ 1,80M/ano de margem potencial | Recuperação estimada de 50% dos R$ 3,6M concedidos acima de 20%. |
| Atendimento | R$ 238,5 mil de custo endereçável entre 2023 e 2025 | Rastreio e dúvidas técnicas representam 44,9% dos tickets. |

## Memória do cenário-base

### Estoque

A simulação combina saldo disponível de Estoque com preço, custo, frete e devoluções históricos de Vendas. O cenário central gera R$ 4,14M de receita estimada pós-devoluções. Esse valor é apresentado separadamente do ROI.

### CX e N1

- Custo endereçável no período: R$ 159.660 + R$ 78.888 = R$ 238.548
- Custo endereçável anual: R$ 238.548 ÷ 3 = R$ 79.516
- Economia anual estimada: (R$ 159.660 × 80% + R$ 78.888 × 50%) ÷ 3 = R$ 55.724

### Retorno

- Benefício anual: R$ 1,80M + R$ 55,7 mil = R$ 1,86M
- Investimento no primeiro ano: R$ 350 mil
- Resultado líquido: R$ 1,51M
- ROI líquido: 4,3x
- Payback: 2,3 meses

## Limitações consideradas

- Estoque é uma posição estática sem data de referência.
- Marketing não possui atribuição confiável aos pedidos do ERP.
- O custo cadastral de Estoque diverge do custo histórico de Vendas.
- Os impactos financeiros são projeções a validar no ciclo de 90 dias.

## Consultas de referência

- `src/queries/visao_geral/kpis_consolidados.sql`
- `src/queries/agent/liquidation.sql`
- `src/queries/atendimento/causas_raiz_e_automacao.sql`
- `src/queries/auditoria/integridade_bases.sql`
