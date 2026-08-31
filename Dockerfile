# ==============================================================================
# Dockerfile: EloGroup AI Consulting Lab - Projeto Vértice Analytics
# ==============================================================================
FROM python:3.12-slim

# Variáveis de ambiente para Python e Streamlit com Hot Reload ativo
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_RUN_ON_SAVE=true \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=poll \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Instala curl para checagem de saúde (healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# 1. Instalação de dependências (aproveita cache de camadas)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 2. Cópia do código-fonte, dados e testes
COPY src/ /app/src/
COPY app/ /app/app/
COPY data/ /app/data/
COPY tests/ /app/tests/

# 3. Pré-processamento dos dados na inicialização/build
RUN python -m src.infrastructure.preprocessor || true

# Porta padrão do Streamlit
EXPOSE 8501

# Healthcheck nativo do Streamlit
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando padrão
CMD ["streamlit", "run", "app/main.py"]
