# Antigravity: o ideal na interface web é que ela exibisse cada grafico e e... (2026-09-04)

---
id: "ca6ec159-5558-4d34-a56d-03521f65a293"
type: "event"
workspace: "workspace1"
source_channel: "ai-chat"
source_system: "antigravity"
event_type: "manual_note"
project: "elogroup-bootcamp"
kind: "note"
canonical_type: "event"
importance: "low"
status: "active"
tags: []
occurred_at: "2026-09-04T20:50:31.814Z"
related: []
---

# Antigravity: o ideal na interface web é que ela exibisse cada grafico e e... (2026-09-04)
Project: EloGroup_Bootcamp
Source: Antigravity

---

### 👤 User
o ideal na interface web é que ela exibisse cada grafico e etc relacionado justamente aos pontos abordados no development.md, ao inves da forma que está, não? ou a forma atual tem mais informacoes relevantes?

### ✨ Assistant
A interface atual **já está diretamente conectada aos pontos do [DEVELOPMENT.md](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md)**, mas com uma arquitetura desenhada para **storytelling executivo e tomada de decisão**, em vez de um relatório linear de desenvolvimento.

---

### Mapeamento: `DEVELOPMENT.md` ➔ Módulos do Dashboard

| Seção no `DEVELOPMENT.md` | Onde está no Dashboard | Foco da Visualização |
| :--- | :--- | :--- |
| **Seção 2 (Outliers & Tukey IQR)** | `8. Dispersão & Outliers` | Boxplots interativos, tabelas de anomalias e quantis ($Q1, Q3, \text{IQR}$) para as 5 bases. |
| **Seção 3 (Observações por Tabela)** | `1. Visão Geral`<br>`2. Vendas & Margem`<br>`3. Marketing & Mídia`<br>`4. Estoque & Operações` | - Decomposição de margem real vs frete/estorno<br>- Eficiência de mídia declarada (ROAS/CAC)<br>- Capital imobilizado e giro de estoque |
| **Seção 5 (Hipóteses do Case)** | `5. Hipótese 4: Atendimento`<br>`6. Hipótese 5: Clientes`<br>`7. Hipótese 6: Decisão de Gestão` | - R$ 159k em custos evitáveis de SAC ("Onde está meu pedido")<br>- Concentração Pareto e clientes em risco (46,7%)<br>- R$ 14,7M travados em 207 SKUs descontinuados vs ruptura |
| **Seção 4 (Incoerências entre Bases)** | `v_10_analise_relacional.py` *(disponível no projeto)* | Diagnóstico de integridade (CRM vs ERP, datas descasadas, gap de atribuição de mídia). |

---

### Por que a estrutura atual é mais recomendada que uma cópia direta do documento?

1. **Separação entre Engenharia e Negócio (C-Level):**
   - No [DEVELOPMENT.md](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md), registramos etapas técnicas de engenharia de dados (ex.: *drop* do pedido `ORD-072219`, `_strip_strings()`, tipagens).
   - No Dashboard, o usuário/avaliador precisa ver **o impacto financeiro (R$) e as respostas das hipóteses**, sem poluição visual de etapas de ETL.

2. **Navegação por Domínio e por Hipótese:**
   - O painel está dividido em dois blocos claros:
     - **Visão Funcional** (Módulos 1 a 4): Para um gestor de Marketing, Vendas ou Supply Chain auditar sua área.
     - **Visão Estratégica / Hipóteses** (Módulos 5 a 7): Para o C-Level avaliar os gargalos transversais e direcionadores de 30/60/90 dias.

3. **Interatividade e Simulação:**
   - Em vez de um texto estático, a interface permite cruzar variáveis, filtrar categorias e inspecionar SKUs críticos e custos de automação.

---

### 💡 Oportunidade de Ajuste

Se o objetivo for dar ainda mais destaque às **análises de integridade e qualidade de dados (Seção 4)** ou ao **plano de ação executivo**:
- Podemos habilitar no menu do [app/main.py](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/app/main.py) a view [v_10_analise_relacional.py](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/app/views/v_10_analise_relacional.py) (dedicada à auditoria de consistência entre tabelas) e/ou [v_08_plano_estrategico.py](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/app/views/v_08_plano_estrategico.py) (matriz de impacto x esforço 30/60/90 dias).

### 👤 User
mas da pra deixar na mesma ordem? ou melhor manter ocmo ta?

### ✨ Assistant
**Dá perfeitamente para ordenar igual ao `DEVELOPMENT.md`**, mas a escolha ideal depende de **como você vai apresentar o projeto**.

Abaixo estão as duas opções e os prós/contras de cada uma:

---

### Opção 1: Alinhar à ordem do `DEVELOPMENT.md` (Jornada Analítica / Apresentação Técnica)
Nesta ordem, a interface conta a história do projeto do início ao fim (ideal para defender o case diante de uma banca técnica):

1. 🔍 **Qualidade & Dispersão (Outliers)** *(Seção 2 do doc - Tukey IQR)*
2. 📊 **Exploração por Tabela** *(Seção 3 do doc - Vendas, Marketing, Estoque, Clientes, SAC)*
3. ⚠️ **Integridade & Conexão entre Bases** *(Seção 4 do doc - Incoerências CRM x ERP x Mídia)*
4. 🎯 **Validação das Hipóteses de Negócio** *(Seção 5 do doc - H4 Atendimento, H5 Clientes, H6 Estoque/Gestão)*
5. 🚀 **Plano de Ação Estratégico (30/60/90 dias)** *(Recomendações executivas)*

> **Vantagem:** Quem ler o [DEVELOPMENT.md](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md) e navegar no dashboard verá **100% de paridade na sequência de raciocínio**.

---

### Opção 2: Estrutura Executiva Agrupada (Recomendada para C-Level / BI)
Em dashboards executivos, geralmente o executivo quer ver **primeiro o resultado macro de negócio**, depois as **hipóteses**, e por último as **auditorias estatísticas**.

Podemos organizar a sidebar com divisórias/seções temáticas:

* **Visão Macro & Áreas de Negócio**
  * 1. Visão Geral & Métricas
  * 2. Vendas & Margem
  * 3. Marketing & Mídia
  * 4. Estoque & Operações
* **Resolução das Hipóteses (Case Vértice)**
  * 5. Hipótese 4: Atendimento & Sintomas
  * 6. Hipótese 5: Segmentação de Clientes
  * 7. Hipótese 6: Decisão Baseada em Dados
* **Auditoria de Dados & Diagnóstico**
  * 8. Dispersão & Outliers (Tukey IQR)
  * 9. Integridade Relacional entre Bases
* **Estratégia**
  * 10. Recomendações 30/60/90 Dias

---

### Qual você prefere?
1. **Reordenar para seguir estritamente o `DEVELOPMENT.md`** (começando por Outliers/Integridade ➔ depois Áreas ➔ depois Hipóteses).
2. **Organizar em seções/grupos na barra lateral** (mantendo a navegação intuitiva de BI e incluindo a tela de Integridade e Plano Estratégico).

### 👤 User
essa visao web sera utilizada no desenvolvimenmto para auditoria e bater com a analise e etc

### ✨ Assistant
Se o objetivo principal da interface web é **auditar, checar métricas e validar cada linha do [DEVELOPMENT.md](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md)** durante o desenvolvimento, então **o ideal absoluto é espelhar exatamente a mesma ordem do documento**.

Dessa forma, enquanto você lê o documento, você consegue abrir o módulo correspondente na tela e bater número por número.

---

### Proposta de Estrutura da Interface (Espelhada no `DEVELOPMENT.md`)

```text
📁 ETAPA 2: PRÉ-PROCESSAMENTO & QUALIDADE
 └─ 1. Outliers & Dispersão (Tukey 1.5x IQR)

📁 ETAPA 3: OBSERVAÇÕES POR TABELA
 ├─ 2. Vendas & Decomposição de Margem
 ├─ 3. Marketing & Canais de Mídia
 ├─ 4. Estoque & Operações (Giro e Rupturas)
 ├─ 5. Clientes & Perfil Cadastral
 └─ 6. Atendimento & Canais de Suporte

📁 ETAPA 4: OBSERVAÇÕES GERAIS (AUDITORIA RELACIONAL)
 └─ 7. Integridade & Incoerências entre Bases (CRM x ERP x Mídia)

📁 ETAPA 5: VALIDAÇÃO DAS HIPÓTESES
 ├─ 8. Hipótese 4: Atendimento & Sintomas (Custos de IA / Onde está meu pedido)
 ├─ 9. Hipótese 5: Segmentação de Clientes (Pareto / Clientes em Risco)
 └─ 10. Hipótese 6: Decisão de Gestão & Estoque (Descontinuados vs Ruptura)

📁 ETAPA 6: PLANO ESTRATÉGICO
 └─ 11. Recomendações Executivas (30 / 60 / 90 Dias)
```

---

### O que isso traz de benefício para a auditoria:
1. **Rastreabilidade 1:1**: Cada item citado no `DEVELOPMENT.md` (ex.: R$ 14,7M em descontinuados, 46,7% em churn, R$ 159k de SAC "onde está meu pedido", 2,3% de vínculo de clientes) tem sua aba correspondente na mesma posição.
2. **Auditoria de Integridade Ativa**: A tela de *Integridade entre Bases* (`v_10_analise_relacional.py`), que detalha as anomalias da Seção 4 (mismatch de R$ 878M vs R$ 14M, datas anteriores ao cadastro, pedidos fora do ERP), fica diretamente acessível.

Quer que eu aplique essa reorganização no menu do [app/main.py](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/app/main.py) agora?

### 👤 User
sim

### ✨ Assistant
Ajuste realizado! O menu do [app/main.py](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/app/main.py) foi reorganizado para espelhar **100% da sequência de raciocínio do [DEVELOPMENT.md](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md)**:

---

### Nova Estrutura da Barra Lateral (Workbench & Auditoria)

1. **`2. Outliers & Dispersão (Tukey IQR)`**  
   ➔ Visualização dos limites de corte, quantis ($Q1, Q3, \text{IQR}$) e anomalias nas 5 bases (*Seção 2*).
2. **`3.0 Visão Geral & KPIs Macro`**  
   ➔ Métricas macro de receita, margem e evolução temporal.
3. **`3.1 Vendas & Decomposição Margem`**  
   ➔ Margem líquida vs nominal, impacto de fretes perdidos e estornos de devoluções (*Seção 3*).
4. **`3.2 Marketing & Canais de Mídia`**  
   ➔ ROAS declarado, CAC e desempenho por canal (*Seção 3*).
5. **`3.3 Estoque & Ruptura vs Excesso`**  
   ➔ SKUs críticos, giro e capital travado em produtos fora de linha (*Seção 3*).
6. **`3.4 Clientes & Perfil Cadastral`**  
   ➔ Distribuição demográfica, idade (ano-base 2026) e LTV histórico (*Seção 3*).
7. **`3.5 Atendimento & Canais de Suporte`**  
   ➔ Canais de entrada (WhatsApp/Chatbot), CSAT e motivos de contato (*Seção 3*).
8. **`4. Integridade entre Bases (Auditoria)`**  
   ➔ Incoerências relacionais: CRM x ERP, vendas sem cadastro, discrepância de mídia e correlação de custos (*Seção 4*).
9. **`5.1 Hipótese 4: Atendimento & IA`**  
   ➔ Volume de "Onde está meu pedido" e simulação de R$ 159k de economia com IA (*Seção 5*).
10. **`5.2 Hipótese 5: Segmentação de Clientes`**  
    ➔ Curva de Pareto (LTV) e diagnóstico dos 46,7% em risco/churn (*Seção 5*).
11. **`5.3 Hipótese 6: Decisão de Gestão & Estoque`**  
    ➔ R$ 14,7M imobilizados em 207 descontinuados vs 99 SKUs zerados (*Seção 5*).
12. **`6. Plano de Ação (30/60/90 Dias)`**  
    ➔ Matriz de priorização de iniciativas (impacto x esforço).

---

### Para rodar e auditar no navegador:
```bash
streamlit run app/main.py
```

### 👤 User
mas ficou graficos irrelevantes la no web? se sim pode remove-los

### ✨ Assistant
Fiz uma varredura completa em todas as telas e **removi trechos de código morto e gráficos que estavam desconectados da análise**.

---

### 🧹 O que foi limpo/removido:

1. **Cruzamentos Inconsistentes de CRM x ERP (Código Morto Removido):**
   - Nas telas de Clientes ([v_05_clientes.py](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/app/views/v_05_clientes.py) e [v_05_hipotese_clientes.py](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/app/views/v_05_hipotese_clientes.py)), havia abas secundárias e blocos de código com `return` que tentavam cruzar canais de aquisição do Marketing com LTV individual de clientes.
   - Como documentado no [DEVELOPMENT.md](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md) (*apenas 346 dos 15.000 clientes possuem vínculo com o extrato de vendas*), esse cruzamento gerava distorções. O código morto foi removido e substituído por alertas explicativos de integridade.

2. **Separação Clara entre "Perfil da Tabela" vs "Hipótese de Negócio":**
   - **`3.4 Clientes (Perfil)`**: Mantém apenas a auditoria do CRM (idade, renda, distribuição demográfica por UF e segmentos RFM).
   - **`5.2 Hipótese 5 (Segmentação)`**: Foca estritamente na curva de Pareto, concentração dos clientes Campeões/Fiéis e o diagnóstico dos **46,7% da base em risco/churn**.

---

### 📊 Resumo dos Gráficos Atuais (Todos com Vínculo Direto ao `DEVELOPMENT.md`):

| Módulo | Gráficos / Visualizações Exibidas | Ponto do `DEVELOPMENT.md` que Audita |
| :--- | :--- | :--- |
| **2. Outliers (IQR)** | Boxplots e quantis ($Q1, Q3, \text{IQR}$) das 5 bases | *Seção 2 (Tukey IQR)*: Anomalias de SAC (~26k h), descontos abusivos e SKUs travados. |
| **3.0 Visão Geral** | Evolução temporal e receita por canal | *Seção 3*: Sazonalidade (mar/mai/nov/dez) e ticket de Influenciadores (~R$ 901). |
| **3.1 Vendas & Margem** | Decomposição em cascata (CMV/Frete/Margem), devoluções e Top SKUs | *Seção 3*: Margem real vs nominal, estornos (R$ 2,5M) e frete perdido (R$ 45k). |
| **3.2 Marketing** | Investimento vs Receita por Canal e Dispersão CAC x ROAS | *Seção 3*: ROAS declarado de Influenciadores (7,75x) e matriz de eficiência. |
| **3.3 Estoque** | Taxa de Ruptura (%) e Lead Time por Categoria | *Seção 3*: 99 SKUs zerados e 701 SKUs abaixo do ponto de pedido. |
| **3.4 Clientes** | Demografia por UF, LTV por RFM e Faixas de Fidelidade | *Seção 3*: Perfil da base cadastral do CRM e idade base 2026. |
| **3.5 Atendimento** | Distribuição de canais (WhatsApp dominante) e notas CSAT | *Seção 3*: Concentração no WhatsApp e CSAT mediano (nota 3). |
| **4. Integridade** | Diagnósticos cruzados (CRM x ERP, Mídia x ERP, Estoque x Vendas) | *Seção 4*: Mismatch de R$ 878M vs R$ 14M, correlação nula de custos e vínculo de 2,3%. |
| **5.1 Hipótese 4** | Custo operacional por motivo de contato e economia com IA | *Hipótese 4*: R$ 159k em "Onde está meu pedido" e R$ 78k em Dúvidas Técnicas. |
| **5.2 Hipótese 5** | Distribuição RFM e média de pedidos no histórico | *Hipótese 5*: Volume de compras dos Campeões e 46,7% em risco/churn. |
| **5.3 Hipótese 6** | Capital travado por status do produto | *Hipótese 6*: R$ 14,7M imobilizados em 207 SKUs descontinuados. |
| **6. Plano de Ação** | Matriz Impacto x Esforço e Roadmap 30/60/90 dias | Recomendações executivas finais de gestão e IA. |

Agora, **todos os gráficos em tela têm um propósito analítico direto e auditável**.

### 👤 User
da pra evidenciar em cada tela qual/quais bases utilizou? pra nao haver confusao?

### ✨ Assistant
Pronto! Agora **cada tela exibe um banner padronizado de auditoria no topo**, detalhando exatamente a origem dos dados para evitar qualquer confusão durante o desenvolvimento:

---

### 🏷️ O que o banner no topo de cada tela informa:

1. **📁 Tabela(s) Utilizada(s):** Nome exato da view no DuckDB (`vendas`, `marketing`, `estoque`, `clientes`, `atendimento` ou cruzamento).
2. **⏱️ Escopo / Amostra:** Volume de registros e recorte temporal (ex.: *27.753 transações no ERP \| Jan/2023 a Jan/2024* vs *35.840 tickets no SAC \| Jan/2023 a Dez/2025*).
3. **📖 Ref. DEVELOPMENT.md:** Seção e tópico exato do documento [DEVELOPMENT.md](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md) que aquela tela audita.

---

### 📋 Mapeamento em Tela:

| Módulo na Interface | Tabela(s) no Banner | Escopo / Recorte Exibido |
| :--- | :--- | :--- |
| **`2. Outliers & Dispersão`** | `vendas` `atendimento` `estoque` `clientes` `marketing` | 5 Bases Sanitizadas (27.7k vendas, 35.8k tickets, 5k SKUs, 15k clientes, 3.5k campanhas) |
| **`3.0 Visão Geral`** | `vendas` | 27.753 transações (ERP) \| Jan/2023 a Jan/2024 |
| **`3.1 Vendas & Margem`** | `vendas` | 27.753 transações (Status Aprovado) \| Jan/2023 a Jan/2024 |
| **`3.2 Marketing & Mídia`** | `marketing` | 3.500 campanhas de mídia declaradas \| Jan/2023 a Dez/2025 |
| **`3.3 Estoque & Ruptura`** | `estoque` | 5.000 SKUs cadastrados (WMS) \| Snapshot Jan/2026 |
| **`3.4 Clientes & Perfil`** | `clientes` | 15.000 clientes cadastrados (CRM) \| Ano Base 2026 |
| **`3.5 Atendimento & SAC`** | `atendimento` | 35.840 chamados (Helpdesk) \| Jan/2023 a Dez/2025 |
| **`4. Integridade entre Bases`** | `vendas` `marketing` `estoque` `clientes` `atendimento` | Cruzamento Relacional Global (Auditoria de Integridade) |
| **`5.1 Hipótese 4 (Atendimento)`**| `atendimento` | 35.840 tickets de suporte (10.749 sobre rastreio) |
| **`5.2 Hipótese 5 (Clientes)`** | `clientes` | 15.000 clientes cadastrados (LTV declarado no CRM) |
| **`5.3 Hipótese 6 (Estoque)`** | `estoque` | 5.000 SKUs (207 descontinuados e 701 críticos) |
| **`6. Plano de Ação`** | `vendas` `atendimento` `estoque` `clientes` `marketing` | Síntese Executiva Transversal (30 / 60 / 90 Dias) |

Todos os testes automatizados passaram (`13 passed`).

### 👤 User
essa rupttura por categoria ta certa? beleza no topo e o resto quase nd?

### ✨ Assistant
**Sim, o dado está 100% correto matematicamente na base.** O que você observou é um dos achados mais críticos de Supply Chain do case!

---

### 🔍 O que os dados brutos revelam:

Quando olhamos para a base de estoque (5.000 SKUs):

| Categoria | Total de SKUs | 🔴 Ruptura Total (`Estoque = 0`) | ⚠️ Estoque Crítico (`<= Ponto Pedido`) | 📦 Total que Precisa Reposição | % Reposição da Categoria |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Beleza** | **1.512** | **96 SKUs** *(6,35%)* | 232 SKUs *(15,3%)* | **328 SKUs** | **21,7%** |
| **Acessórios** | 753 | **1 SKU** *(0,13%)* | 125 SKUs *(16,6%)* | **126 SKUs** | **16,7%** |
| **Lifestyle** | 1.006 | **1 SKU** *(0,10%)* | 184 SKUs *(18,3%)* | **185 SKUs** | **18,4%** |
| **Moda** | 1.729 | **1 SKU** *(0,06%)* | 160 SKUs *(9,3%)* | **161 SKUs** | **9,3%** |
| **TOTAL** | **5.000** | **99 SKUs** | **701 SKUs** | **800 SKUs** | **16,0%** |

---

### 💡 Diagnóstico de Negócio:

1. **Ruptura Imediata (Estoque Zerado = 99 SKUs):**
   - **96 de todas as 99 rupturas da empresa (97%)** estão concentradas exclusivamente na categoria **Beleza**.
   - As outras três categorias têm literalmente apenas **1 SKU zerado cada**. Por isso a barra de Beleza aparece lá no topo e as outras parecem "quase nada".

2. **Risco Iminente (Estoque Crítico = 701 SKUs):**
   - Se olharmos além do estoque zerado e considerarmos os produtos **abaixo do ponto de pedido**, o problema é geral: **Lifestyle (18,4%)**, **Acessórios (16,7%)** e **Beleza (21,7%)** têm quase 1 em cada 5 produtos sob risco iminente de desabastecimento.

---

### 🚀 Melhoria Visual Recomendada:

Em vez de plotar apenas os 99 produtos zerados (onde Beleza monopoliza a barra), podemos atualizar o gráfico para exibir **barras agrupadas ou empilhadas**:
- 🔴 **Ruptura Real (Estoque = 0)** (96 em Beleza, 1 no resto)
- 🟡 **Estoque Crítico (< Ponto de Pedido)** (232 Beleza, 184 Lifestyle, 160 Moda, 125 Acessórios)

Deseja que eu atualize o gráfico na tela `3.3 Estoque` para exibir essas duas visões juntas?

### 👤 User
sim. no development.md ja considera isso tb?

### 👤 User
sim. no development.md ja considera isso tb?

### ✨ Assistant
Ajustes aplicados no código, na interface e no documento!

---

### 1. O que foi atualizado na interface (`3.3 Estoque & Ruptura`):
- O gráfico foi reformulado para **barras empilhadas** mostrando a severidade real:
  - 🔴 **Ruptura Real (Estoque = 0)**: 96 em *Beleza* e 1 em cada uma das outras (*Acessórios, Lifestyle, Moda*).
  - 🟡 **Estoque Crítico ($\le$ Ponto de Pedido)**: 232 em *Beleza*, 184 em *Lifestyle*, 160 em *Moda* e 125 em *Acessórios*.
- Adicionada nota explicativa de auditoria abaixo do gráfico para deixar claro o motivo da concentração de Beleza nos produtos zerados vs. o risco crítico generalizado em todas as categorias.

---

### 2. O que foi atualizado no [DEVELOPMENT.md](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md):
A **Seção 3 (Estoque)** foi enriquecida com a discriminação exata:
* **99 SKUs com estoque zero e 701 SKUs operando em nível crítico** abaixo do ponto de pedido (800 SKUs no total).
* **Concentração de Ruptura Zero**: 96 dos 99 SKUs zerados (97%) concentrados em **Beleza** (6,35% do catálogo da categoria).
* **Risco Iminente Generalizado**: Os 701 SKUs críticos afetam todas as categorias (9% a 18% de cada sortimento), evidenciando que o desabastecimento é um risco transversal para toda a operação.