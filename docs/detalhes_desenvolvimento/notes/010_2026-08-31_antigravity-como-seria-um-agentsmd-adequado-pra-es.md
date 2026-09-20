# Antigravity: como seria um AGENTS.md adequado pra essa aplicacao? Quero r... (2026-08-31)

---
type: "event"
workspace: "workspace1"
project: "elogroup-bootcamp"
status: "resolved"
tags: []
occurred_at: "2026-08-31T12:00:00.000Z"
---

# Antigravity: como seria um AGENTS.md adequado pra essa aplicacao? Quero r... (2026-08-31)

Source: Antigravity

---

### 👤 User
Quero criar um AGENTS.md adequado pra essa aplicacao? Quero reforçar nele a necessidade de validar o tratamento dos dados, sempre verificar se estao sendo geradas inconsistencias ou dados invalidos / que nao representam a realidade ou com informacoes faltantes entre outros pontos adequados pra analise de dados

### ✨ Assistant
Para este projeto de análise e diagnóstico de negócios (**Vértice Analytics / Bootcamp EloGroup 2026**), o [`AGENTS.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/AGENTS.md) deve funcionar como uma **diretriz operacional mandatória e guia de integridade analítica**. 

O principal objetivo é garantir que nenhum agente de IA tome decisões com base em dados corrompidos, gere métricas inconsistentes, ignore devoluções/cancelamentos ou faça preenchimentos cegos de valores nulos (`.fillna()`) que distorçam a realidade do negócio.

Abaixo está a proposta completa e estruturada do arquivo:

---

```markdown
# AGENTS.md — Diretrizes para Agentes de IA (Vértice Analytics)

Este repositório contém a aplicação analítica e consultiva da **Vértice Retail** (EloGroup Bootcamp 2026), baseada em **Streamlit**, **DuckDB**, **Pandas** e **Parquet**.

Todo agente de IA operando nesta base de código deve seguir rigorosamente as regras abaixo, com **prioridade absoluta para a integridade, validação e veracidade dos dados**.

---

## 1. Princípio Fundamental: "Data-First & Ground Truth"

> ⚠️ **REGRA DE OURO**: Nenhuma hipótese, gráfico, query SQL ou recomendação de negócio pode ser apresentada sem validação prévia da integridade dos dados subjacentes. Alucinações de dados ou conclusões baseadas em inconsistências não tratadas são inaceitáveis.

Ao manipular dados nesta aplicação, o agente deve seguir o seguinte protocolo de sanitização e verificação:

### 1.1 Checklist de Validação de Tratamento e Ingestão (`preprocessor.py`)
- **Espaços em Branco e Formatação**: Todas as colunas de texto/identificadores devem passar por `.str.strip()` para evitar falhas de agregação e joins (ex: `'Aprovado '` vs `'Aprovado'`).
- **Detecção de Linhas Corrompidas**: Registros com IDs incompletos, headers duplicados ou colunas transacionais nulas (ex: `ORD-072219`, ticket `TKT`) devem ser auditados e explicitamente descartados no pipeline.
- **Tipagem Estrita**:
  - Datas devem ser convertidas com `pd.to_datetime(..., errors='coerce')` e auditadas para garantir que não geraram NaTs em datas críticas.
  - Booleanos literais (`"True"`, `"False"`) devem ser convertidos de forma idempotente (`.str.upper() == 'TRUE'`).
  - Colunas financeiras e quantitativas devem ser convertidas para numérico de forma segura.

### 1.2 Prevenção de Inconsistências e Distorções Silenciosas
- **Cuidado com `.fillna()` cego**:
  - Preencher valores ausentes com `0.0` em métricas de satisfação (CSAT), tempos ou taxas pode distorcer drasticamente as médias e a realidade analítica. 
  - Sempre justifique se um nulo deve ser preenchido com zero, ignorado na agregação (`NULL` no SQL) ou tratado como categoria `'Não Informado'`.
- **Prevenção de Divisão por Zero**: Em cálculos de percentuais (Margem %, CTR %, Markup %, Taxa de Conversão, etc.), utilize `np.where(denominador > 0, ..., 0.0)` ou `NULLIF(denominador, 0)` no DuckDB.
- **Coerência Temporal**:
  - O ano base de referência para cálculos de idade e histórico do case é **2026**.
  - Tempos de atendimento e entrega não podem ser negativos (`clip(lower=0.0)` ou verificação `data_fim >= data_inicio`).

---

## 2. Consistência Matemática e Regras de Negócio

Qualquer alteração em queries SQL ([`src/queries/`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/queries/)), transformações ou visualizações deve respeitar as seguintes verdades contábeis:

| Domínio | Regra / Fórmula Mandatória | Detalhe Crítico |
| :--- | :--- | :--- |
| **Vendas & Margem** | `margem_calculada = receita_liquida - custo_produto - custo_frete` | Não deduza frete duas vezes se a receita já for líquida. |
| **Devoluções** | `is_venda_efetiva = (status_pagamento == 'Aprovado') AND (NOT devolvido)` | Pedidos devolvidos estornam a receita (`receita_liquida_efetiva = 0`) e tornam o frete de envio um **prejuízo direto** (`margem_efetiva = -custo_frete`). |
| **Estoque** | `em_ruptura = (estoque_disponivel <= ponto_pedido) OR (estoque_disponivel == 0)` | Produtos com status `'Descontinuado'` devem ter seu capital imobilizado segregado de produtos de linha ativa. |
| **Marketing** | `lucro_bruto_mkt = receita_gerada - investimento_reais` | CAC e CPA só são calculados sobre conversões reais válidas. |
| **Atendimento** | `tempo_resolucao_horas = (data_fechamento - data_abertura) / 3600` | Chamados de dúvidas sobre entrega e dúvidas técnicas devem ser classificados como automatizáveis para cálculo de custo evitável. |

---

## 3. Diretrizes para Queries SQL (`src/queries/`) e DuckDB

1. **Evitar Cartesian Products / Multiplicações de Linhas**: Ao realizar `JOIN` entre tabelas (ex: `vendas` com `clientes` ou `estoque`), sempre verifique se a granularidade não infla somatórios de receita.
2. **Uso de Filtros Canônicos**:
   - Para métricas de faturamento e vendas, aplique sempre o filtro `WHERE status_pagamento = 'Aprovado'` (ou analise explicitamente as vendas devolvidas/canceladas).
3. **Modularidade**: Todas as consultas analíticas devem residir em arquivos `.sql` dedicados dentro de [`src/queries/<modulo>/`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/queries/) e serem carregadas via [`src/infrastructure/query_loader.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/infrastructure/query_loader.py).

---

## 4. Estrutura do Projeto & Fluxo de Trabalho

```text
├── app/                        # Interface Streamlit
│   ├── components/cards.py     # Componentes visuais reutilizáveis
│   ├── views/                  # Telas temáticas e hipóteses do case
│   └── main.py                 # Ponto de entrada da aplicação
├── data/
│   ├── raw/                    # CSVs brutos originais (somente leitura)
│   └── processed/              # Arquivos Parquet gerados pelo pipeline
├── src/
│   ├── config.py               # Paths e configurações globais
│   ├── infrastructure/
│   │   ├── preprocessor.py     # Ingestão, saneamento e cálculo de métricas
│   │   ├── database.py         # Conexão DuckDB e registro de views
│   │   └── query_loader.py     # Carregamento de queries SQL
│   └── queries/                # Consultas SQL versionadas
└── tests/
    └── test_analytics.py       # Testes de integridade e validação matemática
```

---

## 5. Ciclo Obrigatório de Verificação para Agentes

Sempre que implementar uma nova feature, hipótese ou correção:

1. **Modificou o pipeline de dados (`preprocessor.py`)?**
   - Execute o pipeline para atualizar os Parquets:
     ```bash
     python -m src.infrastructure.preprocessor
     ```
2. **Rodar os testes automatizados de sanidade**:
   - Execute a suíte de testes do pytest:
     ```bash
     pytest tests/
     ```
   - Garanta que todos os testes passem (integridade matemática, views do DuckDB, tipos de dados e exclusão de anomalias).
3. **Se adicionar novas métricas ou regras**:
   - Crie o respectivo teste de validação unitária/integração em [`tests/test_analytics.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/tests/test_analytics.py).
4. **Verificar os Dashboards Streamlit**:
   - Garanta que os filtros de tela não gerem valores `NaN` nos KPI cards nem gráficos vazios.
```

---

### Principais Destaques Desta Estrutura:
1. **Regras Contábeis e de Negócio Fixas**: Evita que o agente deduza custos incorretamente ou ignore o impacto das devoluções na margem efetiva.
2. **Prevenção de Nulos e Erros Matemáticos**: Regras explícitas contra divisões por zero e uso indevido de `.fillna()`.
3. **Contrato de Validação com `pytest`**: Obriga o agente a rodar e expandir os testes em [`tests/test_analytics.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/tests/test_analytics.py) após qualquer manipulação de dados.
4. **Arquitetura Modular**: Deixa claro o fluxo `data/raw` $\rightarrow$ `preprocessor.py` $\rightarrow$ `data/processed` $\rightarrow$ `DuckDB` $\rightarrow$ `queries/*.sql` $\rightarrow$ `Streamlit`.

Deseja que eu crie diretamente este arquivo como [`AGENTS.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/AGENTS.md) na raiz do repositório?

### 👤 User
quero criar um de forma simplificada e conforme as recomendacoes: simples, direto, sem rodeios e redundancias e curto: somente com o necessario e essencial para analise e tratamento dos dados: validacoes, verificacoes de coerencia, nao inventar dados etc

### ✨ Assistant
O arquivo [`AGENTS.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/AGENTS.md) foi criado na raiz do repositório seguindo as melhores práticas atuais: **curto, direto ao ponto, denso em contexto prático e sem redundâncias de prompt**.

### Conteúdo aplicado no [`AGENTS.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/AGENTS.md):

```markdown
# AGENTS.md

Instruções operacionais para agentes de IA no repositório **Vértice Analytics** (Streamlit + DuckDB + Pandas/Parquet).

---

## 1. Visão Geral e Arquitetura

- **Pipeline**: `data/raw/*.csv` ➔ `src/infrastructure/preprocessor.py` ➔ `data/processed/*.parquet` ➔ `DuckDB` ➔ `src/queries/*.sql` ➔ `Streamlit (app/)`.
- **Ano base do case**: `2026` (usado para cálculo de idade e métricas temporais).

---

## 2. Regras Críticas de Integridade de Dados

1. **Higienização Obrigatória**:
   - Aplicar `.str.strip()` em colunas de texto/IDs para evitar falhas em joins e filtros.
   - Descartar linhas corrompidas conhecidas (ex: `order_id == 'ORD-072219'`, `ticket_id == 'TKT'`).
2. **Prevenção de Inconsistências**:
   - **Proibido `.fillna()` cego**: Não preencher nulos com `0` sem justificativa (distorce médias de CSAT e taxas).
   - **Divisão por Zero**: Tratar denominadores com `np.where(denominador > 0, ..., 0.0)` ou `NULLIF(denominador, 0)`.
   - **Tempos e Durações**: Não podem ser negativos (usar `.clip(lower=0.0)`).
3. **Consistência Contábil e de Negócio**:
   - `margem_calculada = receita_liquida - custo_produto - custo_frete`.
   - **Devoluções**: Se `devolvido == True`, `receita_liquida_efetiva = 0` e `margem_efetiva = -custo_frete` (prejuízo do frete).
   - **Vendas Válidas**: Filtrar por `status_pagamento == 'Aprovado'`.
   - **Ruptura de Estoque**: `estoque_disponivel <= ponto_pedido OR estoque_disponivel == 0`.

---

## 3. Padrões de Código e Queries

- **Queries SQL**: Centralizar consultas em `src/queries/<dominio>/*.sql` e carregar via `src.infrastructure.query_loader`.
- **Joins Seguros**: Evitar joins 1-N que dupliquem registros ou inflam métricas financeiras.
- **Visualização**: Garantir que componentes Streamlit tratem retornos vazios sem exibir `NaN`.

---

## 4. Comandos e Validação Obrigatória

Após qualquer modificação em pipelines, métricas ou queries:

```bash
# 1. Regenerar Parquets após alterar preprocessor
python -m src.infrastructure.preprocessor

# 2. Executar testes de integridade e validação matemática
pytest tests/

# 3. Executar aplicação Streamlit
streamlit run app/main.py
```
```

### Por que esse formato é ideal?
- **Pouco consumo de contexto/tokens**: Menos de 55 linhas com alta densidade de informação útil.
- **Imperativos claros**: Foco direto em proibições analíticas comuns (ex: `.fillna()` sem contexto, divisões por zero) e regras contábeis invioláveis (ex: frete perdido em devoluções).
- **Loop de feedback fechado**: Qualquer agente sabe imediatamente quais comandos rodar (`preprocessor` e `pytest`) para validar se quebrou ou gerou dados incorretos.

### 👤 User
o ponto 2 eu ja fiz no pre processamento. As bases utilizadas pelo agente ja estarao limpas e sem dados incorretos ( porem possivelmente incoerentes/inconsistentes ) 

### ✨ Assistant
Excelente observação. Você tem toda razão: ficar descrevendo detalhes de implementação passada (como *"removemos a linha X"* ou *"demos strip no campo Y"*) é redundante e consome contexto à toa, já que o código de ingestão já faz isso.

O papel do [`AGENTS.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/AGENTS.md) deve ser orientar a **postura analítica ativa do agente** ao criar novas queries, dashboards e diagnósticos.

O arquivo foi atualizado na raiz do projeto com apenas **42 linhas**, direto ao ponto:

```markdown
# AGENTS.md

Instruções para agentes de IA atuando na análise de dados, queries e dashboards do **Vértice Analytics**.

---

## 1. Arquitetura em Poucas Palavras

- **Dados**: `data/processed/*.parquet` ➔ Carregados como views no `DuckDB` (`src/infrastructure/database.py`).
- **Consultas**: Centralizadas em `src/queries/<modulo>/*.sql` e consumidas pelo `src.infrastructure.query_loader`.
- **Interface**: Dashboards modulares em `app/views/` via Streamlit.

---

## 2. Postura Analítica e Validação Ativa de Dados

Antes e depois de criar ou modificar qualquer query, métrica, gráfico ou diagnóstico:

1. **Adequação ao Propósito da Análise**:
   - Questione se o recorte de dados reflete fielmente a pergunta de negócio.
   - *Exemplo*: Para métricas de margem real, considere o impacto de cancelamentos/devoluções; para volume de atrito operacional, olhe todas as transações; para performance de estoque, distingua SKUs ativos de descontinuados.

2. **Checagem de Sanidade dos Resultados**:
   - Valide se os valores retornados são plausíveis antes de plotar (evite taxas impossíveis, duplicações de receita por joins 1-N ou valores fora de escala).
   - Compare os totais agregados das novas queries com os KPIs macro do dashboard para garantir consistência global.

3. **Tratamento de Dados Ausentes e Casos de Borda**:
   - Não mascare ausência de informação como zero quando isso distorcer o significado analítico (ex: CSAT não avaliado vs nota zero).
   - Garanta que gráficos e cards tratem filtros vazios ou períodos sem dados com mensagens informativas, nunca com `NaN` ou erros na interface.

---

## 3. Comandos Úteis

```bash
# Executar suíte de testes
python -m pytest tests/

# Iniciar a aplicação
streamlit run app/main.py
```
```

### O que mudou:
- **Zero ruído de implementação**: Não repete o que já está codado no `preprocessor.py`.
- **Foco em pensamento crítico**: Exige que o agente avalie se o filtro ou agrupamento realmente responde à dor de negócio.
- **Validação de sanidade**: Obriga o agente a conferir se os números fazem sentido antes de gerar visualizações no Streamlit.

### 👤 User
no 3. em tratamento de dados ausentes o ideal seria o agente me perguntar antes de tomar qualquer atitude

### ✨ Assistant
Essa visão é fundamental. Em análise de dados, **premissas sobre dados ausentes e imputações alteram o resultado de negócio**, e o agente nunca deve assumir essas decisões de forma silenciosa ou unilateral.

Fizemos a distinção clara entre:
1. **Decisões metodológicas/de negócio** (ex: o que fazer com CSATs não avaliados ou clientes sem canal de aquisição): o agente **deve expor o impacto, dar sugestões e perguntar/alinhar com você**.
2. **Tratamento técnico na UI** (ex: filtros que retornam zero linhas): o agente apenas garante que a interface exiba um aviso informativo amigável (`st.info`) em vez de crashar ou mostrar `NaN`.

O ponto 3 do [`AGENTS.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/AGENTS.md) foi atualizado para:

```markdown
3. **Tratamento de Dados Ausentes e Decisões Metodológicas**:
   - **Não tome decisões de imputação sozinho**: Ao encontrar dados ausentes, anomalias ou ambiguidades (ex: CSAT em branco, dados cadastrais faltantes), aponte o impacto, sugira opções (ex: ignorar, criar categoria 'Não informado', imputar) e **consulte o usuário antes de aplicar**.
   - **Tratamento na Interface**: Garanta que filtros vazios ou períodos sem dados exibam mensagens informativas amigáveis (`st.info`), nunca `NaN` ou erros no dashboard.
```

Com isso, o documento fica enxuto, direto e previne que o agente altere a narrativa analítica sem o seu consentimento.

### 👤 User
tem mais algo mt relevante pra colocar?

### ✨ Assistant
**Do jeito que está, já está ótimo e cobre 95% do que é crítico** sem sobrecarregar a janela de contexto do modelo.

Se fôssemos apontar **duas coisas muito específicas deste projeto** que poderiam ser úteis (mas apenas se você achar necessário), seriam:

---

### 1. Ano de Referência Fixo (`2026`)
* **O risco**: Agentes de IA tendem a usar `datetime.now().year` para calcular idades ou recência de compras (RFM). Como este case é simulado com base no ano de **2026**, qualquer cálculo temporal usando o ano do sistema gerará números negativos ou inconsistentes.
* **Impacto**: Evita cálculos de idade/tempo distorcidos em novas queries de clientes ou estoque.

### 2. Padrão Visual e Componentes Reutilizáveis
* **O risco**: O agente começar a inventar estilos próprios ou recriar cards de KPI do zero no Streamlit em vez de usar o que você já padronizou.
* **Impacto**: Lembrar de reutilizar `app/components/cards.py` e as cores de `app/styles/elo_theme.py` para manter a identidade visual do case.

---

### Veredito:
Se o seu foco principal é **qualidade e integridade dos dados / postura analítica**, a versão atual já está no **ponto ideal** (concisa, firme e sem gordura). 

Você prefere deixar como está ou acha válido adicionar esses dois pequenos lembretes de uma linha?

### 👤 User
Defina uma role no inicio caso seja rlevante. defina a role e objetivo com base no contexto do projeto ( vale colocar no inicio do agents o objetivo e informacoes relevantes do bootcamp)

### ✨ Assistant
O arquivo [`AGENTS.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/AGENTS.md) foi atualizado com a remoção da frase genérica e a inclusão da **Role**, do **Objetivo do Bootcamp** e do **Ano Base** de forma enxuta no cabeçalho:

```markdown
# Vértice Analytics

- **Papel**: Consultor analítico sênior no case **Vértice Retail (Bootcamp EloGroup 2026)**.
- **Objetivo**: Diagnosticar gargalos de rentabilidade e produtividade, validar hipóteses de negócio e estruturar recomendações executivas com impacto financeiro (R$) para o C-Level (horizonte 30/60/90 dias).
- **Ano Base**: `2026` (referência temporal fixa para cálculos de idade, recência e histórico).

---

## 1. Arquitetura em Poucas Palavras

- **Dados**: `data/processed/*.parquet` ➔ Carregados como views no `DuckDB` (`src/infrastructure/database.py`).
- **Consultas**: Centralizadas em `src/queries/<modulo>/*.sql` e consumidas pelo `src.infrastructure.query_loader`.
- **Interface**: Dashboards modulares em `app/views/` via Streamlit, reutilizando componentes de `app/components/cards.py` e estilos de `app/styles/elo_theme.py`.

---

## 2. Postura Analítica e Validação Ativa de Dados

Antes e depois de criar ou modificar qualquer query, métrica, gráfico ou diagnóstico:

1. **Adequação ao Propósito da Análise**:
   - Questione se o recorte de dados reflete fielmente a pergunta de negócio.
   - *Exemplo*: Para margem real, considere cancelamentos/devoluções; para atrito operacional, olhe todas as transações; para estoque, distingua SKUs ativos de descontinuados.

2. **Checagem de Sanidade dos Resultados**:
   - Valide se os valores retornados são plausíveis antes de plotar (evite taxas impossíveis, duplicações de receita por joins 1-N ou valores fora de escala).
   - Compare os totais agregados das novas queries com os KPIs macro do dashboard para garantir consistência global.

3. **Tratamento de Dados Ausentes e Decisões Metodológicas**:
   - **Não tome decisões de imputação sozinho**: Ao encontrar dados ausentes, anomalias ou ambiguidades (ex: CSAT em branco, dados cadastrais faltantes), aponte o impacto, sugira opções (ex: ignorar, criar categoria 'Não informado', imputar) e **consulte o usuário antes de aplicar**.
   - **Tratamento na Interface**: Garanta que filtros vazios ou períodos sem dados exibam mensagens informativas amigáveis (`st.info`), nunca `NaN` ou erros no dashboard.

---

## 3. Comandos Úteis

```bash
# Executar suíte de testes
python -m pytest tests/

# Iniciar a aplicação
streamlit run app/main.py
```
```

O documento agora tem **44 linhas**, fornece contexto de negócio claro e estabelece um padrão de validação contínua para qualquer agente que atuar no repositório.