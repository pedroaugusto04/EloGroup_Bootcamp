# Antigravity: em uma analise de dados semelhante a essa, qual o padrao e p... (2026-09-08)

---
type: "event"
workspace: "workspace1"
project: "elogroup-bootcamp"
status: "resolved"
tags: []
occurred_at: "2026-09-08T12:00:00.000Z"
---

# Antigravity: em uma analise de dados semelhante a essa, qual o padrao e p... (2026-09-08)

Source: Antigravity

---

### 👤 User
em uma analise de dados semelhante a essa, qual o padrao e passo a passo pra investigacao? analise exploratoria-> profiling -> etc? todos foram feitos aqui?

### ✨ Assistant
Vou explorar o workspace para entender o que foi feito no projeto antes de responder!

### ✨ Assistant
Agora tenho um panorama completo do projeto. Deixa eu criar um relatório estruturado respondendo sua pergunta.

### ✨ Assistant
Criei o relatório completo! Aqui vai um resumo rápido:

## O pipeline padrão tem 10 etapas — **9 foram feitas aqui**, 1 está em andamento:

| # | Etapa | Status |
|---|---|---|
| 1 | **Problem Framing** | ✅ Case bem definido com 6 hipóteses guia |
| 2 | **Data Room** | ✅ 5 datasets organizados em `data/raw/` |
| 3 | **Data Profiling** | ✅ Relatórios HTML gerados com `ydata-profiling` |
| 4 | **Data Cleaning** | ✅ Feito no script `analise_bootcamp_vertice.py` |
| 5 | **EDA** | ✅ Queries SQL por domínio em `src/queries/` |
| 6 | **Teste de Hipóteses** | ✅ 3 hipóteses confirmadas com números |
| 7 | **Segmentação (RFM)** | ✅ Clientes segmentados, análise de LTV e canal |
| 8 | **Síntese de Insights** | ✅ KPIs executivos consolidados |
| 9 | **Exec Output / Roadmap** | ✅ Matriz 30/60/90 dias |
| 10 | **Produto / Automação** | 🔄 Em construção (Streamlit + Agent + API) |

**A ordem clássica é exatamente essa:** profiling → cleaning → EDA → hipóteses → insights → produto. O projeto seguiu o padrão corretamente — a etapa atual é transformar o diagnóstico em **produto analítico operacional** (dashboard + agente de IA).

O que falta fortalecer está detalhado no relatório — principalmente o **Assumptions Log** (documentar as decisões de limpeza) e possíveis análises cruzadas entre os 5 datasets.

### 👤 User
mas n seria cleaning primeiro? qual a ordem masi recomendada e robusta

### ✨ Assistant
Boa pergunta — essa é uma dúvida real que divide profissionais. A resposta curta: **profiling vem antes do cleaning**, e há uma razão técnica forte pra isso.

---

## A ordem mais robusta e o porquê

```
Problem Framing
      ↓
Data Inventory
      ↓
🔍 Profiling BRUTO  ← perfila o dado SUJO
      ↓
🧹 Cleaning         ← limpa com base no que o profiling revelou
      ↓
✅ Profiling PÓS-CLEANING  ← valida que a limpeza funcionou
      ↓
EDA
      ↓
Hipóteses → Segmentação → Insights → Output → Produto
```

### Por que profiling ANTES do cleaning?

> **Você não pode limpar o que não enxerga.**

O profiling bruto revela **o que precisa ser limpo**:
- Quais colunas têm nulls e em qual proporção
- Quais tipos estão errados (`"TRUE"` como string em vez de bool)
- Outliers reais vs. erros de input
- Distribuições inesperadas (ex: data de nascimento em 1900)
- Cardinalidade de categóricas (typos como `"São Paulo"` vs `"Sao paulo"`)

Se você limpar antes de perfilar, você age **no escuro** — pode descartar linhas que eram válidas ou normalizar coisas que não precisavam.

### Por que um segundo profiling pós-cleaning?

Para **validar** que a limpeza não introduziu novos problemas — ex: um `fillna(0)` que distorce uma média, ou um `dropna()` que criou viés de seleção.

---

## Como ficou no projeto Vértice

No projeto, a ordem foi aproximadamente correta:

| Etapa | O que aconteceu | Problema |
|---|---|---|
| Profiling | ✅ Feito nos 5 datasets (HTML reports) | — |
| Cleaning | ✅ Feito no script Python | Misturado com carregamento, sem log de decisões |
| Profiling pós-cleaning | ❌ **Não foi feito** | Sem validação de que o cleaning funcionou |

O maior gap é o **segundo profiling** — que neste projeto seria simples de adicionar rodando o `ydata-profiling` nos dataframes **após** o `carregar_e_limpar_dados()`.

---

Quer que eu adicione um step de profiling pós-cleaning automatizado ao pipeline do projeto?

### 👤 User
nao entendi. oq seria esse profiling pos-cleaning? mudaria algo aqui?

### ✨ Assistant
Boa pergunta. Deixa eu mostrar com exemplos concretos do **próprio projeto**.

### ✨ Assistant
Perfeito. Agora consigo explicar com o código real.

---

## O que é profiling pós-cleaning, na prática

**Profiling** é simplesmente "tirar uma foto" do dataset — quantas linhas, quantos nulls, qual distribuição. Você já fez isso **antes** da limpeza (os 5 HTMLs em `docs/profiling/`).

**Profiling pós-cleaning** = tirar essa mesma foto **depois** de rodar o `carregar_e_limpar_dados()` — pra verificar se as transformações funcionaram como esperado ou criaram problemas novos.

---

## Exemplos concretos do **seu código**

### Exemplo 1 — o `dropna` silencioso
```python
# linha 51
self.df_vendas = pd.read_csv(path_vendas).dropna(subset=["order_id"])
```
Quantas linhas foram descartadas aqui? **Você não sabe.** Podem ser 0 ou podem ser 5.000. Sem o profiling pós-cleaning, não tem como verificar se o dado perdido era relevante.

---

### Exemplo 2 — o `errors="coerce"` que vira NaT
```python
# linha 52
self.df_vendas["data_pedido"] = pd.to_datetime(self.df_vendas["data_pedido"], errors="coerce")
```
`errors="coerce"` converte datas inválidas em `NaT` (null de data). Se houver 500 pedidos com data malformada, eles viram `NaT` **silenciosamente** — e depois suas análises temporais ficam erradas sem você perceber.

---

### Exemplo 3 — o cast de booleano
```python
# linha 53
self.df_vendas["devolvido"] = self.df_vendas["devolvido"].astype(str).str.upper() == "TRUE"
```
E se no CSV tiver valores como `"1"`, `"yes"`, `"Sim"`, `"true "` (com espaço)? Todos viram `False` silenciosamente. O profiling pós-cleaning mostraria a distribuição True/False pra você validar se bate com o esperado.

---

## Mudaria algo no projeto?

**No resultado final, provavelmente não** — porque os dados do case são simulados e limpos por design. Mas em um projeto real (ou na avaliação do bootcamp), é o que diferencia uma análise **confiável** de uma análise **ingênua**.

O profiling pós-cleaning responderia perguntas como:

| Pergunta | Sem pós-profiling | Com pós-profiling |
|---|---|---|
| Quantas linhas foram descartadas no `dropna`? | ❓ | ✅ Vejo exatamente |
| `data_pedido` tem NaTs após o parse? | ❓ | ✅ Vejo a % de nulls |
| `devolvido` tem a proporção esperada True/False? | ❓ | ✅ Vejo a distribuição |
| O join entre datasets não perdeu registros? | ❓ | ✅ Vejo as contagens |

---

Em resumo: **não muda o conteúdo da limpeza, muda a confiança que você tem nela.** É o "print de confirmação" formal e estruturado do que aconteceu com seus dados.

Quer que eu implemente isso no projeto — um método `validar_cleaning()` que gera um relatório resumido pós-limpeza?

### 👤 User
vc pode fazer e ver se fica correto conforme o resto da implementacao ou se sobrou algo q eu n vi?

### ✨ Assistant
Deixa eu ler o código completo primeiro antes de mexer em qualquer coisa.

### ✨ Assistant
Agora tenho o quadro completo. Vou implementar o `validar_cleaning()` **no lugar certo** — que é o `preprocessor.py` (o cleaning real do projeto), não o script de arquivo. E também vou apontar o que encontrei de inconsistências.

### ✨ Assistant
Agora tenho tudo que preciso. Vou adicionar o método `validar_cleaning()` diretamente no [`preprocessor.py`](file:///C:/Users/pedro/OneDrive/Documentos/GitHub/EloGroup_Bootcamp/src/infrastructure/preprocessor.py), que é o pipeline de cleaning real do projeto.

### ✨ Assistant
Agora vou rodar pra ver se funciona e se encontra algum problema real nos dados:

### ✨ Assistant
Erro de encoding dos emojis no terminal Windows (cp1252). Vou substituir os emojis por ASCII puro:

### ✨ Assistant
Rodou limpo. Vamos ver o JSON gerado pra ver os detalhes completos:

### ✨ Assistant
Tudo rodou perfeito. Aqui está o resultado completo:

---

## O que o profiling pós-cleaning encontrou

**Dados estão íntegros** — zero alertas em todos os 5 datasets. Mas os números revelam coisas interessantes que **confirmam e enriquecem o diagnóstico**:

| Dataset | Bruto | Processado | Descartadas | Observações |
|---|---|---|---|---|
| vendas | 27.759 | 27.758 | **1** | 1 linha sem `preco_unitario`/`status_pagamento` — intencional |
| marketing | 3.500 | 3.500 | 0 | Limpo |
| estoque | 5.000 | 5.000 | 0 | Limpo |
| clientes | 15.000 | 15.000 | 0 | Limpo |
| atendimento | 35.841 | 35.840 | **1** | 1 linha de cabeçalho `"TKT"` removida — tratamento já existia |

### Achados que confirmam o diagnóstico:
- **`devolvido`: 14,87% True** → bate exatamente com os 14,88% reportados no diagnóstico ✅
- **`is_automatizavel`: 44,86% True** → confirma os 44,9% de tickets automatizáveis do relatório ✅
- **`is_estoque_critico`: 701 SKUs** → confirma os 701 SKUs em ruptura iminente ✅
- **`sla_resposta_estourado`: 33%** → dado novo — **1 em cada 3 tickets estoura o SLA de resposta**, não estava no diagnóstico original

---

O que foi adicionado ao projeto:
- [`validar_cleaning()`](file:///C:/Users/pedro/OneDrive/Documentos/GitHub/EloGroup_Bootcamp/src/infrastructure/preprocessor.py) no `DataPreprocessor` — roda automaticamente ao final de `run_all()`
- [`cleaning_validation_report.json`](file:///C:/Users/pedro/OneDrive/Documentos/GitHub\EloGroup_Bootcamp/docs/profiling/cleaning_validation_report.json) gerado em `docs/profiling/` — o "assumptions log" estruturado que estava faltando

### 👤 User
quais informacoes rlevantes eu posso tirar do profile? dados interessantes, outliers,distribuicoes etc?

### ✨ Assistant
Os HTMLs são muito grandes pra ler diretamente. Vou rodar um script que extrai as métricas mais relevantes dos dados processados — distribuições, outliers, skewness, concentração — e te entrego um relatório limpo.

### ✨ Assistant
O script está sendo executado do diretório errado. O `ROOT` está sendo calculado erroneamente a partir do path do arquivo scratch. Vou corrigir isso:

### ✨ Assistant
Quase tudo rodou. Só deu erro na coluna `canal_aquisicao` — vou checar o nome correto e continuar:

### ✨ Assistant
Todos os dados estão em mãos. Agora vou montar o relatório de insights:

### ✨ Assistant
Relatório completo criado! Aqui os **10 achados mais relevantes** — alguns confirmam o diagnóstico, outros são achados novos:

---

### 🔴 Achados críticos (que o diagnóstico não tinha explicitado)

1. **Tempo de resolução com P95 de 845 dias** — fisicamente impossível. São tickets com `data_fechamento` incorreta no sistema (nunca formalmente encerrados). **Problema de qualidade de dados**, não visto antes.

2. **Mediana de resposta = 11min, mas média = 135min** — a operação é rápida pra maioria, mas existem 2.385 tickets com tempos absurdos puxando a média. Esses outliers provavelmente são os responsáveis pelo CSAT ruim.

3. **Defeito tem 31,5% de CSAT crítico** — o pior de todas as categorias, não estava em destaque no diagnóstico original.

### 🟡 Achados que confirmam e refinam o diagnóstico

4. **LTV skewness = 2,94** — média (R$9.273) quase o dobro da mediana (R$4.773). O número mais honesto pra apresentar à diretoria é a mediana.

5. **Influenciador: ROAS 7,69x recebendo só 13,3% do orçamento vs Marketplace com 3,00x recebendo 15,5%** — inversão clara de alocação.

6. **229 campanhas outlier de ROAS alto** — candidatas concretas a escalar com mais verba.

### ⚪ Limitações dos dados simulados

7. **Idades 20–41, skewness zero, outliers zero** — não use para segmentação etária real. É artifício de simulação.

### 👤 User
o quao impactantes sao esses outliers considerados?

### ✨ Assistant
Ótima pergunta — e a resposta é: **depende do tipo de outlier**. Existem 3 tipos completamente diferentes, e a ação certa pra cada um é oposta.

### ✨ Assistant
Agora tenho tudo para dar uma resposta definitiva e precisa. Os dados revelaram coisas muito claras sobre cada grupo.

---

## Os 3 tipos de outlier — e o que fazer com cada um

### 🟢 Tipo 1: Outliers que são o **sinal mais importante** → JAMAIS remover

**Campanha com ROAS outlier (229 campanhas):**
```
Fence IQR: 7,87x
ROAS médio dos outliers: 11,33x
Distribuição: 222 Influenciador + 7 TikTok Ads
```
Esses não são ruído — são **suas melhores campanhas**. Remover seria o equivalente a jogar fora a lista de clientes VIP. O correto é **isolar e estudar** o que essas 222 campanhas de Influenciador têm em comum.

---

**Clientes com LTV outlier (1.253 clientes):**
```
Fence IQR: R$ 25.507
LTV médio dos outliers: R$ 41.730
Segmento: 511 Campeão + 509 Fiel + 226 Promissor
```
São os seus **melhores clientes**. Removê-los de uma análise de LTV médio é o que cria a ilusão de que a base toda tem LTV de R$9.273 — quando a mediana real é R$4.773. Mantenha sempre. Use a **mediana** quando quiser representar o cliente típico, não a média.

---

### 🔴 Tipo 2: Outliers que são **erro de dado** → Tratar/flaggar

**tempo_resolucao_horas (8.798 tickets — 24,6%):**
```
data_fechamento nula: 0  ← nenhuma nula!
Mas: TKT-000004 aberto em nov/2024, fechado em 2025-12-31 23:59:00
     TKT-000005 aberto em jul/2023, fechado em 2025-12-31 23:59:00
```
A data de fechamento **não é nula, mas é `2025-12-31 23:59:00`** — uma data sentinel, que significa *"ticket ainda aberto, preenchemos com o fim do período de dados"*. São tickets **nunca resolvidos**, não tickets que demoraram 845 dias. **Não remover, mas separar em categoria própria: `status_aberto`.**

---

**Campanhas de duração outlier (424 campanhas):**
```
Fence: 202 dias
Max: 1.095 dias
Status: 100% "Ativa"
```
Todas as 424 campanhas anômalas estão com status `"Ativa"`. Campanha ativa por 3 anos quase certamente é um **dado de CRM mal gerenciado** (campanha "sempre ativa" que ninguém desativou) ou campanha evergreen desatualizada. Não remova — mas sinalize para auditoria.

---

### 🟡 Tipo 3: Outliers que são **eventos reais raros** → Manter, analisar separado

**Pedidos com margem negativa (427 pedidos — 1,75%):**
```
Perda total: -R$ 5.782
Distribuição por canal: todos os canais têm (sem concentração)
Distribuição por categoria: todas as categorias têm
```
São pedidos reais onde `desconto + frete > receita líquida`. Distribuídos uniformemente — não há canal ou categoria "culpado". A causa provável são **combinações extremas de desconto alto + frete alto + item barato**. Não remover das análises — são a evidência concreta de vazamento de margem.

---

## Regra prática para este projeto

```
Outlier de ROAS alto       → MANTER (são oportunidades)
Outlier de LTV alto        → MANTER (são VIPs)
Outlier de resolução alta  → TRATAR (data sentinel 31/12/2025)
Outlier de duração campanha → AUDITAR (campanha "viva" há 3 anos)
Pedidos com margem negativa → MANTER (são o vazamento real)
```

> O IQR é um **detector**, não um juiz. Ele diz "isso é estatisticamente distante do centro" — mas só você (com contexto de negócio) decide se isso é ruído, erro ou o dado mais importante da análise.

Quer que eu implemente o tratamento da data sentinel no `preprocessor.py`? É uma correção concreta — tickets com `data_fechamento == 31/12/2025 23:59` deveriam ter `tempo_resolucao_horas = NaN` e um flag `is_aberto = True`.

### 👤 User
e os do tempo de resposta?

### ✨ Assistant
Bom ponto — deixa eu investigar os outliers de `tempo_primeira_resposta_minutos` especificamente, da mesma forma que fizemos com a resolução.

### ✨ Assistant
Os dados falam muito claramente. Deixa eu interpretar:

---

## O que os outliers de tempo de resposta são, de fato

### Evidências do que os dados mostram:

**1. Distribuição contínua, sem salto artificial**
```
Q3:    189 min
Fence: 468 min  ← ponto de corte IQR
Outliers começam em: 469 min
Top valores: 478, 474, 475, 473... (contínuos)
```
Não há nenhum salto brusco no valor 469. Os outliers são a **continuação natural da distribuição** — não há um valor sentinel específico que explique a concentração.

**2. CSAT idêntico entre normais e outliers**
```
Normal:  3.24
Outlier: 3.27
```
Praticamente **igual**. Se esses 2.385 tickets com tempo de resposta alto fossem casos graves (clientes furiosos esperando horas), o CSAT deveria ser muito pior. O fato de ser igual sugere que **o tempo de resposta alto não está destruindo a satisfação adicionalmente** — o cliente já estava insatisfeito por outro motivo.

**3. Categoria de problema é idêntica**
```
"Onde está meu pedido?" normal: 30,0% | outlier: 31,1%
Defeito normal: 18,2%              | outlier: 17,8%
```
Mesma distribuição de problemas — não é um tipo específico de ticket que gera resposta lenta.

**4. Hora de abertura distribuída uniformemente**
```
Outliers aparecem igualmente das 7h às 22h
Normais também distribuídos igualmente
Fora do horário comercial: Normal 37% | Outlier 38%
```
Sem concentração fora do horário — o ticket não foi aberto de madrugada e ficou parado até de manhã.

**5. Dia da semana proporcional**
Sem concentração em segunda (que explicaria acúmulo de fim de semana).

---

## Diagnóstico

> Esses 2.385 tickets **são eventos reais**. São tickets que genuinamente demoraram 8–24h para receber uma primeira resposta, por qualquer razão operacional — fila, agente ocupado, escalonamento, etc. **Não são erros de dado e não são sentinels.**

O que o IQR fez foi separar em dois grupos que existem de verdade:

```
Grupo 1 — resposta rápida (mediana ~10min): 33.455 tickets (93%)
  → provavelmente automação, bot, ou resposta padrão automática

Grupo 2 — resposta lenta (mediana ~892min = 14,8h): 2.385 tickets (7%)
  → chegou num humano que estava ocupado ou fora do turno
```

A diferença de mediana entre os dois grupos é de **89x** — o que indica claramente que são **dois processos distintos de atendimento**, não uma variação normal da mesma distribuição.

---

## O que fazer com eles

| Ação | Motivo |
|---|---|
| **Não remover** | São eventos reais e representam 7% do volume |
| **Não usar a média geral** | A média de 135min é enganosa — mistura dois grupos |
| **Separar em dois segmentos** | `resposta_automatizada` (≤468min) e `resposta_humana_atrasada` (>468min) |
| **Investigar os 100%** com SLA estourado | Todo outlier estoura SLA — são candidatos a alerta automático de escalonamento |

Na prática: a métrica correta pra apresentar ao COO não é "tempo médio de resposta = 135min" nem "mediana = 11min" — é:

> *"93% dos tickets são respondidos em menos de 8h. Os 7% restantes têm mediana de 15h de espera — e 100% deles estouraram o SLA. Esse é o grupo que concentra o risco operacional."*

### 👤 User
os zeros em tempo primeira resposta minutos eh pq n respondeu ou pq foi mt rapido

### ✨ Assistant
Boa pergunta, vamos investigar diretamente.

### ✨ Assistant
A resposta é imediata e clara nos dados:

---

## São zeros **reais e intencionais** — não faltam dados

A evidência definitiva:

```
canal_entrada nos zeros:
  ChatBot → 1.790 (100%)
```

**100% dos zeros vêm de tickets abertos pelo ChatBot.** Zero é o tempo de resposta real — o bot responde instantaneamente, em menos de 1 minuto, que o sistema arredonda para 0.

---

## O que isso muda na análise

Você tem **3 grupos distintos**, não 2:

| Grupo | Volume | Tempo Resposta | Quem atende |
|---|---|---|---|
| **Bot (zero)** | 1.790 (5%) | 0 min — instantâneo | ChatBot |
| **Humano rápido** | ~31.665 (88,5%) | mediana ~10 min | Agente humano |
| **Humano lento** | 2.385 (6,7%) | mediana ~892 min | Agente humano — fila/atraso |

E olha o detalhe importante: os tickets de bot **também aparecem em todas as categorias de problema** — inclusive "Defeito" e "Onde está meu pedido?". O bot capta o ticket, mas em alguns casos depois escala pra humano (177 escalonados para N2 nos zeros).

---

## Implicação prática

> Calcular "tempo médio de primeira resposta = 135 min" **inclui os zeros do bot**, o que contamina a métrica de eficiência humana. A métrica correta é separada:
>
> - **SLA do bot:** 0 min (trivial)
> - **SLA do humano:** mediana de ~10 min para os normais, ~892 min para os atrasados

Quer que eu corrija isso no `preprocessor.py`? Seria adicionar uma coluna `canal_resposta = 'bot' | 'humano'` e separar o SLA — aí o dashboard não mistura os dois grupos.