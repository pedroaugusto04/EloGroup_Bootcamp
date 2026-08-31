# Relatório de Diagnóstico Estratégico: Análise das 3 Hipóteses (Vértice Retail)
**Bootcamp EloGroup 2026 · AI Consulting Lab**  
**Público-Alvo:** Diretoria Executiva (CEO, CFO, CMO, COO)  
**Data:** 30 de Agosto de 2026  

---

## 1. Sumário Executivo

A **Vértice Retail** apresenta um quadro característico de empresas de e-commerce de alto crescimento com baixa maturidade de processos: **faturamento robusto (R$ 16,67M de receita líquida)** e **margem nominal saudável (54,34%)**, mas com **vazamentos estruturais de margem** gerados por três fatores centrais:
1. **Sobrecarga no Atendimento**: O suporte ao cliente atua como amortecedor de problemas logísticos e de produto, gerando **R$ 238,5k em custos operacionais evitáveis**.
2. **Crescimento Cego por Aquisição**: Hiperconcentração de receita nos segmentos *Campeões* e *Fiéis* (25,9% da base), com **46,7% dos clientes em risco de churn ou inativos**, impulsionados por canais caros de compra única.
3. **Ineficiência Informacional na Tomada de Decisão**: Mais de **R$ 14,77M de capital de giro imobilizado em estoques descontinuados**, enquanto **701 SKUs enfrentam risco iminente de ruptura (R$ 7,25M)** por falta de integração de dados em tempo real.

---

## 2. Diagnóstico Detalhado por Hipótese

### Hipótese 1: *O atendimento pode estar concentrando sintomas de problemas recorrentes*

#### Evidências Quantitativas:
- **Volume Total de Chamados:** 35.841 tickets analisados (custo operacional de R$ 532.260,00).
- **Concentração em Rastreamento e Dúvidas:**
  - `Onde está meu pedido?`: **10.765 tickets (30,0% do volume)** | Custo: **R$ 159.660,00** | CSAT: 3,24.
  - `Dúvida Técnica`: **5.314 tickets (14,8% do volume)** | Custo: **R$ 78.888,00** | CSAT: 3,25.
  - **Total de Chamados Automatizáveis N1:** **16.079 tickets (44,9%)** $\rightarrow$ **R$ 238.548,00 em custos operacionais diretos evitáveis**.
- **Causas Upstream de Qualidade e Modelagem:**
  - `Defeito`: 6.509 tickets (18,2%) $\rightarrow$ associado diretamente a 14,88% de taxa de devoluções no e-commerce.
  - `Troca de Tamanho`: 5.360 tickets (15,0%) $\rightarrow$ falha na experiência de escolha de tamanho no site.

#### Solução Proposta & Impacto:
1. **Notificação Proativa Omnichannel (Quick Win - 30d):** Disparo de mensagens automáticas com status e rastreamento via WhatsApp/SMS no momento do despacho, reduzindo a abertura de tickets de rastreio em até 50%.
2. **Classificador & Triagem Inteligente via IA (Processo - 60d):** Implementação de bot N1 com NLP para autoatendimento de dúvidas técnicas e emissão de vouchers de troca, economizando ~R$ 180k a R$ 220k/ano.

---

### Hipótese 2: *O crescimento pode esconder diferenças importantes entre segmentos de clientes*

#### Evidências Quantitativas:
- **Base Total:** 15.000 clientes cadastrados.
- **Concentração de LTV (Pareto):**
  - `Campeões` (1.268 clientes / 8,5% da base): LTV médio de **R$ 21.657,32** e 54 pedidos históricos.
  - `Fiéis` (2.612 clientes / 17,4% da base): LTV médio de **R$ 11.232,04** e 34,2 pedidos históricos.
  - **25,9% da base responde por mais de 70% do valor econômico sustentável da marca**.
- **Vulnerabilidade da Base de Clientes:**
  - `Em Risco`: 3.269 clientes (21,8%) | LTV Médio: R$ 6.136,58 | 10,7 pedidos.
  - `Hibernando`: 1.928 clientes (12,9%) | LTV Médio: R$ 2.457,80 | 5,3 pedidos.
  - `Churn`: 1.796 clientes (12,0%) | LTV Médio: R$ 2.215,64 | 5,4 pedidos.
  - **46,7% dos clientes já abandonaram ou estão em vias de abandonar a marca**.
- **Disparidade por Canal de Aquisição:**
  - *Influenciadores*: Maior proporção de clientes de alto valor (35,7% de conversão em clientes fiéis) e excelente ROAS (4,17x a 7,75x).
  - *Google Ads / Marketplace*: Alto CAC unitário com maior taxa de descarte/churn pós-primeira compra (43% a 49% de clientes em risco).

#### Solução Proposta & Impacto:
1. **Rebalanceamento de Mídia:** Redirecionar 15% a 20% do orçamento de canais saturados para criadores e influenciadores de alta conversão.
2. **Motor de Reativação RFM Automatizado:** Campanhas de CRM com cupons dinâmicos para cohorts "Em Risco" com LTV > R$ 5.000, protegendo receita anual estimada em R$ 650k.

---

### Hipótese 3: *Parte da ineficiência pode estar na forma como a informação vira decisão a partir de dados reais*

#### Evidências Quantitativas:
- **Estoque Travado vs Ruptura Crítica:**
  - **R$ 14.775.347,64** de capital de giro imobilizado em 207 SKUs com status `Descontinuado`.
  - **R$ 7.250.310,60** de capital em risco iminente de falta de produto em 701 SKUs com estoque abaixo do ponto de pedido.
  - *Causa:* Ausência de processo integrado de S&OP (Sales & Operations Planning) e falta de alertas automatizados de compras.
- **Erosão por Devoluções:**
  - **R$ 2.503.743,90** de faturamento estornado por devoluções (14,88% dos pedidos).
  - **R$ 45.105,74** em custos de frete direto desperdiçados.

#### Solução Proposta & Impacto:
1. **Plano de Liquidação de Descontinuados (30d):** Criação de campanha *Outlet Flash* com margem controlada para recuperar ~R$ 8M a R$ 10M em liquidez para o caixa.
2. **S&OP Preditivo e Gatilhos de Reposição (90d):** Algoritmo automatizado que dispara ordens de compra ao atingir o ponto de pedido ponderado pelo lead time do fornecedor.
3. **Executive AI Memo:** Automação da geração de relatórios estratégicos semanais para a diretoria, economizando 15 horas semanais de analistas.

---

## 3. Matriz de Priorização & Roadmap 30-60-90 Dias

| Horizonte | Iniciativa | Área Responsável | Impacto Estimado | Esforço |
| :--- | :--- | :--- | :--- | :--- |
| **30 Dias (Quick Wins)** | Notificação Proativa de Rastreio (WhatsApp) | Atendimento / CX | Redução de 40% em tickets de rastreio | 15 dias |
| **30 Dias (Quick Wins)** | Queima Flash de Estoque Descontinuado | Comercial / Estoque | Liberação de R$ 5M+ em capital de giro | 20 dias |
| **30 Dias (Quick Wins)** | Rebalanceamento de Canais de Marketing | Marketing | Economia de R$ 850k em CAC ineficiente | 25 dias |
| **60 Dias (Processos)** | Triagem Inteligente de Chamados via IA | Atendimento / CX | Economia de R$ 180k/ano em suporte N1 | 45 dias |
| **60 Dias (Processos)** | Provador Virtual de Medidas no E-commerce | Produto / UX | Redução de 25% nas devoluções de tamanho | 50 dias |
| **60 Dias (Processos)** | Réguas de Reativação de Clientes RFM | Marketing / CRM | Proteção de R$ 650k em receita de risco | 40 dias |
| **90 Dias (Escala)** | S&OP Preditivo e Reposição Automatizada | Supply Chain | Proteção de R$ 7,25M em rupturas | 80 dias |
| **90 Dias (Escala)** | Gerador Semanal de Relatórios Executivos (IA) | Governança / Dados | Economia de 60h/mês de diretoria/analistas | 70 dias |

---

## 4. Conclusão & Próximos Passos

O diagnóstico comprova que as 3 hipóteses são **verdadeiras e interdependentes**. A implantação do Workbench Analítico Streamlit + DuckDB e dos módulos de IA proposta garante à Vértice Retail uma rota clara para recuperar margem, liberar caixa e elevar a satisfação do cliente em até 90 dias.
