# Antigravity: Receita Líquida por Canal de Venda Investimento vs. Receita ... (2026-09-01)

---
type: "event"
workspace: "workspace1"
project: "elogroup-bootcamp"
status: "resolved"
tags: []
occurred_at: "2026-09-01T16:16:48Z"
---

# Antigravity: Receita Líquida por Canal de Venda Investimento vs. Receita ... (2026-09-01)

Source: Antigravity

---

### 👤 User
Receita Líquida por Canal de Venda Investimento vs. Receita por Canal esses graficos se contradizem? ou nao? as bases estao adequadas?

### ✨ Assistant
Em termos de negócio e auditoria de dados, **eles medem conceitos completamente diferentes e não estão conciliados entre si**. 

---

### 1. Resumo Executivo: Eles se contradizem?

| Dimensão | [Receita Líquida por Canal de Venda](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/app/views/v_01_visao_geral.py#L80) (Visão Geral / Vendas) | [Investimento vs. Receita por Canal](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/app/views/v_03_marketing.py#L51) (Marketing) |
| :--- | :--- | :--- |
| **Origem do Dado** | Base transacional do ERP (`vendas.parquet`) | Relatórios declarados pelas plataformas de mídia (`marketing.parquet`) |
| **Janela Temporal** | **Jan/2023 a Jan/2024** (~13 meses) | **Jan/2023 a Dez/2025** (3 anos completos) |
| **Receita Total** | **R$ 18,89 milhões** (real contábil) | **R$ 878,63 milhões** (46x maior que o ERP) |
| **Investimento Total** | Custos de mercadoria/frete no pedido | **R$ 210,41 milhões** (11x a receita total da empresa) |
| **Canal Líder** | **Marketplace** (R$ 3,99M) e **Google Ads** (R$ 3,64M) | **Influenciador** (R$ 217,58M) e **TikTok Ads** (R$ 139,06M) |
| **Posição de Influenciadores** | **5º lugar** (R$ 2,06M de receita líquida) | **1º lugar absoluto** (R$ 217,58M gerados) |

---

### 2. Por que os números são tão discrepantes? (Diagnóstico de Negócio)

1. **ERP Real vs. Auto-Atribuição de Mídia (*Over-Attribution*)**:
   - **Na base de Vendas**: Mede-se o faturamento real que entrou no caixa por pedido faturado no ERP da Vértice Retail.
   - **Na base de Marketing**: São métricas reportadas pelos próprios painéis das plataformas de anúncios (Google Ads, Meta, TikTok, Agências de Influenciadores). Cada plataforma opera com janelas de conversão (view-through / click-through) e reivindica a venda para si. Se um cliente foi impactado por um post de influenciador, pesquisou no Google e comprou, múltiplos canais reivindicam 100% daquele valor nas suas ferramentas de marketing.
2. **Descompasso de Horizonte Temporal**:
   - A base de vendas cobre apenas até **26/01/2024**.
   - A base de marketing cobre campanhas até **31/12/2025**.
   - *Mesmo isolando apenas o ano de 2023*, a receita reportada no Marketing (R$ 294,2M) é 16x maior do que a receita faturada no ERP (R$ 18,1M).
3. **Escala Sintética dos Dados no Case**:
   - O investimento de marketing (R$ 210M) é uma ordem de grandeza superior a todo o faturamento da empresa (R$ 18,9M), o que aponta uma modelagem simulada das campanhas sem vínculo transacional direto (`campanha_id` $\leftrightarrow$ `order_id`).

---

### 3. As bases estão adequadas?

- **Para análise de Faturamento Real e Rentabilidade da Vértice Retail**: A base adequada e oficial é estritamente a base de **Vendas** ([`vendas.parquet`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/data/processed/vendas.parquet)). Nela estão as deduções de impostos/descontos, custos de produto, frete e estornos de devolução.
- **Para análise de Eficiência Relativa de Mídia (ROAS relativo, CTR, CAC)**: A base de **Marketing** ([`marketing.parquet`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/data/processed/marketing.parquet)) é útil para entender o funil de tráfego pago (impressões $\to$ cliques $\to$ conversões declaradas) e comparar eficiência comparativa entre plataformas, **mas não deve ser somada ou comparada diretamente em R$ absoluto com a DRE da empresa**.
- **Inconsistências Notáveis na base de Marketing**:
  - Canal **Orgânico** aparece com investimento de **R$ 29,8M** (na prática de varejo, tráfego puramente orgânico não possui verba direta de mídia paga).
  - Canal **Marketplace** aparece com investimento em mídia no mesmo formato das redes sociais, quando no e-commerce opera majoritariamente por comissão/take-rate sobre a venda.

---

### 4. Como posicionar isso para a Diretoria (C-Level)

1. **Explicitar a Nomenclatura no Dashboard**: 
   - No módulo de Visão Geral/Vendas: identificar como **"Receita Líquida Real Faturada (ERP)"**.
   - No módulo de Marketing: identificar como **"Receita Atribuída pelas Plataformas de Mídia (Ad-Reported)"**.
2. **Decisão Estratégica**:
   - Informar ao CMO/CFO que as ferramentas de mídia estão **superestimando o retorno de mídia** devido à sobreposição de atribuição e janelas de conversão infladas (sintoma clássico de governança de dados fragmentada descrita no case).

### 👤 User
analisando so os dados de vendas, , 
Receita Líquida por Canal de Venda, eh vaklido assumir que influenciador é o melhor investimento, ou nao necessariamente?

### ✨ Assistant
**Não, não é válido assumir que influenciador é o melhor investimento analisando apenas os dados de vendas.**

Olhar isoladamente a receita de vendas traz pontos cegos importantes para uma tomada de decisão executiva. Abaixo estão os 3 motivos principais:

---

### 1. A base de Vendas não possui o custo do investimento (CAC / Verba / Cachê)
Para afirmar que um canal é o "melhor investimento", é obrigatório conhecer o **Retorno sobre o Investimento (ROI)**.
- A tabela `vendas` registra a receita faturada, descontos, custo do produto e frete, mas **não registra quanto foi pago aos influenciadores** (cachês, comissões de agência, envio de mimos).
- Se a empresa gerou R$ 2,06M em vendas via influenciadores gastando R$ 200k, o investimento foi ótimo; mas se gastou R$ 1,8M em cachês, a operação foi deficitária. A base de vendas sozinha não responde a isso.

---

### 2. Em Volume Total de Receita, Influenciador é apenas o 5º colocado
Na base transacional de vendas, Influenciadores têm o **menor volume de pedidos** de toda a empresa:

| Canal de Venda | Volume de Pedidos | Receita Líquida (R$) | Ticket Médio (R$) | Margem Efetiva (%) | Taxa Devolução (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Marketplace** | 6.040 | **R$ 3,99 M** | R$ 660,03 | 50,6% | 14,95% |
| **Google Ads** | 5.504 | **R$ 3,64 M** | R$ 661,84 | 54,8% | 15,24% |
| **Instagram Ads** | 4.965 | **R$ 3,27 M** | R$ 658,77 | 54,8% | 15,07% |
| **Orgânico** | 3.246 | **R$ 2,14 M** | R$ 658,58 | 55,1% | 14,42% |
| **Influenciador** | **2.263** | **R$ 2,06 M** | **R$ 912,40** | **55,3%** | **14,98%** |
| **TikTok Ads** | 2.928 | **R$ 1,90 M** | R$ 647,23 | 55,1% | 14,34% |
| **Email Marketing** | 2.812 | **R$ 1,89 M** | R$ 672,69 | 55,3% | 14,58% |

- O canal de influenciadores representa apenas **~10,9% do faturamento total** da empresa (R$ 2,06M de R$ 18,89M).

---

### 3. O que os dados de vendas realmente revelam sobre Influenciadores?

- 🟢 **Ponto Forte — Ticket Médio Superior (+38%)**: O ticket médio dos pedidos vindos de influenciadores é de **R$ 912,40**, comparado a ~R$ 660 dos demais canais. Ou seja, quando o cliente converte por esse canal, ele compra cestas de maior valor agregado.
- 🟡 **Margem e Devolução Médias**: A margem líquida (55,3%) e a taxa de devolução (14,98%) são idênticas à média dos outros canais — não há ganho percentual desproporcional na ponta da venda.
- 🔴 **Gargalo de Escala**: Entrega menos da metade do volume de vendas gerado por canais de tração direta como Marketplace e Google Ads.

---

### Diagnóstico Consultivo para a Diretoria (C-Level)

> **Conclusão:** O canal de **Influenciadores é um canal de alta qualificação de ticket, mas não necessariamente o de melhor retorno financeiro ou maior tração.**  
> Para declarar se é o melhor canal de alocação de capital nos próximos 30/60/90 dias, a diretoria precisa cruzar o faturamento do ERP com o **contrato/custo real de cada parceiro** e avaliar se o canal possui capacidade de escalar sem degradar o CAC.

### 👤 User
mas em termos de margem influenciador eh o melhor ? ou n?

### ✨ Assistant
A resposta exata depende de **qual conceito de margem** estamos avaliando:

---

### Comparativo Direto de Margem por Canal (Base `vendas`)

| Canal | Margem Nominal (%) | Margem Efetiva Pós-Devoluções (%) | **Margem em R$ por Pedido** | Massa Total de Margem (R$) |
| :--- | :---: | :---: | :---: | :---: |
| **Influenciador** | **55,56%** | **55,28%** | 🥇 **R$ 374,24** | R$ 846,9 mil (5º) |
| **Email Marketing** | 🥇 **55,60%** | 🥇 **55,28%** | R$ 277,06 | R$ 779,1 mil (7º) |
| **Orgânico** | 55,16% | 55,06% | R$ 274,64 | R$ 891,5 mil (4º) |
| **TikTok Ads** | 55,12% | 55,15% | R$ 268,12 | R$ 785,0 mil (6º) |
| **Instagram Ads** | 55,04% | 54,83% | R$ 272,96 | R$ 1,35 milhão (3º) |
| **Google Ads** | 54,84% | 54,76% | R$ 272,31 | 🥈 **R$ 1,50 milhão (2º)** |
| **Marketplace** | 51,42% | 50,57% | R$ 249,17 | 🥇 **R$ 1,50 milhão (1º)** |

---

### 1. Em Margem Percentual (% da receita): **Empatado no topo**
- Influenciador entrega **55,28% de margem efetiva**, praticamente empatado com **Email Marketing (55,28%)**.
- Em termos percentuais, todos os canais diretos (Orgânico, TikTok, Instagram, Google) operam na faixa muito próxima de **54,8% a 55,3%**. Apenas o **Marketplace** fica abaixo (50,6%) devido ao custo logístico e comissões.

### 2. Em Margem em R$ por Pedido (Unitária): **Sim, é o Líder Absoluto** 🥇
- Cada pedido vindo de influenciador deixa **R$ 374,24 de margem limpa** no caixa da empresa (após custo de mercadoria, frete e estorno de devoluções).
- Isso é **+37% a mais de margem por transação** do que o Google Ads (R$ 272,31) ou Instagram Ads (R$ 272,96), impulsionado pelo ticket médio elevado (R$ 912 vs R$ 660).

### 3. Em Massa de Margem Total (Volume em R$ para pagar os custos fixos): **Não**
- Em dinheiro total gerado, Influenciador fica em **5º lugar** (R$ 846,9 mil de margem efetiva).
- Canais de maior volume como **Google Ads (R$ 1,50M)** e **Marketplace (R$ 1,50M)** geraram quase **80% a mais de margem total** para a Vértice Retail.

---

### 💡 Síntese Consultiva para a Diretoria

> **Influenciador é o canal mais eficiente em margem unitária por pedido (R$ 374/pedido)**, mas **não é o maior gerador de margem total da empresa** por limitação de volume.  
> A estratégia ideal é **tentar tracionar o volume desse canal sem conceder descontos excessivos**, capturando mais clientes com esse perfil de alto ticket.

### 👤 User
mas euq uero saber na relacao custo x beneficio

### ✨ Assistant
Se analisarmos a **relação custo x benefício (eficiência do capital investido)**, a resposta é:

> **SIM, Influenciador apresenta uma das melhores relações Custo x Benefício do negócio**, despontando como líder em quase todas as métricas de retorno unitário e de mídia.

Abaixo está o detalhamento desse balanço sob as 3 óticas de custo x benefício:

---

### 1. Ótica de Mídia & Aquisição (ROAS e CAC) 🥇
Na base de campanhas (`marketing`), Influenciador entrega o melhor retorno direto por real investido:

| Canal | Investimento (R$) | Receita Gerada (R$) | **ROAS (Retorno s/ Mídia)** | CAC Médio Declarado | Lucro Bruto Mkt (R$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 🥇 **Influenciador** | R$ 28,1 M | R$ 217,6 M | **7,75x** | **R$ 1,76** | **R$ 189,5 M** |
| 🥈 **TikTok Ads** | R$ 29,8 M | R$ 139,1 M | **4,67x** | R$ 1,75 | R$ 109,3 M |
| 🥉 **Instagram Ads** | R$ 30,2 M | R$ 135,9 M | **4,51x** | R$ 1,96 | R$ 105,8 M |
| **Google Ads** | R$ 30,2 M | R$ 106,6 M | **3,53x** | R$ 1,88 | R$ 76,3 M |
| **Email Marketing** | R$ 29,7 M | R$ 91,0 M | **3,07x** | R$ 1,79 | R$ 61,3 M |
| **Marketplace** | R$ 32,7 M | R$ 98,8 M | **3,02x** | R$ 1,83 | R$ 66,1 M |

* **Conclusão:** Para cada **R$ 1,00 gasto**, Influenciador retornou **R$ 7,75** — uma eficiência **72% superior** ao 2º colocado (TikTok com 4,67x) e mais que o dobro do Google Ads (3,53x).

---

### 2. Ótica Transacional (Retorno Líquido por Pedido) 🥇
Na base do ERP (`vendas`), comparando o custo operacional da venda (produto + frete + estornos) com o dinheiro que sobra no caixa:

- **Margem Líquida por Pedido**: **R$ 374,24** por compra concluída.
- **Demais Canais**: Entregam em média **R$ 270 a R$ 277** por compra.
- **Conclusão:** O custo operacional e de frete do pedido é praticamente o mesmo de qualquer outro canal, mas o **benefício (receita e margem bruta) é 37% maior**, já que o ticket médio é de R$ 912 vs R$ 660.

---

### 3. Ótica de Valor do Cliente no Tempo (LTV vs Retenção) 🥈
No cruzamento com a base de [Clientes](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/queries/clientes/qualidade_canal_aquisicao.sql):

- **Frequência de Recompra**: **21,8 pedidos por cliente** (o cliente vindo de influenciador é o mais fiel da base, empatado com TikTok).
- **LTV Médio**: **R$ 10.856,30** (segundo maior LTV, atrás apenas de TikTok com R$ 12.575).
- **Resiliência a Churn**: Apenas **39,3%** entram na faixa de risco/churn (contra **50,7%** do Google Ads e **54,3%** do Orgânico).

---

### ⚠️ O "Custo Oculto" que a Diretoria precisa considerar:
Apesar do custo x benefício financeiro imbatível, o canal tem **limitação de escala**:
1. **Dificuldade de Escalar Linearmente**: Não é possível simplesmente "dobrar o orçamento" no mesmo dia como no Google/Meta Ads; depende de prospecção, contratação, envio de produtos e agenda de criadores.
2. **Volumetria Baixa**: Trouxe apenas 2.263 pedidos no histórico, enquanto Marketplace e Google Ads trouxeram mais de 5.500 cada.

### 🎯 Recomendação Estratégica (Horizonte 30/60/90 Dias):
> **Aumentar a alocação de verba em Influenciadores e TikTok Ads**, migrando capital de canais de menor ROAS (como Email Marketing e Google Ads), estabelecendo contratos por performance (comissão por cupom) para manter o CAC baixo e alavancar o volume.

### 👤 User
mas e na base de vendas, influenciador entrega o melhor retorno proporcionalmente?

### ✨ Assistant
Olhando **exclusivamente a base de vendas**, a resposta é:

> **Em termos de Margem Percentual (Margem ÷ Receita), NÃO é o único líder — está rigorosamente empatado com os demais canais próprios (em torno de ~55,3%).**  
> No entanto, **proporcionalmente por produto ou por pedido vendido, SIM, entrega o maior retorno em R$ da empresa.**

Veja o raio-X proporcional extraído direto da base de vendas:

---

### Tabela Proporcional de Retorno (Base `vendas`)

| Canal | **Margem Efetiva (%)** <br> *(Margem ÷ Rec. Líquida)* | **Retorno s/ Custo Operacional** <br> *(Margem ÷ [CMV + Frete])* | **Margem por Unidade Vendida (R$)** | **Margem Efetiva por Pedido (R$)** | **Desconto Médio Concedido (%)** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 🥇 **Influenciador** | **55,28%** | **1,250x** | 🥇 **R$ 143,69** | 🥇 **R$ 374,24** | 8,27% (Cupons) |
| 🥇 **Email Marketing** | **55,28%** | 🥇 **1,252x** | R$ 106,41 | R$ 277,06 | 🟢 **7,20%** (Menor) |
| **TikTok Ads** | 55,15% | 1,228x | R$ 102,41 | R$ 268,12 | 8,26% |
| **Orgânico** | 55,06% | 1,230x | R$ 104,50 | R$ 274,64 | 7,71% |
| **Instagram Ads** | 54,83% | 1,224x | R$ 103,40 | R$ 272,96 | 8,00% |
| **Google Ads** | 54,76% | 1,214x | R$ 102,66 | R$ 272,31 | 8,46% |
| **Marketplace** | 🔴 50,57% | 🔴 1,059x | 🔴 R$ 96,70 | 🔴 R$ 249,17 | 7,72% |

---

### O que esses dados revelam:

1. **Margem Percentual é homogênea (~55%)**:
   - Quase todos os canais diretos entregam praticamente a mesma margem percentual (**55,2% a 55,3%**). O modelo de precificação da Vértice Retail garante a mesma taxa de lucro bruto sobre o faturamento em todos os canais próprios. Apenas o Marketplace perde eficiência (50,6%) devido ao peso do frete e comissões.

2. **Retorno sobre Custo Operacional (CMV + Frete)**:
   - Para cada **R$ 1,00 gasto na compra do produto e frete**, Influenciador gera **R$ 1,25 de margem líquida**, rigorosamente empatado com Email Marketing (**R$ 1,25**).

3. **Onde Influenciador realmente se descola (+35% de Retorno Unitário)**:
   - **R$ 143,69 de margem por peça** (vs. ~R$ 103 dos demais canais).
   - **Por que isso acontece?** Os criadores de conteúdo atraem clientes para produtos de ticket mais alto (moda e beleza *premium*), enquanto Google Ads e Marketplace atraem compras mais fragmentadas ou de menor valor.

---

### Resumo Executivo para a Diretoria:
- **Proporcionalmente à Receita (%):** Todos os canais próprios são igualmente rentáveis (~55%).
- **Proporcionalmente por Esforço de Venda / Transação:** **Influenciador entrega 37% a mais de dinheiro por pedido**, tornando cada transação individualmente muito mais rentável para a empresa.

### 👤 User
indivualmente mais rentavel, mas nao necessariaente de modo geral

### ✨ Assistant
**Exatamente! A sua leitura está 100% correta.** 

Em consultoria financeira e de varejo, esse é o clássico dilema entre **Rentabilidade Unitária vs. Massa de Margem**:

---

### 1. Empresa não paga custo fixo com "média", paga com volume total de R$
- A Vértice Retail tem custos fixos (folha de pagamento, servidores, galpão logístico, escritório).
- Mesmo sendo o canal individualmente mais "nobre" (maior ticket e maior margem por pedido), **Influenciadores geraram apenas R$ 846,9 mil de margem total** (apenas 11% do resultado da empresa).
- Em contrapartida, **Marketplace** e **Google Ads** geraram, juntos, **R$ 3,00 milhões de margem total** (quase 40% de todo o resultado da empresa).

| Canal | Margem por Pedido (Unitária) | Massa Total de Margem Gerada (R$) | Participação no Lucro Bruto da Empresa |
| :--- | :---: | :---: | :---: |
| **Marketplace** | R$ 249,17 | **R$ 1.505.009,95** | 🥇 **19,7%** |
| **Google Ads** | R$ 272,31 | **R$ 1.498.803,70** | 🥈 **19,6%** |
| **Instagram Ads** | R$ 272,96 | **R$ 1.355.229,12** | 🥉 **17,7%** |
| **Orgânico** | R$ 274,64 | **R$ 891.467,05** | 11,6% |
| **Influenciador** | 🥇 **R$ 374,24** | **R$ 846.904,93** | 🔴 **11,1%** |
| **TikTok Ads** | R$ 268,12 | **R$ 785.042,41** | 10,2% |
| **Email Marketing** | R$ 277,06 | **R$ 779.101,93** | 10,2% |

---

### 2. O Risco de Escalar Influenciadores
- Para **Influenciadores** gerarem o mesmo dinheiro no caixa que o Google Ads gera, a empresa precisaria **quase dobrar o número de pedidos desse canal** (de 2.263 para ~4.000 pedidos).
- Na prática, campanhas de influenciadores sofrem com a **lei dos retornos decrescentes**: contratar criadores menores ou fora do nicho costuma encarecer o CAC e reduzir o ticket médio, degradando essa vantagem individual.

---

### 🎯 Recomendação para o C-Level (Equilíbrio de Portfólio de Canais)

Para os próximos 30/60/90 dias, a estratégia da Vértice Retail deve trabalhar com papéis complementares:

1. **Canais Motores de Volume & Giro de Estoque (Google Ads & Marketplace)**: Manter tração para cobrir custos fixos e girar os estoques parados, focando em otimizar o frete no Marketplace.
2. **Canal de Ticket Alto & Marca (Influenciadores)**: Crescer de forma seletiva com foco em produtos de alta margem, utilizando contratos atrelados a cupom de performance para não inflar custos fixos de contratação.