# ==============================================================================
# Dockerfile: EloGroup AI Consulting Lab - Projeto Vértice Analytics
# ==============================================================================
# Estágio de dependências de runtime. Mantemos a versão do Python alinhada ao
# ambiente atual e isolamos os artefatos instalados para a imagem final.
FROM python:3.12-slim AS runtime-deps

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements-runtime.txt .
RUN pip install --prefix=/install -r requirements-runtime.txt

# Estágio usado para gerar os Parquets e também pelos testes locais/CI.
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

# Target opcional para executar testes sem adicionar pytest à imagem de runtime.
FROM builder AS test
ENV PYTHONPATH=/install/lib/python3.12/site-packages:/app
COPY app/ /app/app/
COPY tests/ /app/tests/
CMD ["pytest", "tests/test_analytics.py"]

# Imagem final de execução: não leva pytest, CSVs brutos nem o ambiente de
# build para produção.
FROM python:3.12-slim AS runtime

# Defaults seguros para execução em produção. O compose local sobrescreve os
# valores de desenvolvimento (hot reload e volumes).
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_RUN_ON_SAVE=false \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

COPY --from=runtime-deps /install /usr/local

# Instala curl para checagem de saúde (healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Código-fonte da aplicação
COPY src/ /app/src/
COPY app/ /app/app/

# Copia somente os dados derivados gerados no estágio de build.
COPY --from=builder /app/data/processed/ /app/data/processed/

# Porta padrão do Streamlit
EXPOSE 8501

# Healthcheck nativo do Streamlit
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando padrão
CMD ["streamlit", "run", "app/main.py"]
