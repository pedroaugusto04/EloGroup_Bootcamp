# ==============================================================================
# Dockerfile: EloGroup AI Consulting Lab - Projeto Vértice Analytics (v2.0)
# Multi-Stage Build: Frontend (Vite + React + TS) + Backend (FastAPI + DuckDB)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Estágio de Build do Frontend (TypeScript + Vite)
# ------------------------------------------------------------------------------
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ------------------------------------------------------------------------------
# 2. Estágio de Dependências Python de Runtime
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS runtime-deps

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements-runtime.txt .
RUN pip install --prefix=/install -r requirements-runtime.txt

# ------------------------------------------------------------------------------
# 3. Estágio de Pré-Processamento de Dados & Testes
# ------------------------------------------------------------------------------
FROM runtime-deps AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/install/lib/python3.12/site-packages:/app \
    PATH=/install/bin:$PATH \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
RUN pip install --prefix=/install "pytest>=8.0.0"

COPY src/ /app/src/
COPY data/raw/ /app/data/raw/
RUN python -m src.infrastructure.preprocessor

# ------------------------------------------------------------------------------
# 4. Target Opcional de Testes no CI
# ------------------------------------------------------------------------------
FROM builder AS test
ENV PYTHONPATH=/install/lib/python3.12/site-packages:/app
COPY tests/ /app/tests/
CMD ["pytest", "tests/"]

# ------------------------------------------------------------------------------
# 5. Imagem Final de Produção (FastAPI servindo API e Frontend Estático)
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8501 \
    HOST=0.0.0.0

COPY --from=runtime-deps /install /usr/local

# Instala curl para checagem de saúde (healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Código-fonte da aplicação
COPY src/ /app/src/

# Documentos e entregáveis do case
COPY docs/ /app/docs/

# Dados pré-processados gerados
COPY --from=builder /app/data/processed/ /app/data/processed/

# Frontend estático compilado
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Porta padrão da aplicação
EXPOSE 8501

# Healthcheck nativo da API
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/api/health || exit 1

# Inicialização do servidor FastAPI
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8501"]
