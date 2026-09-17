# Guia de Ajuste dos Slides da Apresentação Executiva
**Deck Base:** [`docs/slides/Vértice (1).pdf`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/docs/slides/Vértice%20(1).pdf)  
**Grupo 3:** Pedro Augusto & Pedro Lobo

Este guia contém os **conteúdos e layouts exatos** para você preencher os 2 pontos de melhoria nos seus slides (no Canva, PowerPoint ou Figma).

---

## 1. Slide 08 — Preenchimento da "Demonstração"

*Atualmente o Slide 08 do PDF está com o título "08 / DEMONSTRAÇÃO" e a área central em branco.*

### O que inserir no Slide 08:

**Título:** `08 / DEMONSTRAÇÃO DO COPILOTO EM PRODUÇÃO`  
**Subtítulo:** `Do diagnóstico em DuckDB à recomendação explicável em LangGraph`

#### Elementos Visuais Recomendados:
1. **Lado Esquerdo (Print 1):** Captura de tela da **Visão Executiva / Estoque** do Frontend React mostrando os R$ 14,77M em descontinuados e os 701 SKUs críticos.
2. **Lado Direito (Print 2):** Captura de tela da aba **Copiloto de IA**, mostrando a resposta do agente com a simulação do cenário de queima de descontinuados e o botão de *"Executar Auditoria de Estoque"*.
3. **Card Central Inferior (Acesso da Banca):**
   - **Link Ativo:** `https://vertice-analytics.onrender.com` (ou URL do túnel/local)
   - **QR Code** apontando para o link da aplicação.
   - **Texto de Apoio:** *"Aplicação web unificada (FastAPI + Vite + DuckDB) rodando em container Docker com resposta em <5ms e salvaguardas determinísticas contra alucinações."*

#### Roteiro de Fala da Squad (60 segundos na banca):
> *"Para transformar a análise em ação prática, desenvolvemos a plataforma Vértice Analytics. Aqui na tela vemos o dashboard monitorando o capital travado em tempo real. E na aba do Copiloto, o gestor de compras pode conversar com o agente: a inteligência não inventa números — ela consulta nosso motor determinístico em DuckDB, simula cenários de liquidação com sell-through de 50% e gera um parecer técnico pronto para aprovação."*

---

## 2. Inserção do Slide de "Business Case Consolidado"

*Recomendamos posicionar este slide logo após o Slide 11 ("Agente de Desconto") e imediatamente antes do Slide 12 ("Roadmap").*

### Conteúdo do Novo Slide:

**Numeração/Identificador:** `11.1 (ou 12) / BUSINESS CASE CONSOLIDADO`  
**Título Principal:** `Retorno econômico rápido: investimento pago antes do Dia 66.`  
**Subtítulo:** `O projeto se autofinancia no primeiro mês através da queima de estoque descontinuado e do teto de descontos.`

#### Estrutura em 3 Colunas:

| Coluna 1: Onde Capturamos Valor | Coluna 2: Investimento do Projeto | Coluna 3: Métricas de Retorno (C-Level) |
| :--- | :--- | :--- |
| **• Liquidação de Descontinuados:**<br/>+R$ 5,17M em caixa líquido (cenário 50% sell-through).<br/><br/>**• Teto de 15% em Descontos:**<br/>+R$ 1,80M/ano de margem recuperada sem perda de volume.<br/><br/>**• Automação de Suporte N1:**<br/>+R$ 238,5k/ano em chamados evitáveis.<br/><br/>**• Proteção de Clientes em Risco:**<br/>+R$ 650k em receita preservada. | **Investimento Total (Ano 1): R$ 350 mil**<br/><br/>• Squad de consultoria & dados (90 dias): R$ 250k.<br/>• Infraestrutura Cloud, APIs de IA e mensageria (12m): R$ 75k.<br/>• Treinamento e gestão de mudança: R$ 25k. | **• Payback Descontado:**<br/>**2,2 meses (66 dias)**<br/><br/>**• ROI Ano 1:**<br/>**21,5x o capital investido**<br/><br/>**• Geração Líquida Ano 1:**<br/>**+R$ 7,51 Milhões** |

#### Frase de Fechamento no Rodapé:
> *"Mesmo em cenário de estresse extremo (captura de apenas 30% do estoque descontinuado), o projeto entrega R$ 4,47M líquidos com ROI de 11,8x."*

---

## 3. Roteiro de Fala para o Slide 03 (Frente de Marketing)

*Para evitar a armadilha de tentar defender um "ROAS real calculado" diante de uma banca atenta, adote a seguinte narrativa oral no Slide 03:*

> *"No quadrante de marketing, a nossa principal descoberta não foi apenas que o ROAS declarado é ilusório, mas que **a base de marketing e o ERP de vendas estão completamente desacoplados**. A plataforma de anúncios reporta 38,2 milhões de conversões virtuais em 2023, enquanto a empresa faturou 76,9 mil pedidos no ano. Não há tags UTM nem IDs de campanha nas vendas. Isso significa que a diretoria hoje toma decisões de milhões guiando-se por um indicador de vaidade sem respaldo contábil. Nossa recomendação para 60 dias não é tentar 'otimizar canais no escuro', mas sim instituir governança e rastreabilidade no checkout antes de expandir verbas."*

