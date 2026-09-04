--- ETAPAS REALIZADAS DURANTE A ANÁLISE ---

OBJETIVO CENTRAL: Como podemos usar dados e IA para melhorar rentabilidade, eficiência operacional e qualidade da tomada de decisão nos próximos 90 dias?

1. Análise Exploratória e Limpeza de Dados

* Análise dos dados de forma exploratória, visando entender a estrutura e qualidade dos dados
  (nessa etapa, o foco foi identificar valores nulos, dados faltantes, valores atípicos, etc)

* Utilizamos ydata-profiling para gerar relatórios de profiling dos dados para cada base

* Vendas: Foi identificada uma linha com order_id 'ORD-072219' e com colunas financeiras/transacionais incompletas. Optamos por remover.
* Atendimento: Foi identificada uma linha com ticket_id 'TKT' e o restante dos dados incompletos. Optamos por remover.

2. Pré-Processamento

* **Padronização Geral de Strings**: Aplicado 'strip' em todas as colunas de texto/identificadores de todas as bases para eliminar espaços nas extremidades e evitar inconsistências.

* **Vendas**:
  * **Tipagem & Sanitização**: Conversão de `data_pedido` para datetime e parsing de `devolvido` para booleano.
  * **Numéricas**: Coerção e preenchimento (0.0) de `quantidade`, `preco_unitario`, `receita_bruta`, `desconto_reais`, `receita_liquida`, `custo_produto`, `custo_frete`, `margem_contribuicao` e `tempo_entrega_real`.
  * **Métricas Nominais**: `margem_calculada` (receita líquida - custos), `margem_pct`, `desconto_pct`, além de campos temporais (`ano_mes`, `ano`).
  * **Métricas de Efetividade e Devolução**: 
    * `is_aprovado` (status_pagamento == 'Aprovado')
    * `is_venda_efetiva` (aprovado e não devolvido)
    * `receita_liquida_efetiva` (receita retida após estornos)
    * `margem_efetiva` (margem real deduzindo estorno e considerando frete perdido)
    * `receita_devolvida` (volume financeiro estornado)
    * `custo_frete_perdido` (prejuízo direto com frete de pedidos devolvidos)

* **Marketing**:
  * **Tipagem**: Conversão de datas de campanha (`data_inicio`, `data_fim`) para datetime.
  * **Numéricas**: Coerção e preenchimento de `investimento_reais`, `impressoes`, `cliques`, `conversoes`, `roas`, `receita_gerada` e `cac`.
  * **Métricas**: `ctr_pct` (cliques/impressões), `taxa_conversao_pct` (conversões/cliques), `cpc_reais` (investimento/cliques), `lucro_bruto_mkt` (receita gerada - investimento), `duracao_dias`, `cpa_calculado` e flag `is_ativa`.

* **Estoque**:
  * **Tipagem**: Conversão de `data_ultima_entrada` para datetime.
  * **Numéricas**: Coerção de volumes, custos e níveis de estoque (`lead_time_reposicao`, `custo_unitario`, `preco_venda_sugerido`, `estoque_fisico`, `estoque_reservado`, `estoque_disponivel`, `ponto_pedido`, `shelf_life_dias`, `volume_m3`).
  * **Métricas**: Flags calculadas de `is_ruptura_real` (`em_ruptura` = estoque disponível == 0 / 99 SKUs), `is_estoque_critico` (estoque disponível > 0 e <= ponto de pedido / 701 SKUs), `precisa_reposicao` (ruptura real ou estoque crítico / 800 SKUs), `margem_unitaria_sugerida`, `markup_sugerido_pct`, `valor_total_estoque`, `is_descontinuado`, `capital_travado_descontinuado` (capital imobilizado em produtos fora de linha) e `capital_em_risco_ruptura` (valor de estoque dos 701 SKUs em nível crítico).

* **Clientes**:
  * **Tipagem**: Conversão de `data_cadastro` e `data_nascimento` para datetime, e `opt_in_newsletter` para booleano.
  * **Numéricas**: Coerção de `renda_estimada`, `total_pedidos_historico` e `ltv_acumulado`.
  * **Métricas**: Cálculo da `idade` do cliente a partir do ano de referência do case (2026), `ticket_medio_historico` (LTV / pedidos) e `dias_desde_cadastro`.

* **Atendimento**:
  * **Tipagem**: Conversão de `data_abertura` e `data_fechamento` para datetime.
  * **Numéricas**: Coerção de `nota_csat`, `tempo_primeira_resposta_minutos` e `custo_operacional_ticket`.
  * **Métricas**: `tempo_resolucao_horas` (diferença entre abertura e fechamento), flag `csat_critico` (nota CSAT <= 2.0), flag `is_automatizavel` (chamados de status e dúvidas), `custo_evitavel_automacao` e `sla_resposta_estourado`.

* **Outliers e Anomalias**:
  Obs: Para isso, utilizamos o **Critério de Tukey ($1.5 \times \text{IQR}$)**, com os quantis ($Q1$, $Q3$ e $\text{IQR} = Q3 - Q1$) extraídos dos relatórios de profiling.

  * **Vendas**:
    * `desconto_reais`: 3.609 pedidos (13,0%) com descontos atípicos (acima de R$ 164,26), atingindo o pico de **R$ 1.784,98**.
    * `margem_calculada`: 491 pedidos com **margem negativa** (mínimo de -R$ 49,27), onde descontos e frete superaram o valor da mercadoria.
    * `receita_bruta`: 827 pedidos (2,98%) com valores acima de R$ 2.074,89 (máximo de R$ 5.004,90).
  * **Atendimento**:
    * `tempo_resolucao_horas`: 8.798 registros (24,55%) acima de 190,5h, atingindo **26.294h (~3 anos)**. ANOMALIA GERADA PELA DATA `31/12/2025` EM TICKETS ABERTOS.
    * `tempo_primeira_resposta_minutos`: 2.385 chamados (6,65%) acima de 468 min (~7,8h), com pico em **1.440 min (24h)**.
    * `nota_csat`: 2.627 chamados (7,33%) com nota mínima 1.0.
  * **Estoque**:
    * `valor_total_estoque`: 201 SKUs (4,02%) acima de R$ 186.594, com SKU individual imobilizando **R$ 448.196,21**.
    * `estoque_disponivel`: 99 SKUs com saldo zerado vs 140 SKUs com super-estoque (> 790 un, máx de 1.183 un).
  * **Clientes**:
    * `ltv_acumulado`: 1.253 clientes (8,35%) acima de R$ 25.506, com valor máximo de **R$ 118.316,70**.
    * `total_pedidos_historico`: 998 clientes (6,65%) com mais de 55 pedidos, com pico em **120 pedidos**.
  * **Marketing**:
    * `cac`: 317 campanhas (9,06%) com custo acima de R$ 10,24, atingindo pico de **R$ 82,33**.
    * `roas`: 229 campanhas (6,54%) com retorno acima de 7,87x (máximo de **14,94x**).

Obs: Isoladamente, com exceção da anomalia no tempo de resolução de atendimento, os outliers identificados não fogem tanto do padrão da base. 

* Estoque pode ser um bom ponto a se explorar (muitos SKUs com estoque baixo e muitos com estoque alto)

3. Observações por tabela

Receita/Margem:

* Receita / margem tende a aumentar em meses específicos (Março, Maio, Novembro, Dezembro) -> Possivelmente datas comemorativas / Black Friday. 
* Margem nominal costuma ser cerca de metade da receita bruta.
* Devoluções (14,88% dos pedidos aprovados) estornam R$ 2,50 milhões em receita e geram um prejuízo direto de R$ 45,1 mil em fretes perdidos, reduzindo a margem efetiva de R$ 9,06M para R$ 7,66M.

Marketing:

* Nos relatórios das plataformas de mídia (`marketing`), o investimento, de modo geral, traz bom retorno aparente, com destaque para **Influenciadores** apresentando o maior ROAS declarado (7,75x) e menor CAC.
* No ERP (`vendas`), o canal de Influenciadores representa menor volume absoluto de pedidos (R$ 1,81M líquido, 5º colocado), mas entrega o maior ticket médio da base (R$ 901,91) e margem saudável (52,3%), apesar do maior desconto médio em cupons (R$ 83,36).

Estoque:

* Mais de R$ 14,7 milhões em estoque disponível (R$ 17,7M em estoque físico) imobilizados em 207 SKUs com status 'Descontinuado'.
* 99 SKUs com estoque zero e 701 SKUs operando em nível crítico abaixo do ponto de pedido, muitos deles de alta demanda.

Base de Clientes:

* Clientes 'Campeões' são relativamente poucos mas impactam grande parte da receita da empresa.
* Muitos clientes 'Promissores' e 'Em Risco'.

Atendimento e Suporte:

* WhatsApp como maior canal de entrada (fatia considerável para email/ChatBot também).
* Maioria dos chamados são relacionados a clientes querendo saber onde está o pedido (30% do volume), gerando mais de R$ 150 mil em custos operacionais evitáveis com triagem via IA.
* Índice de satisfação do cliente (CSAT) mediano (nota 3 mais frequente numa escala de 1 a 5).

4. Observações gerais 

Analisando as bases, percebemos que, embora cada tabela esteja relativamente coerente quando analisada individualmente, quando os dados são analisados em conjunto com outras tabelas, existem muitas incoerências.

Enquanto Atendimento, Marketing e Estoque cobrem o período de **2023 a 2025**, a base de Vendas possui dados utilizáveis apenas para o ano fechado de **2023** e 26 dias de 2024.

Apenas **346 dos 15.000 clientes cadastrados (2,3%)** aparecem na tabela `vendas`. Um único cliente concentra **11.282 compras na tabela `vendas` (40,6% de todos os pedidos)**, enquanto o seu cadastro no CRM informa apenas poucos pedidos.

As colunas de `ltv_acumulado` e `total_pedidos_historico` da tabela de `clientes` não batem com o dinheiro e os pedidos reais da tabela de `vendas`.

30,5% dos pedidos da tabela `vendas` (8.464 vendas) foram realizados em datas anteriores à `data_cadastro` registrada para o respectivo cliente na tabela `clientes`.

A base de Marketing reporta **R$ 210,4M de investimento, R$ 878,6M de receita e 115,3M de conversões**, contra **R$ 14,2M de receita líquida efetiva e 20,8k vendas** na base de vendas.

65,4% dos chamados de atendimento (23.436 de 35.840 tickets) apontam para pedidos que não constam no extrato de vendas (o atendimento abrange pedidos com IDs até ~80k, enquanto vendas foi extraída parcialmente).

A correlação entre o custo unitário da venda e o custo cadastrado no estoque para o mesmo SKU é próxima de zero (`0,008`). Valor do produto do estoque não bate com o valor dele nas vendas(?)

Obs: MUITOS problemas entre as bases. Talvez alguma atitude pra integrar os dados e mante-los consistentes pode ser uma boa recomendação. O estado atual inviabiliza muitas análises e decisões.

5. Análise das Hipóteses descritas no case

* **Hipótese 1: O crescimento pode estar vindo com pior qualidade de margem**
  - PREENCHER

* **Hipótese 2:
  - PREENCHER

* **Hipótese 3: Falhas operacionais podem estar destruindo valor depois da venda**
  - PREENCHER

* **Hipótese 4: O atendimento pode estar concentrando sintomas de problemas recorrentes**
  - Principais pontos identificados:
    * Dúvidas de 'Onde está meu pedido' correspondem ao tipo de dúvida mais frequente com maior custo evitável (R$ 159,660.00)
      * Resolvido de forma relativamente simples com envios de emails / mensagens via wpp em atualizações de status do pedido (o prazo de entrega é normal, cerca de 8,3 dias, logo o problema é falta de visibilidade do rastreio e ansiedade do cliente — mensagens automáticas com link de rastreamento podem ser uma boa ideia).
    * Dúvidas técnicas correspondem ao segundo tipo de dúvida mais frequente com segundo maior custo evitável (R$ 78,888.00)
      * Pode ser resolvido com melhores explicações nas páginas dos produtos / FAQ detalhado.
      Caso continue com alto volume mesmo com explicações / FAQ, atendimento automatizado com IA via wpp podem reduzir custos comparado ao atendimento humano.
    Conclusão: Bom ponto a ser explorado. Possível quick win em envio de notificações acerca do status do pedido. 

* **Hipótese 5: O crescimento pode esconder diferenças importantes entre segmentos de clientes**
  - Principais pontos identificados:
    * Clientes 'Campeões' e 'Fiéis' são poucos mas representam grande parte do faturamento (a diferença não está no valor de cada compra, mas no volume de compras).
    * 46,7% dos clientes estão nas faixas 'Em Risco', 'Hibernando' ou 'Churn'.
      * Talvez seria interessante algum mecanismo pra incentivar segunda, terceira compra e fidelidade.
    Conclusão: Bom ponto, mas é mais médio/longo prazo quando comparado com a hipótese 4, por exemplo. Focar em retenção ativa para clientes em risco.


* **Hipótese 6: Parte da ineficiência pode estar na forma como a informação vira decisão**:
  - Principais pontos identificados:
    * Mais de R$ 14,7 milhões em estoque disponível (R$ 17,7M físico) parados em 207 SKUs fora de linha sem uma ação rápida de liquidação.
      * Talvez seja interessante liquidação para queima de estoque
      * Produtos descontinuados em excesso, produtos muito vendidos em falta (?). Ajustar o mecanismo de compra/liberação de estoque
    * Parece que falta entendimento da situação do estoque. Talvez relatórios gerados com IA / dashboards dinâmicos para a gestão podem auxiliar nessas decisões. 
    Conclusão: Possível quick win na liquidação (verificar melhor depois). Verificar o problema do estoque e se realmente trazer mais informações acerca disso ajudaria na tomada de decisão ou se é algum outro tipo de limitação.