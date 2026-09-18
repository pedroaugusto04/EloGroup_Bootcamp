# Racional metodológico e desenvolvimento
**Bootcamp EloGroup 2026 · Grupo 14**  
**Autores:** Pedro Augusto e Pedro Lobo

---

## Objetivo central

Como podemos usar dados e inteligência artificial para melhorar a rentabilidade, a eficiência operacional e a qualidade da tomada de decisão nos próximos 90 dias?

---

## 1. Análise Exploratória e Higienização de Dados

A etapa inicial consistiu na análise exploratória das cinco bases brutas fornecidas, com o objetivo de mapear a estrutura relacional, identificar valores ausentes, avaliar distribuições e detectar anomalias transacionais.

* **Profiling Automatizado:** Execução de rotinas de profiling analítico para todas as tabelas, mapeando tipos primitivos, cardinalidade, proporção de nulos e estatísticas univariadas.
* **Saneamento em Vendas:** Identificação e descarte de registro com identificador inválido (`ORD-072219`), caracterizado pela ausência total de colunas financeiras e transacionais.
* **Saneamento em Atendimento:** Identificação e descarte de registro com identificador corrompido (`TKT`), sem informações cadastrais complementares.

---

## 2. Engenharia de dados e pré-processamento

Todas as transformações foram padronizadas em rotinas determinísticas de pré-processamento, com persistência em formato colunar Parquet para garantir respostas analíticas em milissegundos.

### Padronização geral
* Aplicação de rotina de limpeza de texto em todas as colunas de identificadores e campos descritivos para eliminar espaços em branco nas extremidades e inconsistências de codificação.

### Tabela de Vendas
* **Tipagem e Sanitização:** Conversão do carimbo temporal do pedido para formato de data e hora, e conversão da marcação de devolução para booleano.
* **Tratamento Numérico:** Coerção com preenchimento neutro para quantidade vendida, preço unitário, receita bruta, desconto em reais, receita líquida, custo do produto, frete, margem calculada e tempo de entrega.
* **Métricas Financeiras Nominais:** Cálculo da margem nominal (receita líquida menos custos diretos), percentual de margem, percentual de desconto concedido e agregações de ano e mês.
* **Métricas de Efetividade e Estorno:**
  * Indicador de aprovação de pagamento.
  * Indicador de venda efetiva (aprovada e não devolvida).
  * Receita líquida retida pós-estorno de devoluções.
  * Margem efetiva real (deduzindo a receita estornada e contabilizando o prejuízo do frete perdido).
  * Volume total de receita devolvida e frete consumido em cancelamentos.

### Tabela de Marketing
* **Tipagem:** Conversão das datas de início e término das campanhas.
* **Métricas Operacionais:** Coerção de investimento, impressões, cliques, conversões virtuais declaradas, receita declarada e custos de aquisição.
* **Indicadores Calculados:** Taxa de cliques (CTR), taxa de conversão virtual, custo por clique (CPC), margem bruta declarada de mídia, duração da veiculação e indicador de status ativo.

### Tabela de Estoque
* **Tipagem:** Conversão da data da última entrada física.
* **Métricas de Capacidade:** Coerção de lead time do fornecedor, custo unitário cadastral, preço sugerido, estoque físico, estoque reservado, saldo disponível, ponto de pedido, validade e cubagem.
* **Classificação de Ruptura e Giro:**
  * Ruptura real: 99 SKUs com saldo disponível zerado.
  * Nível crítico: 701 SKUs ativos com saldo disponível abaixo ou igual ao ponto de pedido.
  * Necessidade de reposição: 800 SKUs em situação de atenção (soma dos zerados e críticos).
  * Capital imobilizado em descontinuados: valoração dos 207 SKUs fora de linha.

### Tabela de Clientes
* **Tipagem:** Conversão das datas de cadastro e nascimento, e conversão da opção de recebimento de newsletter.
* **Engenharia de Atributos:** Coerção de renda estimada, total de pedidos histórico e LTV acumulado.
* **Métricas Calculadas:** Idade do cliente referenciada ao ano do case (2026), ticket médio histórico e tempo de relacionamento em dias.

### Tabela de Atendimento
* **Tipagem:** Conversão dos registros de abertura e encerramento dos chamados.
* **Métricas de SLA e Qualidade:** Coerção das notas de satisfação (CSAT), tempo até a primeira resposta em minutos e custo operacional de cada chamado.
* **Classificação Operacional:** Tempo total de resolução em horas, identificador de CSAT crítico (notas 1 e 2), identificador de chamados passíveis de automação (consultas de rastreamento e dúvidas técnicas) e sinalizador de SLA estourado.

---

## 3. Análise de dispersão e detecção de anomalias

A detecção de dados discrepantes utilizou o método de Tukey com base no Intervalo Interquartil (critério de 1,5 × IQR, com limites derivados do primeiro e terceiro quartis):

* **Vendas:**
  * Descontos em reais: 3.609 pedidos (13,0%) com descontos atípicos (acima de R$ 164,26), alcançando máxima de R$ 1.784,98.
  * Margem calculada: 491 pedidos com margem estritamente negativa (mínimo de −R$ 49,27), onde a concessão agressiva de desconto somada ao frete superou o valor dos produtos.
  * Receita bruta: 827 pedidos (2,98%) com ticket atípico acima de R$ 2.074,89 (máximo de R$ 5.004,90).
* **Atendimento:**
  * Tempo de resolução: 8.798 chamados (24,55%) acima de 190,5 horas, atingindo distorção de 26.294 horas (~3 anos) em virtude do preenchimento padrão da data de 31/12/2025 para tickets em aberto.
  * Tempo de primeira resposta: 2.385 chamados (6,65%) acima de 7,8 horas, com pico de 24 horas.
  * Satisfação (CSAT): 2.627 chamados (7,33%) com nota mínima 1,0.
* **Estoque:**
  * Valor total de estoque: 201 SKUs (4,02%) acima de R$ 186.594, com SKU isolado imobilizando R$ 448.196,21.
  * Desbalanceamento físico: 99 SKUs zerados em contraposição a 140 SKUs com excesso de cobertura (acima de 790 unidades, alcançando 1.183 unidades).
* **Clientes:**
  * LTV cadastral: 1.253 clientes (8,35%) com valor acumulado declarado acima de R$ 25.506 (pico em R$ 118.316,70).
  * Pedidos acumulados: 998 clientes (6,65%) com mais de 55 compras cadastradas no CRM.
* **Marketing:**
  * Custo por aquisição (CAC): 317 campanhas (9,06%) com CAC acima de R$ 10,24 (pico de R$ 82,33).
  * Retorno sobre investimento (ROAS declarado): 229 campanhas (6,54%) com retorno aparente acima de 7,87x nas plataformas.

---

## 4. Diagnóstico e descobertas por tabela

### Faturamento e margem
* Sazonalidade observada: picos de receita concentrados em datas comerciais e promocionais do varejo (março, maio, novembro e dezembro).
* Margem nominal saudável: a margem média bruta situa-se em torno de 54,2% a 54,9% do faturamento.
* Impacto severo de devoluções: 14,88% dos pedidos aprovados foram devolvidos, provocando estorno de R$ 2,50 milhões em receita e gerando prejuízo direto de R$ 45,1 mil com fretes perdidos, reduzindo o resultado retido para R$ 7,66M.

### Marketing e mídia paga
* Retorno aparente: relatórios de plataformas de anúncios indicam alto desempenho, com destaque para influenciadores reportando ROAS aparente de 7,75x e baixo CAC.
* Visão no ERP transacional: o canal de influenciadores representa volume financeiro menor (R$ 1,81M líquido), porém entrega o maior ticket médio (R$ 901,91) e margem retida saudável de 52,3%.

### Estoque e abastecimento
* Capital imobilizado em descontinuados: mais de R$ 6,1 milhões (a custo de Vendas) e R$ 14,7 milhões (a custo cadastral de Estoque) retidos em 207 SKUs descontinuados.
* Risco iminente de ruptura: 99 SKUs com estoque zero (sendo 96 deles na categoria Beleza) e 701 SKUs ativos operando abaixo da cobertura do lead time do fornecedor.

### Base de clientes e CRM
* Concentração no topo: os segmentos de clientes de maior fidelidade representam parcela substancial do faturamento acumulado no CRM.
* Risco de inatividade: parcela expressiva da base cadastrada encontra-se em faixas de risco ou inatividade.

### Suporte e atendimento
* Canal prioritário: WhatsApp concentra a maioria dos chamados de entrada, seguido por e-mail e chatbot.
* Demanda operacional evitável: 30,0% dos chamados são dúvidas de localização de pedido (R$ 159,7 mil de custo no período), enquanto 14,8% referem-se a dúvidas técnicas de produto (R$ 78,9 mil).

---

## 5. Auditoria de integridade relacional

A avaliação cruzada entre as cinco tabelas demonstrou que, apesar da consistência interna de cada arquivo, existem divergências estruturais que inviabilizam cruzamentos ingênuos:

1. **Descompasso Temporal:** Vendas cobre 391 dias (2023 até 26/01/2024), enquanto Marketing, Atendimento e Clientes contêm registros distribuídos entre 2023 e 2025.
2. **Cobertura Cadastral de Clientes:** Apenas 346 dos 15.000 clientes da base de CRM aparecem nas transações de Vendas (2,3%).
3. **Concentração no Checkout:** Um único identificador de cliente concentra 40,6% de todas as transações de Vendas (11.282 compras) e 40,0% dos chamados de suporte, caracterizando uso de cadastro padrão/genérico no ponto de venda.
4. **Desconexão de LTV:** O LTV acumulado informado no cadastro de clientes não reconcilia com o faturamento apurado em Vendas (correlação observada de −0,003).
5. **Datas Anacrônicas:** 30,5% dos pedidos em Vendas possuem data anterior à data de cadastro do respectivo cliente no CRM.
6. **Mídia versus Pedidos Faturados:** A base de Marketing reporta 38,2 milhões de conversões virtuais em 2023, enquanto o ERP registra 26,5 mil pedidos faturados no mesmo ano. Os pedidos não possuem vínculo direto com os anúncios, impossibilitando a atribuição causal de receita.
7. **Chamados Órfãos em Atendimento:** 65,4% dos chamados de suporte citam pedidos que não constam no extrato de vendas fornecido.
8. **Divergência de Custos:** A correlação entre o custo unitário histórico de Vendas e o custo unitário cadastrado em Estoque é próxima de zero (0,008). Por conservadorismo, adotou-se o custo realizado de Vendas.

---

## 6. Diagnóstico das hipóteses e módulos de solução

### Conclusão das hipóteses avaliadas

* **Hipótese 1 (Margem e Rentabilidade):** A margem nominal de contribuição permaneceu estável (54,2% a 54,9%). O problema não é queda de margem bruta, mas a queima de valor em concessão de descontos excessivos e custos de suporte evitáveis.
* **Hipótese 2 (Elasticidade de Descontos):** O teste econométrico within-SKU comprovou volume plano em 3,51 unidades por pedido, independentemente do percentual de desconto praticado. Conceder descontos acima de 20% reduziu a margem para 32% sem gerar tração de vendas.
* **Hipótese 3 (Falhas Operacionais e Devoluções):** O tempo de entrega não explica a taxa de devolução. As devoluções decorrem de falhas de qualidade e inadequação de tamanho, concentradas em itens específicos.
* **Hipótese 4 (Sintomas no Atendimento):** Sustentada. Consultas de rastreio (30,0%) e dúvidas técnicas (14,8%) representam 44,9% dos chamados e R$ 238,5 mil em custos que podem ser mitigados com mensageria proativa e triagem N1.
* **Hipótese 5 (Segmentação de Clientes):** Relevante conceitualmente, mas inviabilizada no curto prazo pela baixa cobertura cadastral (apenas 2,3% dos clientes constam no extrato de Vendas).
* **Hipótese 6 (Eficiência na Decisão de Estoque):** Sustentada. Mais de R$ 6,1M em produtos descontinuados estão imobilizados sem ação de liquidação, enquanto 701 SKUs ativos operam em risco de ruptura.

### Seleção de módulos para o plano de 90 dias

* **Módulo de Mídia (Descartado no Ciclo I):** Desacoplamento entre painéis de marketing e vendas inviabiliza otimização causal imediata. Prioridade: instrumentar o checkout antes de realocar orçamentos.
* **Módulo de Suporte e Rastreio (Selecionado como Quick Win):** Disparo de link de rastreamento por mensageria e autoatendimento com IA para dúvidas frequentes. Economia projetada de R$ 55,7 mil/ano.
* **Módulo de Estoque e Precificação Dinâmica (Solução Central):**
  * **Predictive Inventory Advisor:** Prioriza a liquidação assistida dos 206 SKUs descontinuados elegíveis (gerando R$ 4,14M de caixa imediato) e monitora a reposição dos 701 SKUs críticos.
  * **Margin Recovery Advisor:** Aplica tetos dinâmicos de desconto por SKU, protegendo R$ 1,80M/ano de margem sem impactar o volume vendido.