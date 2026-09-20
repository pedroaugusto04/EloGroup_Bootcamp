# Antigravity: Dado o contexto e as informacoes obtidas em DEVELOPMENT.md, ... (2026-09-04)

---
id: "c91549b7-8b76-446f-bc20-ca119be4ef93"
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
occurred_at: "2026-09-04T21:04:53.042Z"
related: []
---

# Antigravity: Dado o contexto e as informacoes obtidas em DEVELOPMENT.md, ... (2026-09-04)
Project: EloGroup_Bootcamp
Source: Antigravity

---

### 👤 User
Dado o contexto e as informacoes obtidas em DEVELOPMENT.md, tem mais alguma informacao relevante q eu deveria me atentar acerca da analise dessa empresa?

### ✨ Assistant
Com base no [`DEVELOPMENT.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md), no código e nas análises quantitativas do projeto, há **4 grandes dimensões de informações críticas** que merecem atenção estratégica na análise da **Vértice Retail**:

---

### 1. Preenchimento das Lacunas de Hipóteses (Seção 5 do `DEVELOPMENT.md`)

No `DEVELOPMENT.md`, as hipóteses 1 a 3 estão marcadas como `PREENCHER`. Ao cruzar os dados, os diagnósticos centrais que sustentam essas hipóteses são:

* **Hipótese 1: Erosão de Margem e Descontos Agressivos**
  * **491 pedidos com margem negativa** (descontos e frete superaram o valor da mercadoria).
  * **13,0% dos pedidos (3.609 vendas)** tiveram descontos anômalos (acima de R$ 164, atingindo pico de R$ 1.784,98).
  * Falta de travas de rentabilidade mínima na aplicação de cupons no checkout.
* **Hipótese 2: Descompasso de Canais de Aquisição vs. Qualidade do Cliente**
  * O canal **Influenciadores** apresenta o maior ticket médio real (R$ 901,91), margem de 52,3% e menor risco de churn, apesar do volume total menor de pedidos.
  * Canais pagos tradicionais (Google Ads/Marketplaces) trazem volume alto com ticket baixo e alta concentração de clientes de compra única (churn imediato).
* **Hipótese 3: Falhas Operacionais Pós-Venda e Devoluções**
  * **14,88% dos pedidos aprovados são devolvidos**, estornando **R$ 2,50 milhões** em receita líquida e gerando **R$ 45,1 mil de frete perdido direto**.
  * Principais causas: *Defeito* (associado a 18,2% dos tickets de suporte) e *Troca de Tamanho* (15% dos tickets), evidenciando falhas na ficha técnica/provador do site e no controle de qualidade de fornecedores.

---

### 2. Armadilhas e Incoerências Críticas de Dados (Data Governance)

Ao apresentar análises para o C-Level, é fundamental explicitar as limitações metodológicas identificadas em [`integridade_bases.sql`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/queries/auditoria/integridade_bases.sql) e [`v_10_analise_relacional.py`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/app/views/v_10_analise_relacional.py):

1. **Janelas Temporais Assimétricas**:
   * A base de `vendas` cobre praticamente apenas **2023** (e 26 dias de 2024), enquanto `marketing`, `atendimento` e `estoque` cobrem de **2023 a 2025**.
   * *Atenção:* Nunca compare totais brutos de marketing com vendas sem alertar para a diferença de janela temporal.
2. **Hiperconcentração de Vendas em 1 Único Cliente**:
   * **1 cliente concentra 11.282 compras (40,6% de todos os pedidos da base de vendas)**. Isso sugere um cliente institucional/B2B/revendedor ou um ID padrão de venda rápida de loja física. Se não isolado, pode distorcer métricas de dispersão e ticket médio.
3. **Mídia Declarada vs. Realidade do ERP**:
   * Marketing reporta R$ 878,6M em receita declarada por pixels/plataformas, contra R$ 14,2M de receita líquida no extrato de vendas. Trata-se de métricas de atribuição sem validação de última milha contábil.
4. **Desconexão de Custos (Estoque x CMV)**:
   * A correlação entre o custo unitário do estoque e o custo registrado na venda para o mesmo SKU é próxima de zero (`0,008`). A base de estoque representa uma **foto estática atual**, não o custo histórico por lote de compra.

---

### 3. Detalhes Operacionais Específicos por Área

* **Estoque (Concentração de Ruptura em Beleza)**:
  * Dos 99 SKUs com estoque zerado no catálogo, **96 SKUs (97%) pertencem exclusivamente à categoria Beleza**. Há um gargalo específico de fornecimento/lead time nessa categoria.
  * Em paralelo, há **R$ 14,77M parados em 207 SKUs descontinuados**, enquanto **701 SKUs** correm risco de ruptura iminente (abaixo do ponto de pedido).
* **Atendimento (Oportunidades de Redução de Custo Direto)**:
  * **44,9% dos chamados são 100% evitáveis/automatizáveis** (*Onde está meu pedido* = 30,0% e *Dúvidas Técnicas* = 14,8%), totalizando **R$ 238,5k em custos operacionais evitáveis**.
  * A anomalia de tickets com tempo de resolução de ~3 anos (26.294h) decorre de chamados abertos sem fechamento preenchido (ou com data fixa de corte `31/12/2025`).

---

### 4. Recomendações Estruturadas para a Apresentação Executiva (Roadmap 30/60/90)

| Horizonte | Iniciativa | Impacto de Negócio |
| :--- | :--- | :--- |
| **30 Dias (Quick Wins)** | • Notificações ativas de rastreio via WhatsApp/SMS.<br>• Campanha de liquidação dos 207 SKUs descontinuados.<br>• Trava de margem mínima no motor de cupons. | • Redução de até 40% nos chamados de rastreio (R$ 159k evitáveis).<br>• Liberação de até R$ 14,7M de capital imobilizado.<br>• Eliminação de pedidos com margem negativa. |
| **60 Dias (Processos)** | • Triagem via IA/NLP para dúvidas técnicas e autoatendimento.<br>• Provador virtual / guia de medidas no e-commerce.<br>• Réguas de CRM para clientes "Em Risco" (46,7% da base). | • Economia de ~R$ 78k em suporte N1.<br>• Redução de devoluções por tamanho.<br>• Proteção de recompras de alto LTV. |
| **90 Dias (Estrutural)** | • S&OP integrado e compras automatizadas no ponto de pedido.<br>• Unificação e governança de dados (MDM) integrando ERP, CRM e Mídia. | • Proteção de R$ 7,25M em risco de ruptura nos 701 SKUs.<br>• Confiabilidade integral para decisões C-Level. |

---

> [!TIP]
> Caso queira que eu elabore o texto final para preencher as seções de Hipóteses no [`DEVELOPMENT.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md) ou aprofundar algum ponto específico para a apresentação, basta me avisar!

### 👤 User
eu quero saber se tem algo alem do que foi descrito la. (obs: os dados de ticket medio e etc consideram ou desconsideram esse cliente? se desconsiderarem, continua o mesmo resultado?)

### ✨ Assistant
Aqui está a resposta detalhada para as duas perguntas:

---

### 1. Os dados de Ticket Médio consideram esse cliente? Se desconsiderarem, o resultado muda?

**Sim, as métricas atuais consideram todos os registros (incluindo o cliente `CLI-11830`).**

Porém, ao rodar a checagem isolando e **desconsiderando** esse cliente (que responde por 9.955 pedidos aprovados na base), **o resultado permanece praticamente o mesmo**:

| Métrica | Com o Top Cliente (`CLI-11830`) | Sem o Top Cliente | Variação Relativa |
| :--- | :--- | :--- | :--- |
| **Volume de Pedidos Aprovados** | 24.454 | 14.499 | -40,7% |
| **Receita Líquida Total** | R$ 16,67M | R$ 9,87M | -40,8% |
| **Ticket Médio Geral** | **R$ 681,65** | **R$ 680,52** | **-0,16%** |
| **Margem de Contribuição %** | **54,34%** | **54,33%** | **-0,01 p.p.** |
| **Taxa de Devolução** | **14,88%** | **14,87%** | **-0,01 p.p.** |
| **Desconto Médio por Pedido** | **R$ 59,30** | **R$ 59,68** | **+0,64%** |

#### E por canal de aquisição? Continua a mesma hierarquia?
**Sim, exatamente a mesma:**
* **Influenciadores**: Ticket médio de **R$ 901,91** (com) vs. **R$ 887,98** (sem) — continua sendo com folga o canal de maior valor e margem saudável (55,6%).
* **Demais canais (Google, Instagram, Marketplace, Orgânico, Email, TikTok)**: Permanecem todos agrupados na faixa de **R$ 651 a R$ 668**.

> **Por que isso acontece?**  
> As transações desse super-cliente seguem a mesma distribuição estatística (mix de produtos, cestas e faixas de preço) do restante da base, portanto **médias, taxas e proporções percentuais não são distorcidas por ele**. No entanto, métricas de **volume absoluto e contagem de clientes ativos no ERP** ficam artificialmente concentradas.

---

### 2. O que mais há de relevante para se atentar além do `DEVELOPMENT.md`?

Além dos pontos já registrados, há **5 fatores adicionais de negócio e modelagem** cruciais para a análise executiva:

---

#### A. O Super-Cliente também replica no Atendimento
O cliente `CLI-11830` não concentra apenas 40% das vendas: ele também concentra **14.355 tickets de suporte (40,0% de todos os chamados)** no [`atendimento`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/queries/atendimento/kpis_atendimento.sql), com CSAT médio de `3,22`.
* *Insight para a consultoria:* Isso confirma que o gerador de dados amarrou a volumetria de atendimento à volumetria de pedidos do ERP, reforçando a regra de que o atendimento é um **sintoma proporcional direto do volume de compras**.

---

#### B. Erosão de Margem Oculta no Canal de Marketplace
Embora o canal `Marketplace` represente o maior volume absoluto de vendas (5.315 pedidos), ele entrega a **menor margem de contribuição da empresa (51,5% vs. ~55,5% dos demais canais)**.
* *Causa:* Descontos médios maiores combinados com o custo de take-rate/comissão e fretes subsidiados.
* *Recomendação:* Revisar a política de sortimento em marketplaces, priorizando SKUs de margem bruta mais elevada para compensar o custo de canal.

---

#### C. Vale-Troca como Indicador de "Clientes Presos no Atrito"
Na análise de meios de pagamento, o **Vale-Troca** movimenta centenas de pedidos com tempo de entrega e aprovação idênticos ao Cartão e PIX.
* *Insight:* Cada compra via Vale-Troca representa um cliente que já sofreu uma devolução anterior (defeito ou tamanho) e está reinvestindo o crédito. Se essa segunda experiência falhar (por nova ruptura ou atraso), o risco de churn definitivo desse cliente é altíssimo.

---

#### D. O Perfil dos 491 Pedidos com Margem Negativa
Identificamos 491 pedidos que geraram prejuízo na venda:
* Eles não ocorrem por erro no custo do produto (CMV), mas pelo **acúmulo descontrolado de frete alto para regiões distantes com cupons de valor fixo agressivos** (ex: cupom de R$ 100+ em pedidos onde o frete custou R$ 40+).
* *Quick Win imediato:* Implementar uma **trava de checkout** que impeça a aplicação de cupom se a margem de contribuição líquida projetada do carrinho for inferior a 15%.

---

#### E. Postura Recomendada para a Apresentação Executiva (C-Level)
Em bancas e reuniões com C-Level no formato EloGroup:
1. **Não gaste tempo excessivo criticando a qualidade dos dados**: Aponte a discrepância entre ERP, CRM e Mídia em 1 slide/tópico como um diagnóstico de maturidade de governança (MDM), e em seguida apresente as decisões práticas que já podem ser tomadas com os dados válidos.
2. **Conecte sempre a ação ao impacto financeiro**:
   * Rastreio automatizado $\rightarrow$ Economia de **R$ 159,6k**.
   * Liquidação de descontinuados $\rightarrow$ Liberação de até **R$ 14,7M** de capital de giro.
   * Reposição dos 701 SKUs críticos $\rightarrow$ Proteção de **R$ 7,25M** em risco de perda de vendas.

### 👤 User
quero talvez um topico no development.md evidenciando esse cliente que foi identificado que aparece tanto em marketing e em vendas. ( quero falar bem resumidamente msm so pra dizer q vimos)

### ✨ Assistant
Atualizei o [`DEVELOPMENT.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/DEVELOPMENT.md#L162-L167) na **Seção 4 (Observações Gerais / Integridade das Bases)** com um tópico direto e sucinto:

```markdown
* **Anomalia do Super-Cliente (`CLI-11830`)**: Um único identificador concentra **11.282 compras na tabela `vendas` (40,6% de todos os pedidos / 9.955 aprovados)** e **14.355 chamados no `atendimento` (40,0% do suporte)**, apesar de ter apenas 15 compras registradas no CRM. 
  * *Impacto Metodológico*: Validamos que **desconsiderar esse cliente não altera os resultados médios** (Ticket Médio: R$ 681,65 com vs. R$ 680,52 sem; Margem %: 54,34% com vs. 54,33% sem; Devoluções: 14,88% com vs. 14,87% sem; Influenciadores segue líder isolado com R$ 888 vs. ~R$ 660 dos demais), confirmando que a distribuição dos dados foi preservada.
```

Todos os 13 testes do projeto continuam passando com sucesso.