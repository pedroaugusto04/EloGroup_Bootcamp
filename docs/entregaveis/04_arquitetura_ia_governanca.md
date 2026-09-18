# Arquitetura do copiloto de IA, segurança e governança
**Bootcamp EloGroup 2026 · Grupo 14**  
**Autores:** Pedro Augusto e Pedro Lobo  

---

## 1. Visão geral da arquitetura

O copiloto separa o cálculo matemático da redação do texto.

Modelos de linguagem não devem calcular margens financeiras, giro de estoque ou valuation, pois são probabilísticos e sujeitos a variações. Todas as métricas numéricas são processadas diretamente no banco de dados analítico e validadas por código determinístico antes de chegarem ao modelo.

A inteligência artificial atua na etapa final: ela recebe os números auditados, contextualiza o cenário de negócio e redige o parecer executivo para a diretoria.

### Estrutura em quatro camadas

1. **Camada de dados:** arquivos de dados processados em memória colunar de alto desempenho para respostas em milissegundos.
2. **Motor determinístico:** rotinas analíticas em Python que calculam giro, capital imobilizado, risco de ruptura e impacto de devoluções.
3. **Orquestração e inteligência:** fluxo estruturado que divide a análise em etapas sequenciais (estoque, demanda, devoluções e recomendações), utilizando o modelo de linguagem apenas para sintetizar o diagnóstico.
4. **Interface e entrega:** painel web executivo para consulta interativa e despachos programados de relatórios por e-mail.

---

## 2. Componentes e salvaguardas

### Motor de cálculo e validação
O cálculo de capital imobilizado utiliza o custo médio histórico apurado nas vendas, evitando distorções presentes no cadastro estático de estoque. Os itens descontinuados e os produtos em risco de ruptura são classificados por categoria e prazo de reposição antes de qualquer recomendação.

### Fluxo de análise estruturado
A análise segue um roteiro fixo dividido em quatro passos: diagnóstico de saldos, cruzamento com histórico de vendas, verificação de devoluções e simulação de liquidação. O modelo não cria etapas por conta própria, garantindo que o escopo permaneça auditável e previsível.

### Salvaguardas numéricas
Se a resposta gerada contiver qualquer valor numérico divergente dos dados apurados pelas consultas, o texto é automaticamente bloqueado e descartado. Em caso de lentidão ou falha na API de inteligência artificial, o sistema exibe o parecer factual direto dos cálculos, mantendo a operação contínua.

### Rotina de relatórios e alertas
O sistema executa análises periódicas de forma autônoma. Ao identificar necessidades críticas de reposição ou lotes parados de descontinuados, compila o parecer e despacha um resumo executivo diretamente para o e-mail dos gestores responsáveis.

---

## 3. Governança e controle de riscos

| Risco | Descrição | Controle implementado | Gatilho de ação |
| :--- | :--- | :--- | :--- |
| Invenção de valores | Citação de métricas não comprovadas nos relatórios. | Validação estrita de todos os números gerados antes da exibição. | Bloqueio imediato da resposta em caso de divergência numérica. |
| Privacidade | Exposição de dados de clientes em prompts ou logs. | O sistema opera somente em nível agregado de SKU e categoria de produto. | Dados individuais de clientes não são enviados ao modelo. |
| Variação de comportamento | Mudança no padrão de consumo distorcendo o cálculo de giro. | Recálculo contínuo com janelas temporais configuráveis. | Alerta quando a média de vendas de um produto oscilar mais de 20%. |
| Adoção e autonomia | Execução indevida de compras pelo sistema. | Nenhuma ordem de compra ou corte de preço é executado sem aprovação humana. | Exceções ao teto de desconto exigem liberação manual da diretoria. |

---

## 4. Consultas SQL de referência

<details>
<summary><strong>1. Métricas financeiras e de vendas macro (Pedidos Aprovados)</strong> — Consolida faturamento bruto, receita líquida, margem de contribuição, pedidos e taxa de devolução.</summary>

```sql
SELECT 
    COALESCE(SUM(receita_bruta), 0) AS gross_revenue,
    COALESCE(SUM(receita_liquida), 0) AS net_revenue,
    COALESCE(SUM(margem_calculada), 0) AS contribution_margin,
    COALESCE(COUNT(order_id), 0) AS total_orders,
    COALESCE(AVG(receita_liquida), 0) AS average_ticket,
    COALESCE(AVG(CASE WHEN devolvido = true THEN 1.0 ELSE 0.0 END) * 100.0, 0) AS return_rate_pct
FROM vendas
WHERE status_pagamento = 'Aprovado';
```
</details>

<br/>

<details>
<summary><strong>2. Descontinuados e capital imobilizado</strong> — Cruza saldo físico e disponível de descontinuados com o custo unitário histórico apurado em vendas.</summary>

```sql
WITH weighted_cost AS (
    SELECT sku_id, SUM(custo_produto) / NULLIF(SUM(quantidade), 0) AS custo_unitario_vendas
    FROM vendas
    WHERE status_pagamento = 'Aprovado' AND quantidade > 0
      AND custo_produto IS NOT NULL AND custo_produto >= 0
    GROUP BY sku_id
)
SELECT e.sku_id, e.nome_produto, e.categoria, e.fornecedor_id,
       e.estoque_fisico, e.estoque_reservado, e.estoque_disponivel,
       c.custo_unitario_vendas,
       e.estoque_fisico * c.custo_unitario_vendas AS capital_fisico,
       e.estoque_disponivel * c.custo_unitario_vendas AS capital_disponivel
FROM estoque e
LEFT JOIN weighted_cost c USING (sku_id)
WHERE e.is_descontinuado
ORDER BY capital_disponivel DESC NULLS LAST;
```
</details>

<br/>

<details>
<summary><strong>3. SKUs críticos abaixo do ponto de pedido</strong> — Identifica produtos ativos com saldo disponível inferior à cobertura mínima do prazo de entrega do fornecedor.</summary>

```sql
WITH sales_pace AS (
    SELECT sku_id, 
           SUM(quantidade) / 391.0 AS media_diaria_vendas
    FROM vendas
    WHERE status_pagamento = 'Aprovado' AND quantidade > 0
    GROUP BY sku_id
)
SELECT e.sku_id, e.nome_produto, e.categoria, e.estoque_disponivel,
       e.lead_time_reposicao, e.ponto_pedido,
       COALESCE(s.media_diaria_vendas, 0) AS demanda_diaria,
       ROUND(COALESCE(s.media_diaria_vendas, 0) * e.lead_time_reposicao, 1) AS ponto_de_pedido_calculado
FROM estoque e
LEFT JOIN sales_pace s USING (sku_id)
WHERE NOT e.is_descontinuado
  AND e.estoque_disponivel < (COALESCE(s.media_diaria_vendas, 0) * e.lead_time_reposicao)
ORDER BY e.estoque_disponivel ASC;
```
</details>

<br/>

<details>
<summary><strong>4. Causas-raiz de atendimento e potencial de automação</strong> — Mensura o volume de chamados por motivo para dimensionar a redução em rastreio e suporte N1.</summary>

```sql
SELECT categoria_problema,
       COUNT(*) AS total_tickets,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentual_volume,
       ROUND(AVG(nota_csat), 2) AS csat_medio,
       ROUND(AVG(tempo_resolucao_horas), 1) AS sla_medio_horas
FROM atendimento
GROUP BY categoria_problema
ORDER BY total_tickets DESC;
```
</details>

<br/>

<details>
<summary><strong>5. Conciliação de mídia vs pedidos reais</strong> — Compara as conversões e receitas declaradas nas plataformas de anúncios com o faturamento do ERP.</summary>

```sql
WITH mkt AS (
    SELECT SUM(custo_total) AS total_investido_mkt,
           SUM(conversoes) AS total_conversoes_declaradas,
           SUM(receita_gerada) AS total_receita_declarada_mkt
    FROM marketing
),
erp AS (
    SELECT COUNT(DISTINCT order_id) AS total_pedidos_faturados_erp,
           SUM(receita_liquida) AS total_receita_liquida_erp
    FROM vendas
    WHERE status_pagamento = 'Aprovado'
)
SELECT mkt.*, erp.*
FROM mkt CROSS JOIN erp;
```
</details>
