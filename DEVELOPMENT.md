--- ETAPAS REALIZADAS DURANTE A ANÁLISE ---

1. Análise dos dados de forma exploratória, visando entender a estrutura e qualidade dos dados

* Base pareceu completa, sem problemas claros de dados faltantes / inconsistentes

2. Análise mais detalhada por base/coluna 

* Utilizamos ydata-profiling para gerar relatórios de profiling dos dados para cada base

* Vendas: Foi identificada uma linha com order_id 'ORD-072219' e com colunas financeiras/transacionais incompletas. Optamos por remover.
* Atendimento: Foi identificada uma linha com ticket_id 'TKT' e o restante dos dados incompletos. Optamos por remover.
* Nas demais bases, não foram identificadas inconsistências / dados faltantes.

3. Pré-Processamento

* **Padronização Geral de Strings**: Aplicado `str.strip()` em todas as colunas de texto/identificadores de todas as bases para eliminar espaços nas extremidades e evitar inconsistências.

* **Vendas**:
  * **Tipagem**: Conversão de `data_pedido` para datetime, `devolvido` para booleano e preenchimento de `motivo_devolucao` nulo como "Não se aplica".
  * **Numéricas**: Coerção e preenchimento (0.0) de `quantidade`, `preco_unitario`, `receita_bruta`, `desconto_reais`, `receita_liquida`, `custo_produto`, `custo_frete`, `margem_contribuicao` e `tempo_entrega_real`.
  * **Métricas**: `margem_calculada` (receita líquida - custos), `margem_pct`, `desconto_pct`, além de campos temporais (`ano_mes`, `ano`).

* **Marketing**:
  * **Tipagem**: Conversão de datas de campanha (`data_inicio`, `data_fim`) para datetime.
  * **Numéricas**: Coerção e preenchimento de `investimento_reais`, `impressoes`, `cliques`, `conversoes`, `roas`, `receita_gerada` e `cac`.
  * **Métricas**: `ctr_pct` (cliques/impressões), `taxa_conversao_pct` (conversões/cliques), `cpc_reais` (investimento/cliques) e `lucro_bruto_mkt` (receita gerada - investimento).

* **Estoque**:
  * **Tipagem**: Conversão de `data_ultima_entrada` para datetime.
  * **Numéricas**: Coerção de volumes, custos e níveis de estoque (`lead_time_reposicao`, `custo_unitario`, `preco_venda_sugerido`, `estoque_fisico`, `estoque_reservado`, `estoque_disponivel`, `ponto_pedido`, `shelf_life_dias`, `volume_m3`).
  * **Métricas**: Flag de `em_ruptura` (estoque disponível <= ponto de pedido ou zero), `margem_unitaria_sugerida`, `markup_sugerido_pct` e `valor_total_estoque`.

* **Clientes**:
  * **Tipagem**: Conversão de `data_cadastro` e `data_nascimento` para datetime, e `opt_in_newsletter` para booleano.
  * **Numéricas**: Coerção de `renda_estimada`, `total_pedidos_historico` e `ltv_acumulado`.
  * **Métricas**: Cálculo da `idade` do cliente a partir do ano de nascimento.

* **Atendimento**:
  * **Tipagem**: Conversão de `data_abertura` e `data_fechamento` para datetime, e preenchimento de `categoria_problema` nulo como "Outros".
  * **Numéricas**: Coerção de `nota_csat`, `tempo_primeira_resposta_minutos` e `custo_operacional_ticket`.
  * **Métricas**: `tempo_resolucao_horas` (diferença entre abertura e fechamento) e flag `csat_critico` (nota CSAT <= 2.0).

4. Análise inicial

Algumas observações:

Receita/Margem:

* Receita / margem tende a aumentar em mêses específicos (Março, Maio, Novembro, Dezembro) -> Possivelmente datas comemorativas / black friday. 

* Margem costuma ser cerca de aproximadamente metade da receita.

Marketing:

* Investimento em marketing como um todo tende a trazer bons resultados. Investimento de marketing através de **influenciadores** mostra boa eficiência com relação aos demais.

Base de Clientes:

* Clientes 'Campeões' são relativamente poucos mas impactam grande parte da receita da empresa
* Muitos clientes 'Promissores' e 'Em Risco'.

Atendimento e Suporte:

* WhatsApp como maior canal de entrada (fatia considerável para email/ChatBot também).
* Maioria dos chamados são relacionados a clientes querendo saber onde está o pedido.
* Indice de satisfação do cliente (CSAT) mediano (nota 3 mais frequente numa escala de 1 a 5).