# Antigravity: na secao de auditoria, vale colocar 39 clientes marcados com... (2026-09-07)

---
id: "1b6f59b4-f1c0-4e22-be14-ba0b1cd7389e"
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
occurred_at: "2026-09-07T14:23:35.096Z"
related: []
---

# Antigravity: na secao de auditoria, vale colocar 39 clientes marcados com... (2026-09-07)
Project: EloGroup_Bootcamp
Source: Antigravity

---

### 👤 User
na secao de auditoria, vale colocar 39 clientes marcados como "Churn" têm vendas recentes essa info? (sustentada por uma query igual as outras) ? alem disso, no plano estrategico, vale manter essa 'priorizacao de investimento em influenciadores' ? dado que pela base de marketing faz mt sentido mas pela de vendas nao tanto

### ✨ Assistant
### 1. Inclusão dos "39 clientes Churn com vendas recentes" na Seção de Auditoria

**Sim, vale muito a pena incluir.** Esse é um achado concreto de **Integridade Relacional (CRM vs. ERP)** que ilustra perfeitamente as falhas de governança de dados da empresa.

#### Evidências dos Dados (DuckDB):
- Na base de CRM (`clientes`), constam **1.796 clientes** marcados com `segmento_rfm = 'Churn'`.
- Cruzando com a base transacional (`vendas`), **exatamente 39 desses clientes** realizaram compras registradas no ERP.
- **O ponto mais crítico**: A extração do ERP se encerra em **26/01/2024**. Clientes classificados pelo CRM como "Churn" (teoricamente inativos há muito tempo) realizaram compras nos dias imediatamente anteriores ao fechamento da base:
  - `CLI-06861`: Comprou em **22/01/2024** (4 dias antes do corte).
  - `CLI-09947`: Comprou em **21/01/2024** (5 dias antes do corte).
  - `CLI-12779`: Comprou em **18/01/2024** (**22 pedidos** acumulados no ERP).
  - `CLI-07585`: Comprou em **17/01/2024** (**12 pedidos** acumulados no ERP).
  - `CLI-05277`: Possui **41 pedidos** no ERP e comprou em **28/12/2023**.

#### Impacto Analítico & de Negócio:
1. **Distorção de Campanhas**: Clientes de alto valor e recém-ativos estão sendo atingidos por réguas de reativação/descontos agressivos de churn desnecessariamente.
2. **Defasagem da Regra RFM**: O modelo de RFM no CRM não está sendo recalculado com base no extrato em tempo real do ERP.

#### Query de Sustentação:
```sql
-- src/queries/auditoria/churn_com_vendas_recentes.sql
SELECT 
    c.customer_id,
    c.segmento_rfm,
    c.total_pedidos_historico AS pedidos_declarados_crm,
    COUNT(v.order_id) AS pedidos_reais_erp,
    MAX(v.data_pedido) AS ultima_compra_erp,
    DATEDIFF('day', MAX(v.data_pedido), CAST('2024-01-26' AS DATE)) AS dias_recencia_ao_corte
FROM clientes c
INNER JOIN vendas v ON c.customer_id = v.customer_id
WHERE c.segmento_rfm = 'Churn'
GROUP BY c.customer_id, c.segmento_rfm, c.total_pedidos_historico
ORDER BY ultima_compra_erp DESC;
```

---

### 2. Vale manter a "Priorização de Investimento em Influenciadores" no Plano Estratégico?

**Recomendação de Consultoria: Não da forma como está redigida atualmente.** A iniciativa deve ser **reformulada ou substituída**.

#### O Contraste dos Dados:

| Métrica | Base Marketing (Painel Mídia) | Base Vendas (ERP Real) | Diagnóstico |
| :--- | :--- | :--- | :--- |
| **ROAS** | **7,75x** *(1º lugar absoluto)* | **0,064x** *(5º lugar)* | Sobre-atribuição severa das plataformas |
| **Receita** | R$ 217,6M declarados | R$ 2,06M faturados no ERP | 99% da receita declarada não entra no caixa |
| **Volume de Pedidos** | 15,9M conversões declaradas | 2.263 pedidos (penúltimo canal) | Baixa tração transacional real |
| **Ticket Médio** | R$ 13,65 por conversão | **R$ 912,40 líquido** *(+38% vs média de R$ 660)* | **Público High-Ticket / Premium** |
| **Margem Líquida** | — | **55,5%** (saudável) | Margem preservada |

#### Por que manter a priorização cega baseada em ROAS é um risco executivo?
1. **Armadilha de Atribuição**: Se o C-Level aprovar mais verba acreditando no ROAS de **7.75x** de Marketing, haverá frustração de caixa, pois a auditoria já revelou que o canal gerou apenas R$ 2M no ERP.
2. **Canais que sustentam o faturamento real**: **Marketplace** (R$ 3,98M) e **Google Ads** (R$ 3,64M) representam mais de **50% da receita e dos pedidos reais** do ERP.

---

### Proposta de Ajuste para o Plano Estratégico

Existem dois caminhos recomendados:

1. **Opção A (Reformulação com Foco em High-Ticket - Recomendada)**:
   - **Novo Título**: *Otimização de Campanhas de Influenciadores para Captação High-Ticket com Rastreamento por Cupom ERP*.
   - **Racional**: Não priorizar pelo volume ou ROAS de mídia, mas direcionar influenciadores nichados para produtos de alto valor agregado (onde o Ticket Médio é R$ 912 vs R$ 660), condicionando a remuneração a cupons reais validados no ERP.

2. **Opção B (Substituição por Alavanca de Maior Impacto no ERP)**:
   - Substituir pela **Otimização de Google Ads & Marketplace + Redução de Frete Perdido**, que respondem pelo maior volume de pedidos e margem bruta real da companhia.

Gostaria que eu:
1. Adicione a query e o achado dos **39 clientes Churn** na rota e na view de Auditoria?
2. Ajuste o texto e os parâmetros da iniciativa de **Influenciadores** no [`src/api/routes/roadmap.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/api/routes/roadmap.py)?

### 👤 User
acho q eu quero só tira essa recomendacao do influenciador, nao? ou ainda vale recomendar? ele gerou pouco pq investiu pouco ou realmente da pra confiar na tabela de marketing?

### ✨ Assistant
### 1. Ele gerou pouco porque investiu pouco?
**Não.** Os dados mostram que o investimento foi praticamente igual entre todos os canais:

* **Influenciadores**: Recebeu **R$ 28,06 milhões** de orçamento (13,3% do total).
* **Demais canais**: Ficaram entre **R$ 29,7M e R$ 32,6M** cada.

Ou seja, **Influenciadores não teve falta de verba**. Teve um investimento massivo de R$ 28M e, no extrato transacional do ERP, gerou apenas **2.006 pedidos aprovados** (o menor volume de todos os canais).

---

### 2. Dá para confiar na tabela de Marketing?
**Para tomada de decisão financeira de C-Level, NÃO.** 

A base de Marketing reflete o típico painel de mídia de agência com **sobre-atribuição descontrolada**:

* **Receita Declarada no Marketing**: **R$ 878,6 Milhões** (com Influenciadores sozinho declarando R$ 217,5M e ROAS de 7,75x).
* **Receita Líquida Real no ERP**: **R$ 14,2 Milhões** no total da empresa (com Influenciadores faturando apenas R$ 1,8M).
* **Conclusão**: A receita declarada em Marketing é **60x maior que o faturamento real da empresa**. Basear alocação de caixa nesse ROAS de 7,75x é uma armadilha clássica de vaidade de mídia.

---

### 3. Vale tirar essa recomendação do Plano Estratégico?

**Sim, a melhor decisão executiva é retirar.**

#### Por que é mais seguro e profissional remover?
1. **Coerência com a Auditoria**: Como você já aponta na seção de Auditoria que a Atribuição de Mídia é uma incoerência crítica (Mídia de R$ 878M vs ERP de R$ 14M), manter uma recomendação que "prioriza influenciadores pelo alto ROAS de marketing" cria uma contradição no seu próprio diagnóstico.
2. **Foco em Valor Real (R$)**: O plano estratégico de 90 dias fica muito mais robusto e defensável focando em alavancas de caixa real:
   - **Liquidação de R$ 14,7M de estoque descontinuado** (Quick Win);
   - **Economia de R$ 159k com automação de WhatsApp no atendimento** (Quick Win);
   - **Revisão de estoque crítico de R$ 7,2M** para evitar rupturas;
   - **Governança e Reconciliação CRM x ERP** (para corrigir anomalias como os 39 clientes Churn com compras recentes).

---

Se você quiser, posso:
1. **Remover a iniciativa de Influenciadores** do [`src/api/routes/roadmap.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/api/routes/roadmap.py) (ou substituí-la por uma iniciativa focada em governança/otimização de mídia baseada no ERP).
2. **Adicionar o achado dos 39 clientes Churn** na rota [`src/api/routes/audit.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/api/routes/audit.py) e criar o arquivo de query SQL correspondente.

### 👤 User
esses clientes churn, a data que eles foram marcados como churn a gente tem? ou eles podem ter sido marcados em uma data e vendas pode ter sido sei la, 1 ano antes?

### ✨ Assistant
**Excelente pergunta.** Você tocou exatamente no ponto que separa uma análise superficial de uma **auditoria de dados profunda**.

A resposta curta é: **NÃO temos uma coluna de data de quando o cliente foi marcado como Churn**, e a sua intuição está **100% correta sobre o descompasso temporal**.

---

### O que os dados realmente mostram:

1. **A tabela `clientes` é um snapshot estático (sem histórico de status)**:
   - Ela possui apenas `data_cadastro`, `total_pedidos_historico`, `ltv_acumulado` e a coluna categórica `segmento_rfm`.
   - Não há registro de log (`data_atribuicao_churn` ou `data_ultima_compra_crm`).

2. **O descompasso das janelas temporais (O "Falso Recente")**:
   - A base de **Vendas (ERP)** termina em **26 de Janeiro de 2024**.
   - A base de **Clientes (CRM)** tem cadastros até **Dezembro de 2025** e cálculos de recência projetados para o Ano Base **2026**.
   - **Resultado**: Um cliente que comprou em Janeiro de 2024 estava ativo *no final do extrato de Vendas*, mas para o CRM (olhando de 2026), ele já estava há **2 anos sem comprar**, o que explica ele estar marcado como "Churn"!

3. **A incoerência bizarra que encontramos nas datas (Anomalia Real de Auditoria)**:
   Ao cruzar as datas de compra do ERP com a data de cadastro do CRM, encontramos anomalias ainda mais graves:
   - `CLI-06861`: Data de cadastro no CRM = **26/10/2025**, mas comprou no ERP em **12/11/2023** e **22/01/2024** (*comprou quase 2 anos antes de se cadastrar!*).
   - `CLI-04614`: Data de cadastro = **02/09/2025**, mas comprou no ERP em **06/12/2023**.
   - `CLI-05277`: Data de cadastro = **28/07/2024**, mas realizou **41 compras no ERP ao longo de 2023**.

---

### Conclusão & Recomendação para a Seção de Auditoria:

Em vez de dizer apenas *"39 clientes Churn têm compras recentes"*, o apontamento de auditoria correto e tecnicamente irrefutável é:

> **"Inconsistência Cronológica e Descompasso de Snapshot CRM x ERP"**:
> * *A base de Vendas encerra em Jan/2024, enquanto o CRM foi consolidado com referência em 2026. Isso gera falsos 'Churns' (clientes que compraram no final do ERP, mas acumulam 2 anos de hiato temporal) e anomalias cadastrais onde clientes possuem histórico transacional até 2 anos antes da sua `data_cadastro`.*

Faz total sentido abordar dessa forma mais precisa e completa?

### 👤 User
nao precisa falar dessa inconsistencia pq pode ser a data entao ne? mas com relacao ao influenciadores, pode so tirar o card entao

### ✨ Assistant
Perfeito! Realizamos as decisões alinhadas:

1. **Auditoria**: Não incluímos a menção aos 39 clientes Churn, evitando ruído metodológico decorrente do descompasso de datas entre as bases.
2. **Plano Estratégico (Roadmap)**: O card de **"Priorização de Investimento em Influenciadores"** foi removido de [`src/api/routes/roadmap.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/api/routes/roadmap.py).

O plano estratégico agora conta com **6 iniciativas focadas em impacto financeiro real no ERP** (com suíte de testes 100% aprovada):
- **30 Dias (Quick Wins)**: Notificações de Status via WhatsApp/E-mail (R$ 159k) e Liquidação de Estoque Descontinuado (R$ 14,7M).
- **60 Dias**: Reativação de Clientes em Risco (R$ 650k) e Melhorias de FAQ/Páginas de Produto (R$ 78k).
- **90 Dias**: Ajuste no Mecanismo de Compras e Alertas de Ruptura (R$ 7,2M) e Governança & Unificação ERP x CRM (R$ 500k).

### 👤 User
de onde vc tirou o que é do ERP e oq é do CRM?

### ✨ Assistant
Essa distinção vem da **natureza funcional de cada base no varejo** e da arquitetura descrita no projeto (documentada em [`DEVELOPMENT.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md) e [`src/api/routes/audit.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/api/routes/audit.py)):

---

### 1. Mapeamento das 5 Bases do Case

| Arquivo Bruto | Base / Tabela | Sistema Típico de Origem | Conteúdo e Função |
| :--- | :--- | :--- | :--- |
| `Vendas.csv` | **`vendas`** | **ERP** *(Enterprise Resource Planning)* | **Transacional Financeiro**: Registra pedidos emitidos, notas, receita bruta/líquida, status de pagamento (aprovado/recusado), frete real, CMV (custo da mercadoria) e devoluções. |
| `Clientes.csv` | **`clientes`** | **CRM** *(Customer Relationship Management)* | **Cadastro e Relacionamento**: Registra o cadastro do usuário, dados demográficos (renda, gênero, idade), pontuação de fidelidade, consentimento de newsletter e a classificação RFM (*Recency, Frequency, Monetary*). |
| `Atendimento.csv` | **`atendimento`** | **SAC / Helpdesk** *(ex: Zendesk/Intercom)* | **Pós-Venda e Suporte**: Tickets de atendimento, motivo de contato, CSAT, tempo de primeira resposta e canais (ChatBot, WhatsApp, Reclame Aqui). |
| `Marketing.csv` | **`marketing`** | **Ad Servers / Painéis de Mídia** *(ex: Meta/Google Ads)* | **Aquisição de Tráfego**: Métricas declaradas pelas plataformas de anúncios (impressões, cliques, conversões e ROAS calculado por cookies/pixel). |
| `Estoque.csv` | **`estoque`** | **WMS / Suprimentos** *(Warehouse Management)* | **Logística e Armazém**: Ponto de pedido, estoque físico/reservado, lead time de fornecedores e custos de catálogo. |

---

### 2. Por que essa distinção foi importante para a análise?

No ecossistema de dados da **Vértice Retail**, as bases vieram de sistemas desacoplados (silos). Por isso:
- **`vendas` (ERP)** é a *"fonte da verdade contábil"* (dinheiro que foi faturado e pago na conta da empresa).
- **`clientes` (CRM)** é a *"visão do perfil do cliente"* (onde o cliente foi rotulado com status de fidelidade ou Churn).

Quando cruzamos as duas tabelas (`vendas` e `clientes`), encontramos o descompasso de governança: o CRM usava uma régua com janela temporal diferente da extração contábil do ERP.

### 👤 User
mas algum lugar fala que é ERP ou CRM ou da pra assumir com 100% de ctz?

### ✨ Assistant
**Não, o enunciado oficial do Bootcamp não usa as siglas "ERP" ou "CRM".** 

No documento oficial do case ([`docs/case/case_clean.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/docs/case/case_clean.md)), eles são chamados apenas de:
* **Tabela de Vendas**
* **Tabela de Clientes**
* **Tabela de Marketing**
* **Tabela de Atendimento**
* **Tabela de Estoque**

---

### Por que usamos "ERP" e "CRM" nas análises?
Os termos "ERP" e "CRM" foram usados no [`DEVELOPMENT.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md) como uma **analogia prática de consultoria** para contextualizar a dor descrita no case: *"reports are manual, data is fragmented"* (silos de dados em sistemas corporativos típicos do varejo).

---

### Recomendação para a Apresentação Executiva:
Para evitar qualquer questionamento da banca e ter **100% de precisão**, o ideal é usar a **nomenclatura funcional direta**:

| Nomenclatura Recomendada | Em vez de | Por quê? |
| :--- | :--- | :--- |
| **Base de Vendas (Transacional / Faturamento)** | *ERP* | Reflete exatamente o extrato financeiro de pedidos e pagamentos. |
| **Base de Clientes (Cadastral / Segmentação RFM)** | *CRM* | Reflete a tabela de cadastro e pontuação de clientes. |
| **Base de Marketing (Mídia)** | *Ad Servers* | Reflete as métricas de campanhas de aquisição. |
| **Base de Atendimento (Suporte / SAC)** | *Helpdesk* | Reflete o registro de chamados e CSAT. |
| **Base de Estoque (Armazém)** | *WMS* | Reflete a posição física e disponibilidade de SKUs. |

Dessa forma, o seu discurso fica **100% aderente ao enunciado do case e imune a contestações**.

### 👤 User
entao ajuste, retirando o que tiver falando de erm/crm mas mantendo a diferenciacao entre os dados

### ✨ Assistant
Ajustes concluídos com sucesso! 

Substituímos todas as referências a siglas corporativas externas (**ERP, CRM, WMS**) pela **nomenclatura funcional direta das tabelas do case**, mantendo com clareza a diferenciação e os papéis de cada fonte de dados:

---

### O que foi padronizado:

1. **Rotas e Lógica de Auditoria** ([`src/api/routes/audit.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/api/routes/audit.py)):
   - *"Extrato ERP"* ➔ **"Base Vendas (Transacional)"** (Jan/2023 a 26/Jan/2024, 27.753 pedidos).
   - *"Vínculo CRM x ERP"* ➔ **"Vínculo Clientes x Vendas"** (346 de 15.000 clientes cadastrados com compras).
   - *"Atribuição de Mídia"* ➔ Comparação entre a receita declarada de campanhas em **Marketing** vs faturamento real na tabela de **Vendas**.
   - *"Custo de Estoque x Vendas"* ➔ CMV na tabela de **Vendas** vs custo de catálogo na tabela de **Estoque**.
   - *"Tickets sem Pedido"* ➔ 65,4% dos chamados em **Atendimento** citam pedidos que não constam em **Vendas**.

2. **Plano Estratégico (Roadmap)** ([`src/api/routes/roadmap.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/api/routes/roadmap.py)):
   - Iniciativa de unificação renomeada para: *"Auditoria de Integridade & Unificação de Dados"* (reconciliação entre o histórico de Vendas e os cadastros de Clientes/Suporte).
   - Categoria ajustada para **Clientes & Vendas**.

3. **Frontend (Interface React / TypeScript)**:
   - [`AuditRelationalView.tsx`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/frontend/src/components/views/AuditRelationalView.tsx): Atualizado para exibir *"Base Vendas"* e *"Atribuição de Mídia vs. Receita Real de Vendas"*.
   - [`ExecutiveView.tsx`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/frontend/src/components/views/ExecutiveView.tsx): Badges e cards ajustados para *"Transações de Vendas"*.
   - [`CustomersView.tsx`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/frontend/src/components/views/CustomersView.tsx): Subtítulos e colunas ajustados para *"LTV Acumulado"* e *"Base total de clientes"*.
   - [`Header.tsx`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/frontend/src/components/layout/Header.tsx): Subtítulos atualizados para *"reconciliação entre Vendas, Clientes e Mídia"*.

4. **Queries SQL** ([`src/queries/auditoria/integridade_bases.sql`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/queries/auditoria/integridade_bases.sql)):
   - Comentários e CTEs ajustados para `vendas_resumo` e `clientes`.

A suíte de testes (`pytest`) foi executada e todos os **67 testes passaram com 100% de sucesso**.

### 👤 User
criou varias queries sql pra que? todas tao sendo usados na auditoria ?

### ✨ Assistant
No projeto, as queries SQL estão divididas em **três propósitos claros** (e não apenas para auditoria):

---

### 1. Queries de Auditoria & Cruzamento Relacional (Ativas na Tela de Auditoria)
Ficam em `src/queries/relacional/` e `src/queries/auditoria/`, sendo consumidas pela rota [`/api/audit/relational`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/api/routes/audit.py) e pela view [`AuditRelationalView.tsx`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/frontend/src/components/views/AuditRelationalView.tsx):
- **`mkt_vs_vendas_real.sql`**: Alimenta o gráfico de barras comparando a receita declarada pelo Marketing (R$ 878M) vs o faturamento real da tabela de Vendas (R$ 14M).
- **`estoque_vs_vendas_giro.sql`**: Cruza o giro de vendas com o estoque para identificar produtos parados vs rupturas.
- **`vendas_vs_atendimento_atrito.sql`**: Cruza pedidos com tickets de suporte e motivos de atrito.
- **`integridade_bases.sql`**: Query de auditoria dos descompassos (pedidos sem cliente cadastrado, chamados sem pedido em vendas, etc.).

---

### 2. Queries Operacionais da Aplicação (Alimentam as Telas do Dashboard)
Ficam em `src/queries/repository/` e nas pastas temáticas (`vendas/`, `clientes/`, `marketing/`, `estoque/`, `atendimento/`), consumidas pelo [`DuckDBRepository`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/infrastructure/database.py) e pelos endpoints da API:
- **Visão Executiva**: KPIs de receita líquida, margem de contribuição e decomposição de custos (`kpis_executivos_vendas.sql`).
- **Visão Clientes**: Segmentação RFM e Pareto (`segmentos_rfm.sql`, `top_estados.sql`).
- **Visão Marketing**: CAC, CTR, taxas de conversão e ROAS por canal (`eficiencia_canais.sql`).
- **Visão Suporte**: Distribuição de CSAT, tempo de resposta e cálculo de custo evitável (`causas_raiz_e_automacao.sql`).
- **Visão Estoque**: Alertas de 99 SKUs zerados e 701 SKUs críticos (`skus_criticos.sql`).

---

### 3. Ferramentas do Agente de IA Copilot & Rastreabilidade do Case
- **`src/queries/agent/*.sql`**: São as ferramentas (Tools) do Agente de IA LangGraph. Quando o usuário conversa com o Copilot no chat, o agente executa essas queries em tempo real para responder sobre estoque, vendas e devoluções.
- **`src/queries/hipotese_*/*.sql`**: Garantem a **rastreabilidade das evidências** exigida pelo regulamento do Bootcamp EloGroup (*"Traceability of Process Artifacts"*), comprovando matematicamente como chegamos nos valores do Business Case e do Roadmap de 30/60/90 dias.

---

**Resumo**: Nem todas são de auditoria — o repositório segue uma arquitetura desacoplada onde **cada card, gráfico, rota de API ou agente de IA consome seu arquivo SQL isolado**, evitando regras de negócio misturadas no código Python ou TypeScript.

### 👤 User
quero saber essas que foram criadas agora. qual o motivo de cada uma e onde apareec

### ✨ Assistant
Aqui está o mapeamento exato de **por que cada query existe e onde ela aparece no sistema**:

---

### 1. Na Tela de Auditoria Relacional ([`AuditRelationalView.tsx`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/frontend/src/components/views/AuditRelationalView.tsx))
Consumidas pela rota [`/api/audit/relational`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/api/routes/audit.py):
* **`relacional/mkt_vs_vendas_real.sql`**: Alimenta o gráfico de barras comparando a Mídia Declarada (R$ 878M) vs o Faturamento Real de Vendas (R$ 14M).
* **`relacional/estoque_vs_vendas_giro.sql`**: Cruza a velocidade de vendas com o estoque para identificar produtos parados vs rupturas.
* **`relacional/vendas_vs_atendimento_atrito.sql`**: Cruza pedidos com tickets de suporte e motivos de devolução.
* **`relacional/clientes_ciclo_atrito.sql`**: Identifica clientes que concentram chamados de suporte.

---

### 2. Nas Telas do Dashboard (Menu Lateral)
Consumidas pelos endpoints de [`analytics.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/api/routes/analytics.py):

* **Visão Executiva ([`ExecutiveView.tsx`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/frontend/src/components/views/ExecutiveView.tsx))**:
  * `vendas/decomposicao_margem.sql`: Alimenta a barra de decomposição (Receita Bruta ➔ Descontos ➔ Frete ➔ CMV ➔ Margem Líquida).
  * `vendas/margem_por_categoria.sql`: Gráfico de margem e faturamento por categoria (Moda, Beleza, Casa, etc.).
  * `vendas/top_skus_faturamento.sql`: Tabela com os produtos mais lucrativos.
  * `vendas/motivos_devolucao.sql`: Gráfico de perdas com estornos e devoluções.

* **Base de Clientes ([`CustomersView.tsx`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/frontend/src/components/views/CustomersView.tsx))**:
  * `clientes/segmentos_rfm.sql` e `distribuicao_rfm_pareto.sql`: Tabela da matriz RFM (Campeão, Fiel, Em Risco, Hibernando, Churn).
  * `clientes/top_estados.sql`: Gráfico de concentração de receita por estado (SP, RJ, MG, etc.).

* **Marketing ([`MarketingView.tsx`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/frontend/src/components/views/MarketingView.tsx))**:
  * `marketing/kpis_marketing.sql` e `eficiencia_canais.sql`: Cards de ROAS, CAC, CTR, taxa de conversão e comparativo por canal.

* **Atendimento & CX ([`SupportView.tsx`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/frontend/src/components/views/SupportView.tsx))**:
  * `atendimento/kpis_atendimento.sql` e `causas_raiz_e_automacao.sql`: Distribuição de CSAT, tempo de resposta e dimensionamento de **R$ 159k de economia com IA**.

* **Estoque & Ruptura ([`InventoryView.tsx`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/frontend/src/components/views/InventoryView.tsx))**:
  * `estoque/kpis_estoque.sql` e `skus_criticos.sql`: Diagnóstico de 99 SKUs zerados e 701 SKUs abaixo do ponto de pedido.

---

### 3. No Chat do Agente Copilot de IA ([`CopilotView.tsx`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/frontend/src/components/views/CopilotView.tsx))
Consumidas pelas ferramentas do agente em [`src/agent/tools.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/agent/tools.py):
* **`agent/inventory_health_scan.sql`**: Executada quando o Copilot faz a varredura autônoma de estoque.
* **`agent/discontinued_stranded_capital.sql`**: Simula a liquidação dos R$ 14,7M de produtos descontinuados.
* **`agent/returns_and_quality_risk.sql`**: Mapeia SKUs com alto volume de devolução por defeito.
* **`agent/sales_demand_matrix.sql`**: Calcula velocidade de vendas para sugerir reposição.

---

### 4. Queries de Rastreabilidade do Case (Process Artifacts)
Pastas `hipotese_4_atendimento/`, `hipotese_5_clientes/`, `hipotese_6_decisao_gestao/` e `auditoria/integridade_bases.sql`:
* São scripts SQL puros que **comprovam matematicamente** cada número apresentado no Business Case e no Roadmap de 30/60/90 dias, atendendo à exigência do regulamento do Bootcamp EloGroup (*"Traceability of Process Artifacts"*).