# Desafio MBA Engenharia de Software com IA - Full Cycle

<!-- TOC -->

- [Desafio MBA Engenharia de Software com IA - Full Cycle](#desafio-mba-engenharia-de-software-com-ia---full-cycle)
  - [Introdução](#introdução)
  - [Requisitos](#requisitos)
  - [Instruções de uso](#instruções-de-uso)
  - [Workflow](#workflow)

<!-- TOC -->

## Introdução

Projeto de ingestão de PDF, armazenamento de embeddings em PostgreSQL+pgVector e busca semântica via CLI usando LangChain.

Estrutura

- `docker-compose.yml` — PostgreSQL com extensão `vector` (pgVector).
- `requirements.txt` — dependências Python.
- `.env.example` — variáveis de ambiente exemplo.
- `document.pdf` — PDF alvo para ingestão.
- `src/ingest.py` — script de ingestão (gera chunks e salva vetores).
- `src/search.py` — busca vetorial e montagem do prompt.
- `src/chat.py` — interface CLI para perguntas.

## Requisitos

- Instale os seguintes softwares:
  - python3
  - docker
  - docker-compose

Configure as credenciais nos arquivos `openai.yaml` e `gemini.yaml`, ou nas variáveis de ambiente `OPENAI_API_KEY` / `GOOGLE_API_KEY`.

Exemplo do arquivo `openai.yaml`:

```yaml
site: "https://platform.openai.com/settings/organization/api-keys"
id: "CHANGE_ID_HERE"
secret: "CHANGE_SECRET_HERE"
```

Exemplo do arquivo `gemini.yaml`:

```yaml
site: "https://aistudio.google.com/api-keys"
nome: "CHANGE_NAME_PROJECT"
nome-do-projeto: "projects/CHANGE_PROJECT_ID"
projeto: "CHANGE_PROJECT_ID"
secret: "CHANGE_SECRET_HERE"
```

## Instruções de uso

Crie e ative um ambiente virtual antes de instalar dependências:

```bash
python3 -m venv venv
source venv/bin/activate
```

Instale dependências:

```bash
pip install -r requirements.txt
```

Inicialize o banco de dados

```bash
docker-compose up -d
```

Ingestão:

- `python src/ingest.py` — divide `document.pdf` em chunks de 1000 caracteres com overlap 150 e armazena embeddings em PostgreSQL via pgVector.

Chat (CLI):

- `python src/chat.py` — faz perguntas; o sistema busca os 10 documentos mais relevantes e chama a LLM para responder somente baseado no contexto.

## Workflow

```mermaid
flowchart TD
  A[Início] --> B[Start DB docker-compose]
  B --> C[Run ingest.py]
  C --> D[Load PDF -> Split chunks]
  D --> E[Create embeddings]
  E --> F["Store vectors in Postgres+pgVector"]
  F --> G[Run chat.py]
  G --> H[User pergunta]
  H --> I[Vector search k=10]
  I --> J[Build prompt with CONTEXTO + REGRAS]
  J --> K["Call LLM (OpenAI/Gemini)"]
  K --> L[Return answer to user]
```

Observações

- Se houver erro com `langchain_postgres`/`psycopg`, a implementação usa `langchain_community` `PGVector` (compatível com `psycopg2`) para persistência.
- Ajuste `DATABASE_URL` em ambiente ou `.env` para apontar para o banco (ex.: `postgresql://postgres:postgres@localhost:5432/rag`).
