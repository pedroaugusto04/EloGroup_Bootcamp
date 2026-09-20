# Mapa de Entregáveis e Guia de Acesso — Vértice Analytics
**Bootcamp EloGroup 2026 · Squad Grupo 14**  
**Autores:** Pedro Augusto Duarte e Pedro Lobo  

---

## 1. Links Oficiais do Projeto

- **Aplicação Web em Produção (Online & Interativa):**  
  **[https://pedro-duarte.ddns.net/vertice/](https://pedro-duarte.ddns.net/vertice/)**  
  *(Todas as análises, dashboards gerenciais, visualizadores de relatórios e o Agente Copiloto de IA estão disponíveis publicamente para teste imediato)*

- **Repositório de Código no GitHub:**  
  **[https://github.com/pedroaugusto04/EloGroup_Bootcamp](https://github.com/pedroaugusto04/EloGroup_Bootcamp)**  

- **Pacote Consolidado de Documentos (Local):**  
  `/home/pedroduarte/Downloads/Bootcamp_Documentos_Grupo14/`

---

## 2. Matriz de Correspondência dos Entregáveis Oficiais do Case

A tabela a seguir correlaciona cada exigência formal do case (*`docs/case/[BootCamp EloGroup 2026] Case.html`*, Seções 7 e 9) com a localização exata de seus respectivos arquivos e telas na aplicação web:

| # | Entregável Oficial (Case) | Onde Encontrar no Repositório | Onde Encontrar no Pacote Grupo 14 (`Downloads`) | Como Visualizar / Testar na Aplicação Web |
|---|---|---|---|---|
| **1** | **Diagnóstico Executivo & Árvore de Hipóteses** | [`docs/entregaveis/01_relatorio_diagnostico_estrategico.md`](docs/entregaveis/01_relatorio_diagnostico_estrategico.md)<br>[`docs/assets/arvore_hipoteses.svg`](docs/assets/arvore_hipoteses.svg) | `Relatorio_Diagnostico_Estrategico.md`<br>`assets/arvore_hipoteses.svg` | **Aba "Entregáveis"** (Doc 01 com Árvore de Hipóteses renderizada) e **Aba "Visão Executiva"** |
| **2** | **Business Case & Modelagem Financeira** | [`docs/entregaveis/02_business_case_modelagem_financeira.md`](docs/entregaveis/02_business_case_modelagem_financeira.md) | `Business_Case_Modelagem_Financeira.md` | **Aba "Entregáveis"** (Doc 02 com matriz de sensibilidade 25%-100%, ROI 4,3x e Payback 2,3 meses) |
| **3** | **Auditoria de Dados & Memória de Cálculo** | [`docs/entregaveis/03_auditoria_dados_memoria_calculo.md`](docs/entregaveis/03_auditoria_dados_memoria_calculo.md) | `Dados_Auditoria.md` | **Aba "Auditoria Relacional"** (7 inconsistências relacionais interativas) e **Aba "Entregáveis"** (Doc 03) |
| **4** | **Arquitetura de IA & Governança Técnica** | [`docs/entregaveis/04_arquitetura_ia_governanca.md`](docs/entregaveis/04_arquitetura_ia_governanca.md) | `Arquitetura_IA_Governanca.md` | **Aba "Entregáveis"** (Doc 04 com diagrama de 4 camadas, salvaguardas anti-alucinação e queries SQL) |
| **5** | **Racional Metodológico de Desenvolvimento** | [`docs/entregaveis/DEVELOPMENT.md`](docs/entregaveis/DEVELOPMENT.md)<br>[`docs/profiling/*.html`](docs/profiling/) *(5 bases)* | `Racional-Metodológico-Desenvolvimento.md` | **Aba "Entregáveis"** (Doc 05) e documentação de profiling das 5 bases |
| **6** | **Roadmap de Implementação (30-60-90 Dias)** | [`docs/assets/RoadMap.png`](docs/assets/RoadMap.png) | `RoadMap/RoadMap.png` | **Aba "Roadmap"** (Gantt interativo, detalhamento de squads, iniciativas por fase e métricas de acompanhamento) |
| **7** | **Dashboard de Gestão Executiva** | Código em `frontend/` e `src/api/` | Código e documentações | **Aplicação Web:**<br>• `/?view=executive` (Vendas e Margem)<br>• `/?view=inventory` (Ruptura e Estoque)<br>• `/?view=marketing` (Canais de Aquisição)<br>• `/?view=customers` (Segmentação RFM)<br>• `/?view=support` (CX e Atendimento)<br>• `/?view=outliers` (Dispersão de Preços) |
| **8** | **Protótipo / Agente de IA em Produção** | `src/agent/` e `src/api/routes/copilot.py` | Código e notas das sessões | **Aba "Copiloto de IA" (`/?view=copilot`)**:<br>Agente inteligente ReAct acoplado ao DuckDB para auditorias e simulações com travas determinísticas |
| **9** | **Rastreabilidade de Artefatos de Processo (Obrigatório - Seção 9 do Case)** | `AGENTS.md` no repositório | `Detalhes do Desenvolvimento/`<br>• `RESUMO.md` (4 fases)<br>• `INDICE.md` (índice automático)<br>• `notes/` (46 notas técnicas) | Rastreabilidade completa de todas as sessões e iterações de IA realizadas durante o projeto |

---

## 3. Navegação na Aplicação Web

Acesse a plataforma em **[https://pedro-duarte.ddns.net/vertice/](https://pedro-duarte.ddns.net/vertice/)**. A interface reúne os módulos principais:

- **Dashboards Gerenciais:**
  - **Visão Executiva (`/?view=executive`):** Faturamento, margem de contribuição, devoluções e indicadores de vendas.
  - **Estoque & Ruptura (`/?view=inventory`):** Análise de capital imobilizado (descontinuados) e itens abaixo do ponto de pedido.
  - **Auditoria de Dados (`/?view=audit`):** Painel interativo com as 7 inconsistências e divergências do Data Room.
  - **Roadmap 30-60-90 (`/?view=roadmap`):** Cronograma de implementação, squads e entregas por fase.

- **Central de Entregáveis (`/?view=deliverables`):**
  - Leitura e visualização formatada dos 5 relatórios estratégicos do case.
  - Visualizador interativo da **Árvore de Hipóteses** vetorial.
  - **Download individual** de arquivos ou exportação de todo o pacote em **ZIP**.

- **Copiloto de IA (`/?view=copilot`):**
  - Agente analítico para simulações de impacto de descontos, estoque e margem.
  - Disparo de auditoria automatizada e envio de relatório executivo por e-mail.

