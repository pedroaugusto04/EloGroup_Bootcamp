# Vértice Analytics

Este projeto é uma aplicação Streamlit para análise de dados. Abaixo estão as instruções de como executar a aplicação com e sem Docker.

## Como Executar

### 1. Via Docker (Recomendado)

Você pode iniciar a aplicação utilizando o Docker Compose.

1. Construa a imagem:
   ```bash
   docker compose build
   ```
2. Inicie os containers em segundo plano:
   ```bash
   docker compose up -d app
   ```
3. Acesse a aplicação no navegador em: http://localhost:8501
4. Para parar a aplicação:
   ```bash
   docker compose down
   ```

---

### 2. Sem Docker

Para rodar o projeto diretamente no seu ambiente local, certifique-se de ter o Python 3.12 instalado.

1. (Recomendado) Crie e ative um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Linux/macOS
   # ou
   .venv\Scripts\activate     # No Windows
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o script de pré-processamento de dados (necessário para preparar os arquivos Parquet de dados):
   ```bash
   python -m src.infrastructure.preprocessor
   ```

4. Inicie o Streamlit:
   ```bash
   streamlit run app/main.py
   ```

5. Acesse a aplicação no navegador em: http://localhost:8501