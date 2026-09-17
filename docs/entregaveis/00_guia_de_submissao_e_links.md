# Hub Central de Submissão e Guia de Acesso: Vértice Analytics
**Bootcamp EloGroup 2026 · AI Consulting Lab · Grupo 3**  
**Autores:** Pedro Augusto & Pedro Lobo  
**Cliente:** Vértice Retail (Diretoria Executiva — CEO, CFO, CMO, COO)

---

## 1. Visão Geral da Entrega

A entrega do Grupo 3 combina **rigor consultivo de negócio**, **auditoria determinística de dados** e uma **plataforma tecnológica em produção** contendo Dashboard Executivo e Copiloto de IA conversacional.

| Entregável Oficial | Formato Principal | Onde Encontrar |
| :--- | :---: | :--- |
| **Apresentação Executiva Final** | PDF / Slides | [`docs/slides/Vértice (1).pdf`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/docs/slides/Vértice%20(1).pdf) |
| **Dashboard de Gestão & Demo de IA** | **Aplicação Web Ativa** | URL pública / `http://localhost:8501` |
| **Relatório Executivo C-Level** | Markdown (.md) | [`01_relatorio_diagnostico_estrategico.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/docs/entregaveis/01_relatorio_diagnostico_estrategico.md) |
| **Business Case & Modelagem Financeira** | Markdown (.md) | [`02_business_case_modelagem_financeira.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/docs/entregaveis/02_business_case_modelagem_financeira.md) |
| **Dossiê de Auditoria & Memória de Cálculo** | Markdown (.md) | [`03_auditoria_dados_memoria_calculo.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/docs/entregaveis/03_auditoria_dados_memoria_calculo.md) |
| **Arquitetura de IA, Segurança e Governança** | Markdown (.md) | [`04_arquitetura_ia_governanca.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/docs/entregaveis/04_arquitetura_ia_governanca.md) |

---

## 2. Acesso à Aplicação Web (Dashboard & Copiloto)

A aplicação unifica o frontend React (TypeScript) e o backend FastAPI (DuckDB + LangGraph) em um único servidor otimizado.

### Link de Produção (Acesso Online)
- **URL da Aplicação Web:** `https://vertice-analytics.onrender.com` *(ou via Cloudflare Tunnel ativo)*
- **Documentação Interativa da API (Swagger):** `/docs`
- **Healthcheck:** `/api/health`

### Como Rodar Localmente em 1 Passo (Via Docker)
Caso deseje reproduzir a execução no seu próprio ambiente local:

```bash
# 1. Clonar e subir o container Docker unificado
docker compose up -d --build app

# 2. Abrir no navegador:
http://localhost:8501
```

*(Para execução nativa sem Docker via Python e Vite, consulte as instruções em [`README.md`](file:///home/pedroduarte/Documents/GitHub/EloGroup_Bootcamp/README.md)).*

---

## 3. Roteiro de Navegação para Avaliação da Banca

Ao acessar a aplicação, a banca pode testar diretamente as seguintes visões no menu lateral:

1. **Visão Executiva (`/`):** KPIs macro de receita líquida (R$ 16,67M), margem de contribuição (54,34%), impacto de devoluções (R$ 2,5M estornados) e visão mensal.
2. **Estoque & Ruptura (`/inventory`):** Mapa dos R$ 14,77M em descontinuados e lista dos 701 SKUs com estoque abaixo do ponto de pedido (96 SKUs zerados em Beleza).
3. **Auditoria Relacional (`/audit`):** Matriz que expõe os 7 defeitos estruturais do data room (inconsistência entre marketing, CRM e vendas).
4. **Plano 30/60/90 Dias (`/roadmap`):** Matriz interativa de priorização com cálculo dinâmico do impacto financeiro do estoque.
5. **Copiloto de IA (`/copilot`):**
   - **Chat Interativo:** Converse com o *Predictive Stock Advisor* perguntando *"Quais SKUs descontinuados possuem maior capital imobilizado?"* ou *"Qual a recomendação de reposição para Beleza?"*.
   - **Auditoria Autônoma com 1 Clique:** Clique em *"Executar Auditoria de Estoque"* para gerar o parecer técnico factual e disparar o relatório formatado por e-mail com salvaguardas determinísticas contra alucinações.
