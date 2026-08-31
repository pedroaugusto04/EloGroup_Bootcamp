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
  * **Métricas**: `tempo_resolucao_horas` (diferença entre abertura e fechamento), flag `csat_critico` (nota CSAT <= 2.0), flag `is_automavel` (chamados de status e dúvidas), `custo_evitavel_automacao` e `sla_resposta_estourado`.

4. Análise inicial

Algumas observações:

Receita/Margem:

* Receita / margem tende a aumentar em meses específicos (Março, Maio, Novembro, Dezembro) -> Possivelmente datas comemorativas / Black Friday. 
* Margem nominal costuma ser cerca de metade da receita bruta.
* Devoluções (14,88% dos pedidos aprovados) estornam R$ 2,50 milhões em receita e geram um prejuízo direto de R$ 45,1 mil em fretes perdidos, reduzindo a margem efetiva de R$ 9,06M para R$ 7,66M.

Marketing:

* Investimento em marketing como um todo tende a trazer bons resultados. Investimento de marketing através de **influenciadores** mostra boa eficiência com relação aos demais.

Estoque:

* Mais de R$ 17,7 milhões de capital de giro imobilizados em SKUs com status 'Descontinuado'.
Muitos SKUs de alta demanda operam em risco de ruptura.

Base de Clientes:

* Clientes 'Campeões' são relativamente poucos mas impactam grande parte da receita da empresa.
* Muitos clientes 'Promissores' e 'Em Risco'.

Atendimento e Suporte:

* WhatsApp como maior canal de entrada (fatia considerável para email/ChatBot também).
* Maioria dos chamados são relacionados a clientes querendo saber onde está o pedido (30% do volume), gerando mais de R$ 150 mil em custos operacionais evitáveis com triagem via IA.
* Índice de satisfação do cliente (CSAT) mediano (nota 3 mais frequente numa escala de 1 a 5).