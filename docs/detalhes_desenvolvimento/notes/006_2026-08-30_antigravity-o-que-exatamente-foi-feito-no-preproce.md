# Antigravity: o que exatamente foi feito no preprocessamento atual? me fal... (2026-08-30)

---
type: "event"
workspace: "workspace1"
project: "elogroup-bootcamp"
status: "resolved"
tags: []
occurred_at: "2026-08-30T20:10:32Z"
---

# Antigravity: o que exatamente foi feito no preprocessamento atual? me fal... (2026-08-30)

Source: Antigravity

---

### 👤 User
o que exatamente foi feito no preprocessamento atual? me fale passo a passo. a primeira coisa q eu quero fazer é remover a linha com ticket_id 'TKT' ( pq tem varios dados null, parece ser uma linha incorreta )

### ✨ Assistant
Aqui está o detalhamento completo, passo a passo, de tudo o que foi implementado no pipeline de pré-processamento atual ([`DataPreprocessor`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/infrastructure/preprocessor.py#L27-L276)), seguido da alteração já aplicada para eliminar a linha com `ticket_id = 'TKT'`.

---

### 1. Visão Geral da Arquitetura de Pré-processamento
* **Arquivos Brutos (`data/raw/`):** Lê os 5 CSVs originais.
* **Auditoria de Integridade:** Calcula o hash **SHA-256** de cada arquivo de entrada antes do processamento.
* **Destino:** Salva os dados tratados e tipados no formato otimizado colunar **Apache Parquet** em `data/processed/`.
* **DuckDB In-Memory OLAP:** O banco analítico lê esses Parquets diretamente como views sem perda de performance.
* **Log de Auditoria:** Gera o arquivo `data/audit_log.json` com contagem de linhas antes/depois, nulos tratados e regras aplicadas.

---

### 2. O que foi feito passo a passo em cada tabela

#### 📊 1. Vendas (`process_vendas`)
1. **Limpeza de Linhas Nulas/Corrompidas:** Descarta linhas sem `order_id` ou sem `quantidade` (1 linha corrompida descartada).
2. **Tipagem e Conversão de Datas:** Converte `data_pedido` para datetime (`pd.to_datetime`).
3. **Tratamento Booleano e Nulos:** Padroniza `devolvido` para booleano (`True`/`False`) e preenche valores ausentes de `motivo_devolucao` com `"Não se aplica"`.
4. **Conversão Numérica:** Coage colunas financeiras e operacionais (`quantidade`, `preco_unitario`, `receita_bruta`, `desconto_reais`, `receita_liquida`, `custo_produto`, `custo_frete`, `margem_contribuicao`, `tempo_entrega_real`) para numérico com preenchimento padrão de `0.0`.
5. **Cálculo de Métricas e Enriquecimento:**
   * `margem_calculada = receita_liquida - custo_produto - custo_frete`
   * `margem_pct = (margem_calculada / receita_liquida) * 100`
   * `desconto_pct = (desconto_reais / receita_bruta) * 100`
   * Cria colunas temporais de agregação: `ano_mes` (`YYYY-MM`) e `ano`.

---

#### 📈 2. Marketing (`process_marketing`)
1. **Remoção de Inválidos:** Descarta registros sem `campanha_id`.
2. **Tipagem de Datas:** Converte `data_inicio` e `data_fim` para datetime.
3. **Conversão Numérica:** Garante tipagem numérica de `investimento_reais`, `impressoes`, `cliques`, `conversoes`, `roas`, `receita_gerada` e `cac`.
4. **Cálculo de Eficiência de Mídia:**
   * `ctr_pct = (cliques / impressoes) * 100`
   * `taxa_conversao_pct = (conversoes / cliques) * 100`
   * `cpc_reais = investimento_reais / cliques`
   * `lucro_bruto_mkt = receita_gerada - investimento_reais`

---

#### 📦 3. Estoque (`process_estoque`)
1. **Remoção de Inválidos:** Descarta registros sem `sku_id`.
2. **Tipagem de Datas:** Converte `data_ultima_entrada` para datetime.
3. **Conversão Numérica:** Converte métricas volumétricas e de estoque (`estoque_fisico`, `estoque_reservado`, `estoque_disponivel`, `ponto_pedido`, `custo_unitario`, `preco_venda_sugerido`, `shelf_life_dias`, `volume_m3`, `lead_time_reposicao`).
4. **Regras de Negócio e Ruptura:**
   * `em_ruptura = (estoque_disponivel <= ponto_pedido) | (estoque_disponivel == 0)`
   * `margem_unitaria_sugerida = preco_venda_sugerido - custo_unitario`
   * `markup_sugerido_pct = (margem_unitaria_sugerida / custo_unitario) * 100`
   * `valor_total_estoque = estoque_disponivel * custo_unitario`

---

#### 👥 4. Clientes (`process_clientes`)
1. **Remoção de Inválidos:** Descarta registros sem `customer_id`.
2. **Tipagem de Datas:** Converte `data_cadastro` e `data_nascimento` para datetime.
3. **Conversão Numérica:** Tipa `renda_estimada`, `total_pedidos_historico` e `ltv_acumulado`.
4. **Enriquecimento Demográfico:**
   * Calcula a idade com base no ano de referência do case (2026): `idade = 2026 - ano_nascimento` (preenchendo valores ausentes com a mediana).
   * Normaliza `opt_in_newsletter` como booleano (`True`/`False`).

---

#### 🎧 5. Atendimento (`process_atendimento`)
1. **Remoção de Registros Inválidos:** 
   * Descarta registros sem `ticket_id`.
   * **(Nova regra aplicada)**: Filtra explicitamente a linha com `ticket_id == 'TKT'` (que continha todas as demais colunas como `NaN`).
2. **Tipagem de Datas:** Converte `data_abertura` e `data_fechamento` para datetime.
3. **Conversão Numérica:** Tipa `nota_csat`, `tempo_primeira_resposta_minutos` e `custo_operacional_ticket`.
4. **Métricas de SLA e Qualidade:**
   * `tempo_resolucao_horas = (data_fechamento - data_abertura) em horas` (com limite inferior a 0).
   * `csat_critico = (nota_csat <= 2.0)` (flag para acionamento de IA / retenção).
   * Preenchimento de `categoria_problema` nulo como `"Outros"`.

---

### 3. Alteração Realizada: Remoção do `ticket_id == 'TKT'`

Modificamos o método [`process_atendimento`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/infrastructure/preprocessor.py#L223-L263) com a filtragem explícita:

```python
# Remove registros sem ticket_id ou registros corrompidos/inválidos como 'TKT'
df = df.dropna(subset=["ticket_id"]).copy()
df = df[df["ticket_id"].astype(str).str.strip().str.upper() != "TKT"].copy()
```

* **Resultado da Execução:**
  * Linhas brutas em `Atendimento.csv`: **35.841**
  * Linhas tratadas em `atendimento.parquet`: **35.840** (linha corrompida removida com sucesso).
  * O arquivo `data/audit_log.json` e todos os testes automatizados da suite (`pytest`) foram reexecutados e passaram com 100% de sucesso.

### 👤 User
pq devolvido precisou disso? "TRUE"?

### ✨ Assistant
A linha:

```python
df["devolvido"] = df["devolvido"].astype(str).str.strip().str.upper() == "TRUE"
```

foi usada para **garantir a conversão segura e padronizada para booleano puro (`True`/`False`)**, protegendo o pipeline contra três problemas comuns em arquivos CSV no Pandas:

---

### 1. O problema com `NaN` (Valores Nulos)
No CSV bruto de vendas, há **1 linha com valor nulo (`NaN`)** nessa coluna:
* Se você fizesse uma conversão direta como `df["devolvido"].astype(bool)`, no Python/Pandas **qualquer valor diferente de `0` ou `False`, inclusive `np.nan`, é convertido para `True`**! 
* Ou seja, uma linha nula/em branco acabaria virando falsamente `True` (devolvido).

---

### 2. Variações de formatação em CSV (Strings vs Booleano)
Dependendo de como o CSV é lido ou manipulado, valores booleanos podem vir como:
* Texto com espaços extras: `" True "`, `"False "`
* Variações de maiúsculas/minúsculas: `"true"`, `"True"`, `"TRUE"`
* Texto versus tipo nativo do pandas `object`

O encadeamento `.astype(str).str.strip().str.upper() == "TRUE"` garante que:
* `"TRUE"`, `" True"`, `"true"`, `True` -> viram **`True`** (booleano).
* `"FALSE"`, `False`, `"nan"`, `np.nan`, `None`, vazios -> viram **`False`** (booleano).

---

### 3. Compatibilidade nativa com SQL / Parquet / DuckDB
Ao converter essa coluna explicitamente para um booleano puro (`bool`), quando salvamos em Parquet e consultamos no DuckDB, podemos fazer consultas diretas e expressivas como:

```sql
SELECT AVG(CASE WHEN devolvido = true THEN 1.0 ELSE 0.0 END) * 100.0 AS return_rate
FROM vendas;
```

sem risco de falha de tipagem ou contagens incorretas por conta de strings misturadas com booleanos.

### 👤 User
mas essa nao foi removida logo no inicio?

### ✨ Assistant
**Exatamente! Você tem toda razão.** 

Aquela única linha que tinha `devolvido = NaN` era a linha `27758` (que também tinha `quantidade = NaN`), e ela **já foi removida logo no início** pelo `dropna(subset=["order_id", "quantidade"])`.

Portanto:
* Todas as linhas restantes no dataset já continham booleanos válidos (`True` / `False`).
* Aquele trecho com `.astype(str).str.strip().str.upper() == "TRUE"` acabou sendo apenas uma **redundância / programação defensiva** caso o pandas lesse a coluna como texto ou houvesse outros dados corrompidos.

Podemos simplificar sem nenhum problema para apenas:
```python
df["devolvido"] = df["devolvido"].astype(bool)
```
ou até mesmo `df["devolvido"] = df["devolvido"].fillna(False).astype(bool)`.

### 👤 User
mas ela ja nao eh bool? precisa mexer nela?

### ✨ Assistant
No arquivo CSV, ela **não é lida como `bool` nativo pelo Pandas**, ela é carregada como **`object`** (tipo genérico do Python/Pandas para objetos/strings). 

Isso acontece porque:
1. Como o CSV original continha 1 linha com valor nulo (`NaN`), o leitor padrão do Pandas (`pd.read_csv`) não consegue converter a coluna para `bool` primitivo na leitura, classificando-a como **`object`**.
2. Mesmo após dar o `dropna()`, o Pandas **mantém o tipo `object`** da coluna na memória, a menos que você faça a conversão explícita.

### Por que é importante tipar?
Se ela continuar como `object`:
* Ao salvar em **Parquet**, ela pode ser gravada como string/texto em vez de booleano lógico (`BOOLEAN`).
* No **DuckDB** e nas queries SQL, comparações booleanas como `WHERE devolvido = true` podem gerar inconsistências de tipagem ou perda de performance.

Por isso, só precisamos de uma conversão simples e direta:
```python
df["devolvido"] = df["devolvido"].astype(bool)
```
Isso transforma a coluna de `object` para o tipo primitivo `bool` de forma limpa.

### 👤 User
acho que por enqnt pode tirar essa feature que faz auditoria literalmente nos dados. so nao quero mexer diretamente nos csvs qnd fizer isso, mas nao precisa disso por enqnt.

### ✨ Assistant
Pronto! Toda a camada de auditoria e cálculo de hash SHA-256 foi removida.

### O que foi feito:
1. **Remoção de Auditoria e SHA-256:**
   * Removido o cálculo de SHA-256 e o registro de auditoria em [`preprocessor.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/infrastructure/preprocessor.py).
   * Removidos os arquivos `src/infrastructure/audit_logger.py` e `data/audit_log.json`.
   * Atualizada a suite de testes ([`tests/test_analytics.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/tests/test_analytics.py)) para remover a dependência de auditoria e manter os testes de validação dos dados e limpeza do `ticket_id = 'TKT'`.
2. **Arquivos brutos intactos:** Os arquivos CSV originais em `data/raw/` continuam **100% inalterados**.
3. **Pipeline Reexecutado:** O pipeline gerou novamente os arquivos `.parquet` limpos e leves em `data/processed/`, e todos os testes passaram com sucesso (100%).

### 👤 User
o dado que tava com ticket_id TKT e o resto null tava em qual tabela msm? continua aparecendo no csv original n?

### ✨ Assistant
Estava na tabela de **Atendimento** (`[BootCamp EloGroup 2026] Atendimento.csv`).

E **sim, continua aparecendo normalmente no CSV original** (na linha 35.841 do arquivo bruto em `data/raw/`). 

O CSV bruto **não foi modificado**. A linha só é descartada dinamicamente pelo código do pipeline no Pandas antes de gerar a tabela tratada (`data/processed/atendimento.parquet`), que é a base usada pelo DuckDB e pelo painel.

### 👤 User
pq no dbeaver SELECT * FROM atendimento WHERE customer_id IS NULL aq nao mostra nenhum linha

### ✨ Assistant
Isso acontece por conta de onde a sua consulta no DBeaver está conectada:

### 1. Se o DBeaver estiver conectado ao DuckDB / Parquet processado (`atendimento.parquet`):
* A linha com `ticket_id = 'TKT'` (que era a única linha onde `customer_id` era `NULL`) **foi removida durante o nosso pré-processamento**.
* Como o `atendimento.parquet` já está limpo, não resta nenhuma linha com `customer_id IS NULL` na tabela.

---

### 2. Se o DBeaver estiver consultando diretamente o CSV original:
Dependendo de como o DBeaver ou o driver lê o CSV bruto:
* **String vazia vs NULL:** Em arquivos CSV, um valor em branco pode ser interpretado como string vazia (`''`) ou espaço em vez de `NULL` SQL. Nesse caso, a consulta seria:
  ```sql
  SELECT * FROM atendimento WHERE customer_id IS NULL OR TRIM(customer_id) = '' OR ticket_id = 'TKT';
  ```
* **Leitura com `read_csv` no DuckDB:** Se você fizer no DuckDB:
  ```sql
  SELECT * FROM read_csv('data/raw/[BootCamp EloGroup 2026] Atendimento.csv') WHERE ticket_id = 'TKT';
  ```
  Ele vai retornar exatamente essa última linha (linha 35.841).

### 👤 User
confirme que o processamento não alterou o csv original.

### ✨ Assistant
**Não, de forma alguma!** O CSV original **nunca é alterado**.

O fluxo funciona exatamente assim:

1. **`data/raw/` (CSVs originais):** Ficam intactos e intocados no disco como "somente leitura" (fonte da verdade bruta).
2. **`preprocessor.py` (Script Python):** Lê os CSVs brutos para a memória do Python, faz as limpezas (como remover o `'TKT'`) e **salva o resultado em novos arquivos** em `data/processed/*.parquet`.
3. **`data/processed/` (Arquivos Parquet):** São esses arquivos gerados que o DuckDB e as análises usam.

Se você abrir o arquivo CSV bruto no VS Code, Bloco de Notas ou terminal e for até o final dele, a linha com `TKT` ainda estará lá exatamente como veio.

### 👤 User
realmente existia esse 'tkt' em atendimento?

### ✨ Assistant
**Você não inventou! Realmente tinha.** 

É literalmente a **última linha** do arquivo `data/raw/[BootCamp EloGroup 2026] Atendimento.csv`. Veja o texto bruto como ele está lá gravado no final do arquivo:

```csv
TKT-035838,CLI-01729,ORD-064278,2023-05-11 08:11:33,2023-05-11 10:11:33,ChatBot,Onde está meu pedido?,Escalado para N2,Comprei semana passada e nada até agora. Péssimo.,4.0,0.0,2.0
TKT-035839,CLI-01729,ORD-009904,2025-04-02 18:42:39,2025-12-31 23:59:00,ChatBot,Defeito,Em Análise,O produto chegou com defeito de fabricação.,4.0,0.0,2.0
TKT-035840,CLI-02474,ORD-049113,2024-11-01 16:57:17,2025-12-31 23:59:00,Telefone,Onde está meu pedido?,Em Análise,"O pedido sumiu no rastreamento, preciso de uma posição urgente.",3.0,14.0,15.0
TKT,,,,,,,,,,,
```

Essa linha `TKT,,,,,,,,,,,` veio no dataset bruto do bootcamp com apenas o prefixo `"TKT"` e todas as outras 11 colunas vazias (com vírgulas sem nada entre elas). Você identificou perfeitamente!

### 👤 User
e em vendas? tinha uma tb?

### ✨ Assistant
**Sim! Exatamente a mesma coisa em Vendas!**

Também era a **última linha** do arquivo `[BootCamp EloGroup 2026] Vendas.csv` (linha 27.759). 

O arquivo foi cortado no meio da gravação do produto `"Caderno C"`, deixando todas as colunas numéricas, financeiras e de status como `NaN`/nulas:

```csv
ORD-072219,CLI-14211,SKU-03584,2024-01-26 11:19:29,Google Ads,Lifestyle,Caderno C
```

Essa linha é descartada logo no início de `process_vendas` pelo `dropna(subset=["order_id", "quantidade"])` (ou `dropna(subset=["order_id"])` se não tiver os valores numéricos).

### 👤 User
qual era o id pra eu informar na doc? como a linha tava?

### ✨ Assistant
Aqui estão os dados exatos de ambas as anomalias para você documentar no seu relatório/apresentação:

---

### 1. Tabela: Atendimento (`[BootCamp EloGroup 2026] Atendimento.csv`)
* **Posição:** Linha 35.841 (última linha do arquivo).
* **ID identificado:** `ticket_id = 'TKT'`
* **Como a linha estava no CSV bruto:**
  ```csv
  TKT,,,,,,,,,,,
  ```
* **Descrição do problema:** Registro corrompido/incompleto contendo apenas o prefixo `'TKT'` e todos os outros 11 campos (`customer_id`, `order_id`, datas, métricas e textos) vazios (`NULL` / `NaN`).

---

### 2. Tabela: Vendas (`[BootCamp EloGroup 2026] Vendas.csv`)
* **Posição:** Linha 27.759 (última linha do arquivo).
* **ID identificado:** `order_id = 'ORD-072219'` (com `customer_id = 'CLI-14211'` e `sku_id = 'SKU-03584'`).
* **Como a linha estava no CSV bruto:**
  ```csv
  ORD-072219,CLI-14211,SKU-03584,2024-01-26 11:19:29,Google Ads,Lifestyle,Caderno C
  ```
* **Descrição do problema:** Linha truncada no meio do campo do produto (`"Caderno C"`), sem nenhuma das colunas financeiras e transacionais (`quantidade`, `preco_unitario`, `receita_bruta`, `custos`, `status_pagamento`, `devolvido`, etc., todas `NULL` / `NaN`).