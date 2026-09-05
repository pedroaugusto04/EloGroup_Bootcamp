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

## Deploy na VPS via GitHub Actions

O workflow em `.github/workflows/deploy.yml` executa os testes, gera os Parquets,
publica a imagem no GHCR e atualiza o serviço na VPS via SSH. O deploy ocorre em
push para `main` quando houver alteração no código, dados brutos, dependências
ou arquivos de infraestrutura, e também pode ser disparado manualmente.

No GitHub, crie um Environment chamado `production` e configure estes Secrets:

- `VPS_HOST`, `VPS_USER`, `VPS_SSH_PORT` e `VPS_SSH_PRIVATE_KEY`;
- `OPENAI_API_KEY` (necessário para o Copiloto/Agente);
- `RESEND_API_KEY` (necessário apenas para envio real de e-mails).

Configure em Variables, no mínimo, `VPS_APP_DIR` e `APP_BASE_URL`. Os demais
valores têm defaults no workflow; os nomes disponíveis estão em
`.github/env/production.variables.env.example` e
`.github/env/production.secrets.env.example`.
