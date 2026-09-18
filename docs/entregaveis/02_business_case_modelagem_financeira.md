# Business case: soluções priorizadas
**Bootcamp EloGroup 2026 · Grupo 14**  
**Autores:** Pedro Augusto e Pedro Lobo

---

## Proposta

Implementar, em 90 dias, três frentes conectadas ao diagnóstico:

1. **Predictive Stock Advisor:** prioriza liquidação de descontinuados e ações de reposição.
2. **Margin Recovery Advisor:** recomenda o teto de desconto por SKU para proteger margem.
3. **Rastreio e Atendimento N1:** reduz consultas operacionais com comunicação proativa e autoatendimento.

## Impacto estimado no cenário-base

| Frente | Impacto | Premissa principal | Critério de acompanhamento |
| --- | ---: | --- | --- |
| Estoque | R$ 4,14M em receita estimada pós-devoluções | 50% de sell-through dos descontinuados em 90 dias, desconto médio de 30% e ajuste de 14,88% para devoluções. | Receita realizada e sell-through do lote. |
| Descontos | R$ 1,80M/ano de margem potencial | Redução de descontos acima do teto recomendado; o teste within-SKU indicou volume estável mesmo com desconto agressivo. | Margem cedida acima do teto e volume diário. |
| CX e N1 | R$ 55,7 mil/ano de economia estimada | Captura de 80% do custo de rastreio e 50% do custo de dúvidas técnicas. | Volume de tickets de rastreio, FCR e CSAT. |

## Retorno econômico

A liquidação gera entrada de caixa. O cálculo de retorno econômico considera a margem recuperada e a economia operacional anualizadas.

| Indicador | Cenário-base |
| --- | ---: |
| Margem recuperada e economia anual | R$ 1,86M |
| Investimento do projeto (ano 1) | R$ 350 mil |
| Resultado econômico líquido (ano 1) | R$ 1,51M |
| ROI líquido (ano 1) | 4,3x |
| Payback estimado (run-rate) | 2,3 meses |

O investimento considera R$ 250 mil para a squad de 90 dias e R$ 100 mil para infraestrutura, APIs, mensageria e gestão de mudança no primeiro ano.

## Premissas e decisão

- **Estoque:** 50% de sell-through dos descontinuados em 90 dias, desconto médio de 30% e ajuste de 14,88% para devoluções.
- **Base de cálculo:** saldo disponível de Estoque; preço, custo, frete e devoluções históricos de Vendas.
- **Descontos:** redução de descontos acima do teto recomendado, com acompanhamento de margem cedida e volume diário.
- **CX e N1:** R$ 238,5 mil de custo endereçável entre 2023 e 2025; a captura de 80% em rastreio e 50% em dúvidas técnicas equivale a R$ 55,7 mil/ano de economia.
- **ROI:** considera margem recuperada em descontos e economia em CX; a receita estimada da liquidação é apresentada separadamente.

Decisão solicitada: aprovar o ciclo de 90 dias, com revisão dos indicadores nos dias 30, 60 e 90 antes de qualquer ampliação de escopo.
