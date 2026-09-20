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

## 3. Como Visualizar e Testar na Aplicação Web em Produção

A aplicação web hospedada em **[https://pedro-duarte.ddns.net/vertice/](https://pedro-duarte.ddns.net/vertice/)** reúne todos os componentes analíticos e operacionais do projeto:

### 3.1. Leitura dos Relatórios e Exportação Unificada (Aba "Entregáveis")
- **URL Direta:** `https://pedro-duarte.ddns.net/vertice/?view=deliverables`
- **Funcionalidades:**
  - Visualização formatada em Markdown de todos os 5 documentos estratégicos (Diagnóstico, Business Case, Auditoria, Governança e Metodologia).
  - Visualização interativa da **Árvore de Hipóteses** vetorial (`SVG`).
  - Alternância entre modo de leitura (*preview*), edição e tela dividida (*split*).
  - **Download individual** de cada arquivo `.md`.
  - **Botão "Baixar Pacote Completo (.ZIP)"**: exporta em um único arquivo compactado todos os relatórios em Markdown, guias e assets visuais (`GET /api/deliverables/export/zip`).

### 3.2. Teste do Agente Copiloto de IA (Aba "Copiloto de IA")
- **URL Direta:** `https://pedro-duarte.ddns.net/vertice/?view=copilot`
- **Arquitetura:** O copiloto utiliza o padrão **ReAct** integrado ao **DuckDB** e **LangGraph**, aplicando uma **salvaguarda factual estrita**: modelos de linguagem nunca calculam métricas financeiras ou de giro diretamente; todas as métricas são apuradas pelo motor analítico determinístico antes da redação executiva.
- **Como Testar:**
  - Selecione a janela temporal desejada (*Histórico Completo*, *Ano 2023* ou *Últimos 90 Dias*).
  - Exemplos de perguntas para testar a inteligência do agente:
    - *"Qual o impacto financeiro de liquidar a categoria Moda com 30% de desconto?"*
    - *"Quantos SKUs descontinuados possuem saldo em estoque e qual o capital imobilizado?"*
    - *"Quais categorias apresentam o maior risco de ruptura e estão abaixo do ponto de pedido?"*
  - **Relatório Executivo Automatizado por E-mail:** na interface, clique no botão para executar a auditoria autônoma (`POST /api/copilot/audit/run`), que gera o parecer auditado e despacha um memo executivo formatado diretamente para a diretoria.

### 3.3. Dashboards Analíticos de Gestão
- **Visão Executiva (`/?view=executive`):** Faturamento líquido de R$ 16,67M (R$ 14,17M retido pós-devoluções), margem de contribuição estável em 54,6%, volume de pedidos e taxa de devolução de 14,88%.
- **Estoque (`/?view=inventory`):** Mapeamento dos 206 SKUs descontinuados com capital imobilizado (R$ 6,1M de custo histórico) e dos 701 SKUs ativos abaixo do ponto de pedido.
- **Auditoria Relacional (`/?view=audit`):** Painel interativo com as 7 divergências estruturais do Data Room (Marketing x Vendas, Clientes x Vendas com 40,6% de concentração, temporalidade desacoplada, inelasticidade de descontos, etc.).
- **Roadmap 30-60-90 Dias (`/?view=roadmap`):** Cronograma dinâmico em formato Gantt com detalhamento de squads, dependências técnicas, entregas e critérios de sucesso.

---

## 4. Auditoria de Conformidade para a Entrega

### Validações de Consistência:
1. **Consistência Numérica:** Todos os documentos compartilham exatamente a mesma base auditada:
   - Receita retida pós-devoluções: **R$ 14,17M** (de R$ 16,67M faturados em pedidos aprovados).
   - Liquidação de descontinuados (cenário central, 50% sell-through, 30% desc.): **R$ 4,14M** de receita pós-devoluções.
   - Retorno anual recorrente: **R$ 1,86M/ano** (R$ 1,80M em disciplina de descontos + R$ 55,7 mil em automação de CX).
   - Investimento ano 1: **R$ 350 mil** | ROI Líquido: **4,3x** | Payback: **2,3 meses**.
2. **Aplicação em Produção Online:** O servidor web em `https://pedro-duarte.ddns.net/vertice/` está ativo, respondendo com status HTTP 200 e com endpoints de API funcionais.
3. **Multiplataforma:** A entrega pode ser consumida via web interativa, via repositório de código ou via documentos Markdown/ZIP.

### Observações de Organização dos Arquivos:
1. **Imagem do Roadmap (`RoadMap.png`):**
   - A imagem de alta resolução do Roadmap foi sincronizada de `Bootcamp_Documentos_Grupo14/RoadMap/RoadMap.png` para `docs/assets/RoadMap.png` no repositório.
2. **Artefatos de Processo (Seção 9 do Case - "Traceability of Process Artifacts"):**
   - A pasta `Detalhes do Desenvolvimento/` (com `RESUMO.md`, `INDICE.md` e as 46 notas técnicas em `notes/`) comprova o uso disciplinado e rastreável de inteligência artificial durante todas as fases do projeto. Ao submeter os arquivos do grupo, garanta que esta pasta esteja inclusa no pacote enviado à banca.
