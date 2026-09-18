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

## Matriz de sensibilidade da liquidação (descontinuados)

A modelagem de liquidação abrange 206 dos 207 SKUs descontinuados com saldo (1 SKU sem histórico em Vendas foi excluído por conservadorismo). Com desconto simulado de 30% sobre os preços praticados no ERP e ajuste de devoluções por categoria:

| Cenário de sell-through | Unidades liquidadas | Receita bruta | Ajuste devoluções | Receita pós-devoluções | Margem de contribuição |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Conservador (25%) | 16.263 un. | R$ 2,43M | −R$ 360 mil | **R$ 2,07M** | R$ 484 mil (23,4%) |
| Central (50%) | 32.526 un. | R$ 4,86M | −R$ 720 mil | **R$ 4,14M** | R$ 969 mil (23,4%) |
| Otimista (75%) | 48.789 un. | R$ 7,29M | −R$ 1,08M | **R$ 6,21M** | R$ 1,45M (23,4%) |
| Liquidação total (100%) | 65.052 un. | R$ 9,72M | −R$ 1,44M | **R$ 8,28M** | R$ 1,94M (23,4%) |

*A receita de liquidação representa destravamento de capital de giro e reforço imediato de caixa; não é somada diretamente ao retorno econômico anualizado recorrente.*

## Retorno econômico recorrente

O cálculo de retorno econômico considera a margem recuperada em descontos e a economia operacional anualizadas:

| Indicador | Cenário conservador | Cenário-base |
| :--- | ---: | ---: |
| Margem recuperada de descontos | R$ 900 mil/ano (captura de 25%) | R$ 1,80M/ano (captura de 50%) |
| Economia operacional em CX | R$ 35,0 mil/ano | R$ 55,7 mil/ano |
| **Benefício anual recorrente** | **R$ 935 mil** | **R$ 1,86M** |
| Investimento total do projeto (ano 1) | R$ 350 mil | R$ 350 mil |
| **Resultado econômico líquido (ano 1)** | **R$ 585 mil** | **R$ 1,51M** |
| **ROI líquido no primeiro ano** | **1,7x** | **4,3x** |
| **Payback do investimento** | **4,5 meses** | **2,3 meses** |

## Composição do investimento (ano 1)

O investimento de R$ 350 mil está estruturado em:
- **Squad de projeto (90 dias):** R$ 250 mil (Tech Lead, Engenheiro de Dados/Analytics, Especialista de Negócios e CX).
- **Infraestrutura e consumo de nuvem (12 meses):** R$ 60 mil (instâncias analíticas DuckDB in-memory e API LangGraph).
- **Mensageria e WhatsApp:** R$ 20 mil (notificações proativas de rastreio aos clientes).
- **Gestão de mudança e capacitação:** R$ 20 mil (treinamento de equipes de compras e atendimento).

## Premissas e decisão

- **Estoque:** 50% de sell-through dos descontinuados em 90 dias, desconto médio de 30% e ajuste histórico de 14,88% para devoluções.
- **Base de cálculo:** saldo disponível de Estoque; preço, custo, frete e devoluções históricos de Vendas.
- **Descontos:** redução gradual de descontos acima do teto recomendado com acompanhamento diário de elasticidade volumétrica.
- **CX e N1:** R$ 238,5 mil de custo de chamados no período de 391 dias (anualizado para R$ 79,5k/ano); a captura de 80% em rastreio e 50% em dúvidas técnicas equivale a R$ 55,7 mil/ano de economia.
- **Decisão solicitada:** aprovar o ciclo de 90 dias com revisão dos indicadores nos dias 30, 60 e 90 antes de qualquer ampliação de escopo.
