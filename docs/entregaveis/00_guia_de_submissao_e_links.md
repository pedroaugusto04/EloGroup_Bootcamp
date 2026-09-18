# Hub central de submissão e guia de acesso: Vértice Analytics
**Bootcamp EloGroup 2026 · AI Consulting Lab · Grupo 14**  
**Autores:** Pedro Augusto e Pedro Lobo  
**Cliente:** Vértice Retail (Diretoria Executiva: CEO, CFO, CMO e COO)

---

## 1. Visão geral da entrega

A entrega reúne análise estratégica de negócio, auditoria relacional das bases, artefatos rastreáveis de dados e uma aplicação web com painel executivo e copiloto de IA.

| Entregável | Formato | Onde encontrar |
| :--- | :---: | :--- |
| Apresentação executiva final (Deck principal) | PDF | [`docs/slides/Vértice-Slides.pdf`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/docs/slides/Vértice-Slides.pdf) |
| Slides auxiliares (Contrato de dados e anexos) | PDF / PPTX | [`docs/slides/Vértice-Slides-Auxiliares.pdf`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/docs/slides/Vértice-Slides-Auxiliares.pdf) |
| Painel de gestão e demo de IA | Aplicação web | URL pública / `http://localhost:8501` |
| Relatório executivo e diagnóstico | Markdown (.md) | [`01_relatorio_diagnostico_estrategico.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/docs/entregaveis/01_relatorio_diagnostico_estrategico.md) |
| Business case e modelagem financeira | Markdown (.md) | [`02_business_case_modelagem_financeira.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/docs/entregaveis/02_business_case_modelagem_financeira.md) |
| Dossiê de auditoria e memória de cálculo | Markdown (.md) | [`03_auditoria_dados_memoria_calculo.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/docs/entregaveis/03_auditoria_dados_memoria_calculo.md) |
| Arquitetura de IA e governança | Markdown (.md) | [`04_arquitetura_ia_governanca.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/docs/entregaveis/04_arquitetura_ia_governanca.md) |
| Relatórios de profiling das bases | HTML | [`docs/profiling/`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/docs/profiling/) (vendas, estoque, marketing, clientes, atendimento) |
| Repositório de queries parametrizadas | SQL | [`src/queries/`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/src/queries/) |

---

## 2. Acesso à aplicação web

A aplicação integra o frontend React (TypeScript) e o backend FastAPI (DuckDB e LangGraph) em um único serviço.

### Link em produção
- URL da aplicação: `https://vertice-analytics.onrender.com` *(ou túnel ativo)*
- Documentação da API (Swagger): `/docs`
- Healthcheck: `/api/health`

### Execução local via Docker

```bash
# 1. Subir o container Docker unificado
docker compose up -d --build app

# 2. Abrir no navegador:
http://localhost:8501
```

Instruções para execução sem Docker constam no [`README.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/README.md).

---

## 3. Roteiro de navegação para a banca

Ao abrir a aplicação, os módulos estão disponíveis no menu lateral:

1. **Visão executiva (`/`):** receita líquida de R$ 16,67M, margem de contribuição de 54,34%, impacto de devoluções (R$ 2,5M estornados) e evolução mensal.
2. **Estoque e ruptura (`/inventory`):** R$ 14,77M em itens descontinuados e 701 SKUs abaixo do ponto de pedido (com 96 SKUs zerados em Beleza).
3. **Auditoria relacional (`/audit`):** matriz com as 7 inconsistências estruturais entre marketing, CRM e vendas.
4. **Plano 30-60-90 dias (`/roadmap`):** matriz de priorização com simulação de impacto financeiro em estoque.
5. **Copiloto de IA (`/copilot`):**
   - Chat analítico: consultas sobre estoque e descontinuados (como *"Quais SKUs descontinuados possuem maior capital imobilizado?"* ou *"Qual a recomendação de reposição para Beleza?"*).
   - Auditoria com um clique: botão *"Executar Auditoria de Estoque"* para gerar o parecer com base nos cálculos em DuckDB e despachar o relatório por e-mail.
