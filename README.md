# Vértice Analytics (EloGroup Suite)

Plataforma de inteligência analítica, auditoria de dados e copiloto de decisão executiva desenvolvida para o case **Vértice Retail (Bootcamp EloGroup 2026)**.

---

## 1. Arquitetura

- **Frontend Moderno (TypeScript)**: Interface web minimalista em React + Vite + Tailwind CSS + Recharts (`frontend/`), desenhada na identidade visual da EloGroup (`#09090b`, `#121215`, `#38bdf8`) e sem emojis.
- **Backend API (FastAPI)**: Servidor assíncrono em Python 3.12 (`src/api/main.py`) expondo os dados analíticos e o Copiloto de IA.
- **Motor de Dados (DuckDB)**: Banco colunar vetorial in-memory que consome diretamente os arquivos `data/processed/*.parquet` e executa consultas SQL em `< 5ms`.
- **Copiloto ReAct (LangGraph)**: Agente inteligente com memória persistente para diagnósticos e simulações de estoque.

### Contrato do Copiloto de estoque

O módulo é um **copiloto de estoque baseado em tendência histórica de vendas**. A posição de Estoque foi fornecida sem data de snapshot confirmada; Vendas cobre o período observado de 01/01/2023 a 26/01/2024. Nenhum cenário representa previsão ou perda realizada.

- `estoque` fornece somente atributos operacionais e cadastrais.
- Todo valor financeiro vem de `vendas`; o valuation usa custo médio ponderado do histórico aprovado.
- As janelas aceitas são `full_history`, `calendar_2023` e `last_90d_observed`.
- A API rejeita filtros SQL livres. `POST /api/copilot/audit/run` aceita apenas `period_key`, `send_email` e `to_email`.
- O worker é executado sob demanda. O parecer factual é publicado quando os checks determinísticos passam, mesmo se o complemento do LLM não estiver disponível.

---

## 2. Como Executar

### Opção A: Via Docker (Recomendado)

A aplicação utiliza um **Multi-Stage Build** que compila o frontend TypeScript e o backend FastAPI em um único container otimizado:

```bash
# 1. Construir e iniciar o container em background
docker compose up -d --build app

# 2. Acessar a aplicação no navegador:
# http://localhost:8501 (Interface Web e Documentação em /docs)

# 3. Parar o container
docker compose down
```

---

### Opção B: Desenvolvimento Local (Sem Docker)

#### 1. Backend (Python + FastAPI)
```bash
# Criar e ativar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependências de runtime e desenvolvimento
pip install -r requirements.txt

# Gerar os arquivos Parquet pré-processados
python -m src.infrastructure.preprocessor

# Iniciar o servidor FastAPI
.venv/bin/uvicorn src.api.main:app --reload --port 8501
```

#### 2. Frontend (TypeScript + React)
Em outro terminal:
```bash
cd frontend
npm install
npm run dev
```
Acesse em: `http://localhost:5173`.

---

## 3. Testes Automatizados

```bash
# Executar a suíte completa de testes (Analytics, API, Repositório e Copiloto)
PYTHONPATH=. .venv/bin/pytest -v

# Validar tipagem e build de produção do frontend TypeScript
cd frontend && npm run build
```
