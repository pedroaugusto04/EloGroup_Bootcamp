--- ETAPAS REALIZADAS DURANTE A ANÁLISE ---

1. Análise dos dados de forma exploratória, visando entender a estrutura e qualidade dos dados

* Base pareceu completa, sem problemas claros de dados faltantes / inconsistentes

2. Análise mais detalhada por base/coluna 

* Utilizamos ydata-profiling para gerar relatórios de profiling dos dados para cada base

* Vendas: Foi identificada uma linha com order_id 'ORD-072219' e com colunas financeiras/transacionais incompletas. Optamos por remover.
* Atendimento: Foi identificada uma linha com ticket_id 'TKT' e o restante dos dados incompletos. Optamos por remover.
* Nas demais bases, não foram identificadas inconsistências / dados faltantes.

3. Pré-Processamento

* **Padronização Geral de Strings**: Aplicado 'strip' em todas as colunas de texto/identificadores de todas as bases para eliminar espaços nas extremidades e evitar inconsistências.

* **Vendas**:
  * **Tipagem & Sanitização**: Remoção da linha corrompida `ORD-072219` (com campos transacionais nulos), conversão de `data_pedido` para datetime e parsing de `devolvido` para booleano.
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
  * **Métricas**: Flag de `em_ruptura` (estoque disponível <= ponto de pedido ou zero), `margem_unitaria_sugerida`, `markup_sugerido_pct`, `valor_total_estoque`, `is_descontinuado`, `capital_travado_descontinuado` (capital de giro imobilizado em produtos fora de linha) e `capital_em_risco_ruptura`.

* **Clientes**:
  * **Tipagem**: Conversão de `data_cadastro` e `data_nascimento` para datetime, e `opt_in_newsletter` para booleano.
  * **Numéricas**: Coerção de `renda_estimada`, `total_pedidos_historico` e `ltv_acumulado`.
  * **Métricas**: Cálculo da `idade` do cliente a partir do ano de referência do case (2026), `ticket_medio_historico` (LTV / pedidos) e `dias_desde_cadastro`.

* **Atendimento**:
  * **Tipagem**: Conversão de `data_abertura` e `data_fechamento` para datetime.
  * **Numéricas**: Coerção de `nota_csat`, `tempo_primeira_resposta_minutos` e `custo_operacional_ticket`.
  * **Métricas**: `tempo_resolucao_horas` (diferença entre abertura e fechamento), flag `csat_critico` (nota CSAT <= 2.0), flag `is_automatizavel` (chamados de status e dúvidas), `custo_evitavel_automacao` e `sla_resposta_estourado`.

4. Análise inicial

Algumas observações:

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