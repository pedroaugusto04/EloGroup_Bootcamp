# Antigravity: complete o pre processamenot no development.md conforme o qu... (2026-08-30)

---
type: "event"
workspace: "workspace1"
project: "elogroup-bootcamp"
status: "resolved"
tags: []
occurred_at: "2026-08-31T00:17:04Z"
---

# Antigravity: complete o pre processamenot no development.md conforme o qu... (2026-08-30)

Source: Antigravity

---

### 👤 User
complete o pre processamenot no development.md conforme o que foi feito ( basicamente padronizacao 
do tipo de dados , padronizacao de colunas numericas ecalculo de mtricas. ) quero de forma resumida, 
mas contendo e separando da melhor forma

### ✨ Assistant
A seção de pré-processamento no arquivo [DEVELOPMENT.md](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md) foi preenchida e estruturada com base nas transformações implementadas no pipeline ([preprocessor.py](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/infrastructure/preprocessor.py)).

### Resumo do que foi adicionado:
- **Organização por Dataset**: Vendas, Marketing, Estoque, Clientes e Atendimento.
- **Divisão Clara em 3 Pilares para cada dataset**:
  1. **Tipagem de dados**: conversão de datas (`datetime`), booleanos e tratamento de nulos categóricos.
  2. **Padronização de colunas numéricas**: coerção com `pd.to_numeric` e preenchimento de valores ausentes com `0.0`.
  3. **Cálculo de métricas**: criação de indicadores analíticos adicionais (ex.: margens, taxas de conversão/CTR, flags de ruptura, idade do cliente, tempo de resolução e CSAT crítico).

### 👤 User
a tabela tem nulos de idade pra justificar a imputaaco pela mediana? ou nao precisa?

### ✨ Assistant
**Não há nenhum valor nulo** na coluna `data_nascimento` (são 15.000 linhas completas e todas convertem perfeitamente para data).

Portanto:
1. **Não precisa de imputação pela mediana**: a base já veio 100% preenchida para essa coluna.
2. No código ([src/infrastructure/preprocessor.py](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/infrastructure/preprocessor.py#L133-L135)), a linha `df["idade"] = df["idade"].fillna(df["idade"].median())` funciona apenas como uma proteção defensiva de pipeline (caso no futuro entrassem dados novos com nulos), mas **para a base atual ela não alterou nenhum registro**.

Se você preferir manter a documentação estritamente fiel aos dados reais sem mencionar imputação (ou quiser simplificar o código/doc), posso ajustar o [DEVELOPMENT.md](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md).

### 👤 User
entao pode tirar essa parte do preprocessamento e do develoment.md

### ✨ Assistant
Pronto! A imputação pela mediana foi removida de ambos os arquivos:

1. **[src/infrastructure/preprocessor.py](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/infrastructure/preprocessor.py#L131-L135)**: Removida a linha `df["idade"] = df["idade"].fillna(df["idade"].median())`.
2. **[DEVELOPMENT.md](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md#L32-L36)**: Atualizado o item de métricas de Clientes para constar apenas o cálculo direto da `idade` a partir da data de nascimento.

### 👤 User
tem alguma inputacao que foi feita?

### ✨ Assistant
**Não foi necessária nenhuma imputação estatística (média, mediana ou moda)** nos dados. 

Aqui está o diagnóstico exato de todas as bases:

1. **Marketing, Estoque e Clientes**:
   - **0 valores nulos**. Todas as colunas vieram 100% preenchidas na base bruta.

2. **Vendas e Atendimento**:
   - Tinham exatamente **1 linha corrompida cada**:
     - *Vendas*: linha com `order_id = 'ORD-072219'` que continha apenas o ID e todas as outras colunas vazias (`NaN`).
     - *Atendimento*: linha com `ticket_id = 'TKT'` com todo o restante dos campos vazios.
   - **Decisão adotada**: Ambas as linhas foram **removidas / descartadas**.

3. **Tratamento defensivo no código**:
   - Métodos como `.fillna(0.0)` em colunas numéricas ou `.fillna("Outros")` foram implementados apenas como boas práticas defensivas de pipeline (para garantir robustez caso entrem novos dados no futuro), mas **nenhum dado real da base foi substituído/imputado**.

### 👤 User
qual a vantagem dos arquivos 'parquet' ?

### ✨ Assistant
O formato **Parquet** (`.parquet`) é um formato de armazenamento de dados **colunar, compactado e binário**, amplamente utilizado em Engenharia de Dados, Data Science e Analytics.

Ele substitui o `.csv` com várias vantagens fundamentais:

---

### 1. Desempenho e Velocidade de Leitura
* **CSV**: É baseado em texto e linha por linha. Toda vez que você lê um CSV, o Python/Pandas precisa ler o arquivo inteiro e tentar "adivinhar" o tipo de cada dado (string, número, data).
* **Parquet**: É binário e altamente otimizado. Ler um Parquet é tipicamente **10x a 50x mais rápido** que ler o mesmo dado em CSV.

---

### 2. Preserva os Tipos de Dados (Schema)
* No CSV, datas como `"2026-03-01"` viram apenas texto (`string`) e precisam ser convertidas novamente a cada carregamento (`pd.to_datetime`).
* No Parquet, os tipos que definimos no pré-processamento (ex.: `datetime`, `float64`, `int64`, `bool`) **ficam gravados nativamente** dentro do próprio arquivo. Ao abrir o Parquet, o Pandas já carrega tudo nos tipos corretos sem custo extra de processamento.

---

### 3. Compressão e Espaço em Disco
* O Parquet organiza os dados por colunas (em vez de linhas). Como dados da mesma coluna têm tipos e padrões semelhantes, os algoritmos de compressão (como Snappy ou Gzip) são muito mais eficientes.
* Um dataset em Parquet costuma ocupar entre **70% a 90% menos espaço** em disco que o CSV equivalente.

---

### 4. Leitura Seletiva de Colunas (*Column Pruning*)
* Se o seu dashboard ou script precisar apenas de 2 colunas de uma tabela com 30 colunas, o Parquet permite carregar **apenas essas 2 colunas da memória**, sem precisar ler o restante da tabela do disco.

---

### 📌 No contexto deste projeto:
Após rodar o pipeline de pré-processamento ([src/infrastructure/preprocessor.py](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/infrastructure/preprocessor.py)), os dados limpos, tipados e enriquecidos com métricas são salvos em `data/processed/*.parquet`. 

Assim, quando o **dashboard Streamlit** ou qualquer view do app inicia, os dados são carregados **quase que instantaneamente** e com consumo mínimo de memória.

### 👤 User
tem mais algo relevante alem dos que eu mencionei que preciso fazer no pre processamento?

### ✨ Assistant
**Para o escopo do projeto e os dados que você tem, o pré-processamento já está completo, robusto e suficiente.**

Não há duplicatas, os tipos estão consistentes, as 2 linhas corrompidas já foram tratadas, e as métricas calculadas cobrem todas as visões do dashboard (DuckDB / Streamlit).

---

### 💡 Caso queira elevar o nível técnico (pontos adicionais opcionais)

Se você quiser deixar a etapa de dados ainda mais rica para apresentação ou documentação do Bootcamp, aqui estão 3 melhorias opcionais que fazem sentido de negócio:

1. **Padronização de Strings / Texto (Strip e Uppercase/Title)**:
   * Garantir que colunas de texto categóricas (como `categoria`, `canal_venda`, `canal_entrada`, `estado`) passem por um `.str.strip()` para evitar problemas com espaços invisíveis no início/fim.

2. **Faixas / Segmentações Categóricas (Feature Engineering)**:
   * **Faixas Etárias em Clientes**: criar colunas como `faixa_etaria` (`"18-25"`, `"26-35"`, `"36-50"`, `"50+"`) para facilitar agregações demográficas diretas.
   * **Faixas de CSAT em Atendimento**: segmentar em `Promotor (4-5)`, `Neutro (3)` e `Detrator (1-2)`.

3. **Validação de Chaves Estrangeiras (Consistência Relacional)**:
   * Checar se todos os `customer_id` ou `order_id` presentes em `atendimento` e `vendas` realmente existem na tabela `clientes` (integridade referencial).

---

### 🎯 Conclusão
O que foi feito **atende 100% dos requisitos** do projeto:
- Limpeza e remoção de registros corrompidos.
- Tipagem e conversão temporal de todas as datas.
- Coerção de numéricos e cálculo de margens, KPIs e flags de negócio.
- Exportação otimizada em `.parquet`.

### 👤 User
quero fazer o do strip nas strings. deixe no codigo com comentario e no development.md

### ✨ Assistant
As alterações foram aplicadas com sucesso:

1. **Código ([src/infrastructure/preprocessor.py](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/infrastructure/preprocessor.py#L37-L43))**:
   - Implementado o método auxiliar `_strip_strings()` com docstring e comentários claros.
   - O método é invocado no início do processamento de cada uma das 5 bases (`vendas`, `marketing`, `estoque`, `clientes`, `atendimento`) para remover espaços invisíveis nas pontas das colunas textuais.

2. **Documentação ([DEVELOPMENT.md](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md#L15-L42))**:
   - Atualizado o item `3. Pré-Processamento`, documentando a etapa de **Texto / Strings** (`str.strip()`) para cada um dos datasets.

### 👤 User
ao inves de repetir o strip em cada topico deixe apenas informando no inicio

### ✨ Assistant
Ajuste realizado no [DEVELOPMENT.md](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md)!

A menção ao `str.strip()` foi centralizada no topo da seção **3. Pré-Processamento**:

> * **Padronização Geral de Strings**: Aplicado `str.strip()` em todas as colunas de texto/identificadores de todas as bases para eliminar espaços sobressalentes nas extremidades e evitar inconsistências em agrupamentos, filtros e joins.

E as repetições individuais dentro de cada dataset foram removidas, deixando a documentação mais concisa e limpa.

### 👤 User
os graficos exibidos na interface streamlit sao todos a partir das consultas sql bem definidas e testadas?

### ✨ Assistant
**Sim, 100% dos gráficos e KPIs exibidos no Streamlit vêm de consultas SQL modulares, desacopladas e padronizadas.**

Aqui está a estrutura de como tudo funciona por trás das telas:

---

### 1. Separação de Camadas (Arquitetura Limpa)
Nenhum gráfico processa regras de negócio no código visual. Toda a lógica analítica está centralizada em **arquivos `.sql` dedicados** dentro de [`src/queries/`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/queries):

* **[app/views/](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/app/views)**: Responsável apenas por renderizar os componentes visuais (Plotly e Streamlit) a partir do resultado retornado pelas queries.
* **[src/infrastructure/query_loader.py](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/infrastructure/query_loader.py)**: Carrega e injeta com segurança os filtros selecionados pelo usuário (como datas, canais, status).
* **[src/infrastructure/database.py](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/infrastructure/database.py)**: Executa as consultas ANSI SQL de alta performance em memória via **DuckDB** em cima dos arquivos `.parquet`.

---

### 2. Mapeamento dos Gráficos por Consulta SQL

Cada view consome seus respectivos arquivos SQL:

| Visão do Dashboard | Consulta SQL (`src/queries/...`) | O que alimenta na interface |
| :--- | :--- | :--- |
| **01. Visão Geral** | `visao_geral/kpis_consolidados.sql`<br>`visao_geral/evolucao_mensal.sql`<br>`visao_geral/receita_por_canal.sql`<br>`visao_geral/mix_categoria.sql`<br>`visao_geral/metodos_pagamento.sql` | Cards de KPIs (Receita, Margem, Pedidos), Gráfico de Tendência Temporal, Gráficos de Pizza/Barras por Canal, Categoria e Pagamento. |
| **02. Vendas e Margem** | `vendas/decomposicao_margem.sql`<br>`vendas/margem_por_categoria.sql`<br>`vendas/motivos_devolucao.sql`<br>`vendas/top_skus_faturamento.sql` | Gráfico Waterfall (Cascata de Margem Bruta até Margem de Contribuição), Margem % por Categoria, Motivos de Devolução e Tabela Top SKUs. |
| **03. Marketing & CAC** | `marketing/kpis_marketing.sql`<br>`marketing/eficiencia_canais.sql` | Cards de CAC, ROAS, Investimento Total, Gráfico de Dispersão e Tabela de Eficiência por Canal. |
| **04. Estoque & Ruptura** | `estoque/kpis_estoque.sql`<br>`estoque/ruptura_por_categoria.sql`<br>`estoque/skus_criticos.sql` | Cards de Ruptura, Gráfico de Taxa de Ruptura por Categoria e Tabela de SKUs Críticos (alerta de reposição). |
| **05. Clientes & RFM** | `clientes/kpis_clientes.sql`<br>`clientes/segmentos_rfm.sql`<br>`clientes/top_estados.sql`<br>`clientes/nivel_fidelidade.sql` | Distribuição de Segmentos RFM (Champions, Loyal, At Risk), Mapa/Barras de Top Estados e Nível de Fidelidade. |
| **06. Atendimento / CSAT** | `atendimento/kpis_atendimento.sql`<br>`atendimento/volume_motivos.sql`<br>`atendimento/distribuicao_csat.sql`<br>`atendimento/canais_entrada.sql`<br>`atendimento/status_chamados.sql`<br>`atendimento/amostra_recentes.sql` | CSAT Médio, Tempo de Resolução (FCR), Volume por Categoria de Problema, Distribuição de Notas e Amostra de Tickets. |

---

### 3. Testes Automatizados
A integridade dos cálculos, das views do DuckDB e das regras de negócio (margem, ruptura, idade e filtros) é validada automaticamente pela suíte de testes em [tests/test_analytics.py](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/tests/test_analytics.py).

### 👤 User
sentiment: str          # 'Positive', 'Neutral', 'Negative' pq em atributos como essse nao usar enums/consts? no python o padrao é str assim msm?

### ✨ Assistant
No Python moderno e em Engenharia de Software profissional, **o ideal é sim usar `Enum` (especialmente `StrEnum` do Python 3.11+) ou `Literal` (`typing.Literal`)**. 

O uso de `str` puro com comentário (`sentiment: str # 'Positive', 'Neutral', 'Negative'`) é um atalho comum em códigos rápidos de prototipagem, mas traz desvantagens.

---

### Por que usar `str` puro é considerado *code smell* (antipattern)?
1. **Sem autocompletion (IntelliSense)**: O desenvolvedor precisa lembrar se era `"Positive"`, `"positive"` ou `"POSITIVO"`.
2. **Sem validação estática de tipos (Mypy / Pyright)**: Se você passar `"Positve"` (com erro de digitação), o Python aceita silenciosamente e o bug só aparece em tempo de execução.
3. **Comentários ficam desatualizados**: Comentários não são executados pelo interpretador nem verificados por linters.

---

### Como o Python moderno trata isso (Padrões da Indústria)

Existem duas abordagens idiomáticas recomendadas:

#### 1. `typing.Literal` (Leve e direto para Data Science / Type Checking)
Se você quer validação de tipos em tempo de desenvolvimento e autocompletion sem precisar instanciar classes extras:

```python
from typing import Literal

SentimentType = Literal["Positive", "Neutral", "Negative"]
UrgencyType = Literal["Low", "Medium", "High", "Critical"]

@dataclass(frozen=True)
class TicketClassification:
    ticket_id: str
    customer_id: str
    sentiment: SentimentType
    urgency: UrgencyType
```

#### 2. `enum.StrEnum` (Python 3.11+ / Padrão de Engenharia de Software & DDD)
Gera constantes reais que se comportam exatamente como `str` (podem ser serializadas em JSON/DataFrames e comparadas diretamente):

```python
from enum import StrEnum

class Sentiment(StrEnum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"

class Urgency(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

@dataclass(frozen=True)
class TicketClassification:
    ticket_id: str
    customer_id: str
    sentiment: Sentiment
    urgency: Urgency
```

**Vantagem do `StrEnum`**:
```python
# Permite autocompletion seguro:
ticket = TicketClassification(..., sentiment=Sentiment.POSITIVE)

# E continua funcionando perfeitamente em comparações de string:
assert ticket.sentiment == "Positive"  # True!
```

---

### Resumo
- Em scripts descartáveis de Data Science, muitos usam `str`.
- Em projetos estruturados (Domain-Driven Design, APIs e plataformas analíticas), **o padrão ouro é usar `StrEnum` ou `Literal`**.

### 👤 User
entao padronize a aplicacao conforme o padrao sugerido

### ✨ Assistant
A padronização foi realizada com base no padrão idiomático moderno do Python 3.11+ utilizando **`enum.StrEnum`**.

### O que foi implementado em [`src/domain/models.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/domain/models.py):

1. **Enumerações Fortemente Tipadas**:
   - `Sentiment`: `POSITIVE`, `NEUTRAL`, `NEGATIVE`
   - `Urgency`: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
   - `IssueCategory`: `LOGISTICS`, `SIZE_FIT`, `DEFECT`, `FINANCIAL`, `GENERAL`
   - `ChurnRisk`: `LOW`, `MEDIUM`, `HIGH`
   - `RoadmapHorizon`: `DAYS_30`, `DAYS_60`, `DAYS_90`
   - `Pillar`: `COMMERCIAL`, `MARKETING`, `OPERATIONS`, `CUSTOMER_SERVICE`
   - `Effort`: `LOW`, `MEDIUM`, `HIGH`
   - `Speed`: `IMMEDIATE`, `MEDIUM`, `STRUCTURAL`

2. **Entidades Refatoradas**:
   - `TicketClassification` e `RoadmapInitiative` agora utilizam os Enums diretamente em seus atributos em vez de `str` genéricos com comentários.

3. **Compatibilidade Transparente**:
   - Por herdar de `StrEnum`, qualquer comparação ou serialização direta como texto (`t.sentiment == "Positive"`) continua funcionando nativamente, ao mesmo tempo em que garante autocompletion (IntelliSense) e validação estática de tipos.

### 👤 User
a receita ter caido em jan.2024 é por falta de dados ou terminou o mes e realmente caiu mesmo?

### ✨ Assistant
A aparente queda em **Jan/2024** acontece por **dois motivos principais**, sendo o corte prematuro da base o fator determinante:

---

### 1. ⚠️ Motivo Principal: O mês de Jan/2024 está incompleto na base (Truncamento de Dados)
Ao analisar o registro temporal dos dados:
* **2023**: Todos os meses possuem os 30 ou 31 dias completos.
* **Jan/2024**: A base de dados foi cortada no dia **26/01/2024 às 11:19:29** (ou seja, faltam quase 6 dias inteiros de faturamento para fechar o mês).

Quando comparamos o **mesmo período exato** (de 01 a 26 de janeiro):
* **Jan/2023 (até dia 26)**: 1.153 pedidos | **R$ 790,5 mil** (R$ 30,4 mil/dia)
* **Jan/2024 (até dia 26)**: 1.221 pedidos | **R$ 802,5 mil** (R$ 30,8 mil/dia)

👉 **Conclusão:** No mesmo período de dias, **o faturamento diário em Jan/2024 na verdade cresceu ligeiramente** em relação a Jan/2023. O total mensal parece menor apenas porque o mês não terminou.

---

### 2. 📉 Motivo Secundário: Sazonalidade Natural pós-Dezembro
* Em relação a **Nov/2023 (R$ 2,71M - Black Friday)** e **Dez/2023 (R$ 2,23M - Natal)**, janeiro é naturalmente um mês de ressaca do varejo (em Jan/2023 o mês cheio faturou R$ 936 mil).

### 👤 User
e pq março maio é maior tb?

### ✨ Assistant
Os picos de faturamento em **Março** e **Maio** acontecem por causa das **grandes datas comerciais sazonais do e-commerce brasileiro**, impulsionadas por forte injeção de campanhas de marketing:

---

### 1. Março: Semana / Mês do Consumidor
* **Data Comercial**: O **Dia do Consumidor (15 de Março)** é considerado a "Black Friday do primeiro semestre".
* **Comportamento nos Dados**:
  * O faturamento salta de ~R$ 914 mil (fevereiro) para **R$ 2,24 milhões** (+145%).
  * Os dias de maior receita concentram-se justamente entre **15 e 21 de março** (com dias faturando ~R$ 130 mil contra a média normal de R$ 30 mil).
  * As categorias líderes foram **Moda** (R$ 797k) e **Beleza** (R$ 674k), alavancadas por campanhas de liquidação e push de carrinho.

---

### 2. Maio: Dia das Mães
* **Data Comercial**: O **Dia das Mães** é historicamente a 2ª data que mais fatura no varejo de moda/lifestyle, atrás apenas do Natal/Black Friday.
* **Comportamento nos Dados**:
  * O faturamento salta de ~R$ 1,09 milhão (abril) para **R$ 2,39 milhões** (+118%).
  * O pico de compras ocorre nos dias que antecedem o 2º domingo de maio (dias **08 a 12 de maio**, faturando entre R$ 150 mil e R$ 167 mil/dia).
  * Categorias como **Beleza, Moda e Acessórios** atingem seus maiores volumes fora de novembro.

---

### 📊 O Calendário Sazonal do Negócio:
Analisando o ano completo de 2023, o negócio possui **4 grandes picos sazonais**:
1. **Março**: Semana do Consumidor (~R$ 2,24M)
2. **Maio**: Dia das Mães (~R$ 2,39M)
3. **Novembro**: Black Friday (~R$ 2,71M — *Recorde do ano*)
4. **Dezembro**: Natal / Festas (~R$ 2,23M)

Nos meses sem datas comemorativas fortes (ex.: Jan, Fev, Jun, Jul, Ago), o faturamento oscila em um platô estável de **R$ 900 mil a R$ 1,1 milhão/mês**.

### 👤 User
março costuma ter black friday na vida real?

### ✨ Assistant
No calendário do varejo brasileiro, **a Black Friday oficial acontece exclusivamente em Novembro** (na última sexta-feira do mês).

Em **Março**, o evento que acontece é o **"Dia / Semana do Consumidor"** (15 de Março).

---

### Por que se diz que Março é a *"Black Friday do 1º Semestre"*?

1. **Origem da Data**:
   * O *Dia Mundial dos Direitos do Consumidor* é 15 de março.
   * Por volta de 2014, o e-commerce brasileiro (liderado pelo Buscapé e grandes varejistas) transformou essa data institucional em uma **data promocional de peso**, justamente para suprir o "vazio" de vendas entre o pós-Carnaval e o Dia das Mães.

2. **Apelo Promocional**:
   * Como o consumidor brasileiro já conhece a dinâmica de grandes descontos da Black Friday, o marketing das marcas costuma anunciar a **Semana do Consumidor** com o mesmo nível de ofertas, queima de estoque e cupons agressivos.
   * Por isso, no jargão do e-commerce e varejo, costuma-se apelidar a Semana do Consumidor de *"a Black Friday do primeiro semestre"*.

---

### 📅 Resumo das Principais Datas do E-commerce no Brasil:
* **Março**: *Semana do Consumidor* (15/mar)
* **Maio**: *Dia das Mães* (2º domingo de maio)
* **Junho**: *Dia dos Namorados* (12/jun)
* **Novembro**: ***Black Friday*** e *Cyber Monday* (final de nov)
* **Dezembro**: *Natal* (25/dez)

### 👤 User
a margem costuma ser metade da receita? ou proximo disso?

### ✨ Assistant
**Sim, exatamente!** Na base de dados deste negócio, a margem fica **muito próxima da metade da receita (54,3% da receita líquida)**.

---

### 📊 Decomposição Financeira da Receita:

Para cada **R$ 100,00** faturados em receita líquida, a estrutura média de custos se divide assim:

```
[+] Receita Líquida:          R$ 100,00  (100%)
[-] Custo do Produto (CMV):  - R$  43,87  ( 43,9%)
[-] Custo de Frete:          - R$   1,79  (  1,8%)
-------------------------------------------------
[=] Margem de Contribuição:    R$  54,34  ( 54,3%)
```

---

### 🔍 Destaques Importantes:

1. **Consistência por Categoria**:
   * Todas as 4 categorias do negócio operam com uma margem unitária muito padronizada e equilibrada:
     * **Acessórios**: `54,5%`
     * **Moda**: `54,4%`
     * **Beleza**: `54,3%`
     * **Lifestyle**: `54,1%`

2. **Diferença por Canal**:
   * Os canais diretos / próprios (Google Ads, Instagram, Orgânico, Email) entregam margens entre **54,8% e 55,5%**.
   * O **Marketplace** tem uma margem um pouco menor (**51,5%**), devido a taxas e comissões extras da plataforma.

3. **No contexto do Varejo/E-commerce**:
   * Uma **Margem de Contribuição de ~54%** (após abater o custo da mercadoria e o frete de envio) é bastante saudável e padrão para marcas dos setores de **Moda, Vestuário e Cosméticos**, que tradicionalmente aplicam um *markup* entre 1.8x e 2.2x sobre o custo de fabricação/compra do produto.

### 👤 User
Descreva CaC vs ROAS

### ✨ Assistant
**CAC** e **ROAS** são as duas métricas mais importantes do Marketing Digital e Varejo, mas olham para o desempenho sob **perspectivas diferentes**:

---

### 1. CAC (Custo de Aquisição de Clientes)
* **O que mede**: Quanto dinheiro a empresa precisa gastar em marketing para conquistar **1 cliente (ou 1 conversão)**.
* **Fórmula**:
  $$\text{CAC} = \frac{\text{Investimento Total em Marketing}}{\text{Total de Novos Clientes (ou Conversões)}}$$
* **Unidade**: Moeda (**R$**).
* **Interpretação**: **Quanto MENOR, melhor**.
* **Exemplo**: Se você investiu R$ 10.000 em anúncios no Instagram e conseguiu 100 clientes, o seu **CAC foi de R$ 100,00 por cliente**.

---

### 2. ROAS (*Return on Ad Spend* - Retorno sobre Gasto com Anúncios)
* **O que mede**: Quantos reais a empresa faturou para **cada R$ 1,00 investido** em anúncios.
* **Fórmula**:
  $$\text{ROAS} = \frac{\text{Receita Gerada pelos Anúncios}}{\text{Investimento em Marketing}}$$
* **Unidade**: Multiplicador (**x**) ou Porcentagem (**%**).
* **Interpretação**: **Quanto MAIOR, melhor**.
* **Exemplo**: Se você investiu R$ 10.000 e esses anúncios geraram R$ 40.000 em vendas:
  $$\text{ROAS} = \frac{40.000}{10.000} = 4.0\text{x}$$
  *(Significa que para cada R$ 1 investido, voltaram R$ 4 em vendas).*

---

### ⚖️ Tabela Comparativa: CAC vs ROAS

| Característica | CAC (Custo de Aquisição) | ROAS (Retorno em Receita) |
| :--- | :--- | :--- |
| **Pergunta que responde** | *"Quanto custa trazer uma nova venda/cliente?"* | *"Quantas vezes o meu investimento voltou em vendas?"* |
| **Foco principal** | **Eficiência de Custo** (Volume / Unitário) | **Eficiência Financeira** (Faturamento / Alavancagem) |
| **Ideal de Negócio** | O mais baixo possível | O mais alto possível (geralmente > 3x no e-commerce) |
| **Depende do Ticket Médio?** | Não (conta apenas o número de clientes) | **Sim** (se o ticket for alto, o ROAS dispara mesmo com poucos clientes) |

---

### 💡 Por que analisar os dois juntos?

Imagine dois cenários com investimento de **R$ 1.000,00**:

* **Canal A (ex: Acessórios/Ticket Baixo)**:
  * Conquistou 20 clientes $\rightarrow$ **CAC = R$ 50,00** *(Ótimo CAC!)*
  * Cada um comprou R$ 60 $\rightarrow$ Receita = R$ 1.200 $\rightarrow$ **ROAS = 1.2x** *(ROAS perigoso, mal paga os custos).*

* **Canal B (ex: Moda de Luxo/Ticket Alto)**:
  * Conquistou apenas 5 clientes $\rightarrow$ **CAC = R$ 200,00** *(CAC parece caro)*
  * Cada um comprou R$ 1.200 $\rightarrow$ Receita = R$ 6.000 $\rightarrow$ **ROAS = 6.0x** *(Canal extremamente lucrativo).*

> 📌 **Resumo prático**: O **CAC** diz a facilidade de atrair pessoas; o **ROAS** diz se o dinheiro investido está compensando financeiramente.

### 👤 User
oq é ruptura nos SKUSs

### ✨ Assistant
**Ruptura de Estoque** (*Stockout*) acontece quando um produto (SKU) **não está disponível para venda ou está em nível criticamente baixo**, fazendo com que a empresa perca vendas ou deixe clientes insatisfeitos.

---

### 1. O que são os termos?
* **SKU (*Stock Keeping Unit*)**: É o código único identificador de cada produto específico no estoque (ex.: `SKU-01184` para *"Base Líquida Luxo Nude"*).
* **Ruptura**: É a falta física daquele item na prateleira ou centro de distribuição. O cliente tenta comprar no site, mas o produto aparece como **"Esgotado" / "Indisponível"**.

---

### 2. Como a Ruptura é calculada no Projeto?
Na gestão de suprimentos deste projeto, um SKU entra em **estado de ruptura** quando atende a uma destas duas condições:

$$\text{Ruptura} = (\text{Estoque Disponível} \le \text{Ponto de Pedido}) \quad\text{OU}\quad (\text{Estoque Disponível} = 0)$$

* **Ponto de Pedido**: É a quantidade mínima de segurança que o estoque precisa ter para cobrir as vendas enquanto o novo lote viaja do fornecedor até o galpão (*Lead Time de reposição*).
* Se o estoque cair abaixo dessa linha de segurança, a empresa já está em risco iminente de zerar antes do novo lote chegar.

---

### 3. Cenário Real nos Dados do Projeto:
* **Total de SKUs cadastrados**: 5.000 produtos
* **SKUs em Ruptura**: **800 produtos (16,0% do catálogo)**
  * **99 SKUs estão com estoque ZERO absoluto** (venda totalmente paralisada).
  * **701 SKUs estão abaixo do Ponto de Pedido** (precisam de ordem de compra urgente para os fornecedores).

---

### 🚨 Por que a Ruptura é um problema grave para o negócio?
1. **Perda Direta de Faturamento**: Clientes prontos para comprar encontram o item indisponível e vão para o concorrente.
2. **Desperdício de Marketing**: Se você gastou dinheiro em anúncios (Google/Instagram) para divulgar um produto que está em ruptura, você jogou o investimento no lixo.
3. **Piora na Avaliação (CSAT)**: Atrasos causados por falta de estoque geram reclamações no atendimento e cancelamento de pedidos.

### 👤 User
esse preço venda sugerido foi imputado ou veio na base?

### ✨ Assistant
**Veio diretamente na base original!** (`[BootCamp EloGroup 2026] Estoque.csv`).

Você **não precisou imputar nem criar essa coluna**. O arquivo CSV bruto já fornecia tanto o `custo_unitario` quanto o `preco_venda_sugerido` para todos os 5.000 SKUs cadastrados.

O que o pré-processamento fez em cima dessa coluna foi apenas:
1. **Tipagem/Coerção Numérica**: `pd.to_numeric(df["preco_venda_sugerido"])` para garantir que os valores fossem lidos como `float`.
2. **Cálculo de Novas Métricas**:
   * $\text{Margem Unitária Sugerida} = \text{Preço Sugerido} - \text{Custo Unitário}$
   * $\text{Markup Sugerido (\%)} = \left(\frac{\text{Margem Unitária}}{\text{Custo Unitário}}\right) \times 100$

### 👤 User
Nesse contexto, oq eh ltv medio? e segmento rfm?

### ✨ Assistant
### 1. O que é LTV Médio (*Lifetime Value*)?

* **Definição**: **LTV** (*Lifetime Value*, ou "Valor do Ciclo de Vida") é o **total de dinheiro que um cliente já gastou na sua empresa ao longo de todo o histórico de relacionamento dele**.
* **LTV Médio**: É a média do faturamento histórico acumulado por cliente:
  $$\text{LTV Médio} = \frac{\text{Soma de todo o dinheiro gasto por todos os clientes}}{\text{Número total de clientes}}$$
* **Nos dados do projeto**:
  * O **LTV Médio é de R$ 9.272,84**.
  * Isso significa que, em média, cada cliente cadastrado na base já gerou mais de R$ 9,2 mil em compras ao longo da sua vida útil com a marca.

---

### 2. O que é Segmento RFM?

**RFM** é uma das metodologias clássicas mais poderosas de CRM e Marketing para **dividir os clientes em grupos estratégicos** com base em 3 variáveis de comportamento:

1. **R — Recência (*Recency*)**: Há quantos dias o cliente fez a última compra? *(Comprou ontem ou há 1 ano?)*
2. **F — Frequência (*Frequency*)**: Com que regularidade ele compra? *(Comprou 1 vez ou 50 vezes?)*
3. **M — Valor Monetário (*Monetary*)**: Quanto dinheiro no total ele já gastou? *(Ticket / LTV alto ou baixo?)*

---

### 👥 Os Segmentos RFM na Base do Projeto:

| Segmento RFM | % da Base | LTV Médio | Quem é esse cliente? | Estratégia de Ação |
| :--- | :---: | :---: | :--- | :--- |
| 🏆 **Campeão (*Champion*)** | **8,5%** | **R$ 26.670** | Compram muito frequente (~54 pedidos), gastam alto e compraram recentemente. | Tratamento VIP, lançamentos antecipados e programas de fidelidade exclusivos. |
| 💎 **Fiel (*Loyal*)** | **17,4%** | **R$ 16.896** | Clientes assíduos (~34 pedidos) e responsivos a promoções. | Ações de *Cross-sell* e *Up-sell* para transformá-los em Campeões. |
| 🌱 **Promissor (*Promising*)** | **27,5%** | **R$ 8.077** | Compradores recentes com bom potencial de crescimento. | Campanhas de onboarding, cupons para 2ª/3ª compra e engajamento. |
| ⚠️ **Em Risco (*At Risk*)** | **21,8%** | **R$ 5.403** | Já foram bons clientes no passado, mas **faz muito tempo que não compram**. | Campanhas de reativação (*win-back*) com ofertas personalizadas antes que abandonem a marca. |
| 💤 **Hibernando / Churn** | **24,8%** | **~R$ 2.700** | Fizeram pouquíssimas compras há muito tempo e pararam de comprar. | Campanhas de baixo custo (e-mail marketing) ou descarte de base para não inflar custos de CAC. |

---

### 💡 Por que LTV e RFM são vitais juntos?
O cruzamento de **CAC com LTV** dita a saúde financeira da empresa:
* Se o seu **CAC** (custo para trazer o cliente) for **R$ 150**, e o **LTV Médio** for **R$ 9.272**, a relação **LTV / CAC é de ~60x**, mostrando que reter e fidelizar clientes é infinitamente mais rentável do que apenas buscar clientes novos todos os meses.

### 👤 User
pra essa base, quais valem mais atacar?

### ✨ Assistant
Para esta base, a análise de **Retorno sobre Esforço (ROI)** mostra com clareza quais segmentos devem ser priorizados.

Aqui está o ranking estratégico de **onde focar a energia e o orçamento de marketing/CRM**:

---

### 🥇 1º Lugar (Prioridade Máxima): Proteger e Blindar os "Fiéis" e "Campeões"
* **Quem são**: Apenas **25,8% dos clientes** (3.880 pessoas), mas representam **56,0% de toda a receita histórica da empresa** (mais de **R$ 77,9 milhões** em LTV).
* **Por que atacar**: Perder um único cliente "Campeão" custa **R$ 26,6 mil** em receita histórica (o equivalente a perder 10 clientes novos).
* **Ação Estratégica**:
  * Não use desconto agressivo (eles já compram sem precisar de cupom).
  * Ofereça **benefícios de status e relacionamento**: acesso antecipado a lançamentos (coleções novas de Moda/Beleza), atendimento prioritário e frete grátis/fidelidade.

---

### 🥈 2º Lugar (Maior Potencial de Expansão): Acelerar os "Promissores"
* **Quem são**: O maior grupo da base ativa (**27,5% dos clientes** — 4.127 pessoas) com LTV médio de **R$ 8.077** e ~16 pedidos.
* **Por que atacar**: São clientes que compraram recentemente, tiveram boa experiência, mas ainda não criaram o hábito fixo de recompra dos "Fiéis".
* **Ação Estratégica**:
  * Campanhas de **Recompra Cruzada (*Cross-sell*)**: quem comprou Moda recebe sugestão personalizada de Beleza/Acessórios.
  * Cupons com prazo de validade (ex: "15% off na sua próxima compra em até 30 dias") para encurtar o ciclo de recompra.

---

### 🥉 3º Lugar (Resgate Cirúrgico de Receita): "Em Risco"
* **Quem são**: **21,8% da base** (3.269 clientes) com LTV acumulado de **R$ 17,6 milhões**.
* **Por que atacar**: Eram clientes com frequência média de ~10 pedidos que **pararam de comprar recentemente**. Se nada for feito, eles migram definitivamente para *Churn*.
* **Ação Estratégica**:
  * Campanhas automáticas de *Win-back* (resgate) via E-mail / WhatsApp: *"Sentimos sua falta! Aqui está um cupom especial para voltar"*.
  * Pesquisa de satisfação rápida para entender se o abandono foi por problema de entrega, defeito ou preço.

---

### 🚫 Onde NÃO gastar dinheiro (Baixo Retorno): "Churn" e "Hibernando"
* **Quem são**: **24,8% da base** (3.724 clientes), mas geram apenas **7,3% da receita**.
* **Decisão de Negócio**: Não invista em mídia paga (anúncios caros no Instagram/Google) para tentar recuperar esse grupo. Use apenas **canais com custo marginal zero** (disparos pontuais de e-mail marketing).

---

### 📌 Resumo Executivo para Apresentação:
> *"Foco na regra 80/20: Proteger a fatia de **Fiéis + Campeões** (que sustentam mais da metade do negócio) e criar esteiras de automação para transformar os **Promissores** na nova geração de clientes fiéis."*

### 👤 User
oq eh nota csat

### ✨ Assistant
**CSAT** (*Customer Satisfaction Score*, ou **Índice de Satisfação do Cliente**) é a métrica padrão de mercado usada para medir **o nível de satisfação imediata do cliente** em relação a uma interação específica (como um atendimento de suporte ou a conclusão de uma compra).

---

### 1. Como funciona na prática?
Geralmente é feita aquela pergunta clássica após o fechamento do chamado:
> *"Em uma escala de 1 a 5, quão satisfeito você ficou com o atendimento recebido?"*

* **5 — Muito Satisfeito**
* **4 — Satisfeito**
* **3 — Neutro / Regular**
* **2 — Insatisfeito** *(CSAT Crítico / Detrator)*
* **1 — Muito Insatisfeito** *(CSAT Crítico / Detrator)*

---

### 2. A métrica nos dados deste Projeto:
* **Média Geral de CSAT**: **3,24** (em uma escala de 1 a 5).
  * Uma média de **3,24 é considerada baixa/mediana** para e-commerce (o benchmark saudável costuma ficar acima de 4,0).
* **Notas Críticas (Notas 1 e 2)**: Representam **21,5% de todos os chamados** (mais de 7.700 atendimentos onde o cliente saiu frustrado).

---

### 3. Onde está a "dor" do cliente (CSAT por Motivo):

Ao quebrar a nota de satisfação por categoria do problema, os dados mostram onde a operação está falhando:

| Categoria do Chamado | Volume | CSAT Médio | Diagnóstico |
| :--- | :---: | :---: | :--- |
| 🔴 **Defeito no Produto** | 6.509 | **2.82** | **Pior nota da empresa**. O produto chegou danificado ou com baixa qualidade. |
| 🟠 **Onde está meu pedido?** | 10.765 | **2.99** | **Maior volume de chamados da empresa (30%)**. Ansiedade/atraso na entrega logística. |
| 🟠 **Pagamento não aprovado** | 4.281 | **2.99** | Fricção no checkout / recusa de cartão. |
| 🟠 **Troca de Tamanho** | 5.360 | **2.99** | Problema comum de Moda/Vestuário (tabela de medidas). |
| 🟢 **Dúvida Técnica** | 5.314 | **3.83** | Atendimento consultivo funciona bem. |
| 🌟 **Elogio** | 3.611 | **4.57** | Clientes altamente satisfeitos. |

---

### 💡 Por que o CSAT é crucial para a consultoria do Case?
O CSAT baixo nos chamados de *"Onde está meu pedido?"* e *"Defeito"* explica diretamente as **taxas de devolução** e o risco de clientes fiéis virarem **"Em Risco / Churn"** no modelo RFM. Reduzir o tempo de resposta e resolver o rastreio logístico é a forma mais rápida de subir esse indicador.

### 👤 User
foi feita alguma inputacao na base pra nota csat ou todas estavam preenchidas?

### ✨ Assistant
**Não foi feita nenhuma imputação!** Todas as notas já estavam 100% preenchidas na base original.

### Detalhamento dos dados:
* **Total de registros na base bruta de Atendimento**: 35.841 linhas.
* Havia apenas **1 única linha com valor nulo** em toda a tabela, que era a linha corrompida com `ticket_id = 'TKT'` (que veio com todos os campos vazios).
* Após **remover essa linha corrompida**, restaram **35.840 atendimentos válidos**, e **todos eles (100%) já possuíam a nota de CSAT preenchida** entre 1.0 e 5.0.

Nenhuma nota precisou ser calculada, estimada ou substituída por média/mediana.