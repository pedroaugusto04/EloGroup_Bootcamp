# Guia de ajuste dos slides da apresentação executiva
**Deck base:** [`docs/slides/Vértice (1).pdf`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/docs/slides/Vértice%20(1).pdf)  
**Grupo 3:** Pedro Augusto e Pedro Lobo

Este guia contém os conteúdos e layouts para preencher os dois pontos de melhoria nos slides (no Canva, PowerPoint ou Figma).

---

## 1. Slide 08: demonstração do copiloto em produção

O slide 08 do PDF original está com o título "08 / DEMONSTRAÇÃO" e a área central vazia.

### O que inserir no slide 08

**Título:** `08 / DEMONSTRAÇÃO DO COPILOTO EM PRODUÇÃO`  
**Subtítulo:** `Do diagnóstico em DuckDB à recomendação explicável em LangGraph`

#### Elementos visuais recomendados:
1. **Lado esquerdo:** captura de tela da visão de estoque do painel React, mostrando os R$ 14,77M em descontinuados e os 701 SKUs críticos.
2. **Lado direito:** captura de tela da aba do copiloto de IA, exibindo a resposta com o cenário de queima de descontinuados e o botão "Executar Auditoria de Estoque".
3. **Card central inferior (acesso da banca):**
   - Link ativo: `https://vertice-analytics.onrender.com` (ou endereço do túnel/local)
   - QR Code para o link da aplicação.
   - Texto de apoio: *"Aplicação web unificada (FastAPI, Vite e DuckDB) rodando em container Docker com resposta em menos de 5ms e validações determinísticas de dados."*

#### Roteiro de fala sugerido (60 segundos):
> *"Para transformar a análise em ação prática, desenvolvemos a plataforma Vértice Analytics. No painel, monitoramos o capital imobilizado por categoria. Na aba do Copiloto, o gestor pode consultar diretamente o sistema: o modelo não calcula dados por conta própria; ele consulta nosso motor analítico em DuckDB, simula a liquidação com 50% de sell-through e gera um parecer técnico pronto para aprovação."*

---

## 2. Inserção do slide de business case consolidado

Recomenda-se posicionar este slide logo após o slide 11 ("Agente de Desconto") e antes do slide 12 ("Roadmap").

### Conteúdo do slide:

**Identificador:** `11.1 (ou 12) / BUSINESS CASE CONSOLIDADO`  
**Título principal:** `Retorno econômico: investimento recuperado no primeiro trimestre`  
**Subtítulo:** `O projeto se autofinancia com a liquidação de estoque descontinuado e a contenção de descontos excessivos.`

#### Estrutura em três colunas:

| Onde capturamos valor | Investimento do projeto | Métricas de retorno (C-Level) |
| :--- | :--- | :--- |
| • Liquidação de descontinuados:<br/>+R$ 4,14M líquido pós-devoluções no cenário de 50% de sell-through.<br/><br/>• Teto em descontos:<br/>+R$ 1,80M/ano de margem recuperada sem perda observada de volume.<br/><br/>• Automação de suporte N1:<br/>+R$ 55,7 mil/ano em chamados evitáveis de rastreio e dúvidas técnicas.<br/><br/>• Proteção de clientes em risco:<br/>base de retenção e monitoramento contínuo. | Investimento total (ano 1): R$ 350 mil<br/><br/>• Squad de consultoria e dados (90 dias): R$ 250k.<br/>• Infraestrutura em nuvem, APIs e mensageria (12 meses): R$ 75k.<br/>• Treinamento e gestão de mudança: R$ 25k. | • Payback estimado:<br/>2,3 meses<br/><br/>• ROI no ano 1:<br/>4,3x o capital investido<br/><br/>• Resultado econômico líquido no ano 1:<br/>+R$ 1,51M |

#### Fechamento:
> *"Mesmo em cenário conservador (captura de 30% do estoque descontinuado), o projeto mantém retorno positivo rápido e reduz a pressão sobre o capital de giro."*

---

## 3. Roteiro de fala para o slide 03 (frente de marketing)

Para apresentar a frente de marketing com precisão diante da banca, adote a seguinte narrativa:

> *"No quadrante de marketing, a base de anúncios e o ERP de vendas estão desacoplados. A plataforma de mídia reporta 38,2 milhões de conversões virtuais em 2023, enquanto a empresa faturou 76,9 mil pedidos no ano. As vendas não possuem tags UTM nem identificadores de campanha, tornando o ROAS de tela fictício. Por isso, a recomendação para 60 dias é estruturar rastreabilidade e governança no checkout antes de expandir verbas."*
