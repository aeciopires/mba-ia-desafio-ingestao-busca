# MBA IA - Desafio Ingestão & Busca - RAG System

<!-- TOC -->

- [MBA IA - Desafio Ingestão \& Busca - RAG System](#mba-ia---desafio-ingestão--busca---rag-system)
- [Introdução](#introdução)
  - [Objetivo](#objetivo)
  - [Requisitos de Software](#requisitos-de-software)
  - [Variáveis de Ambiente](#variáveis-de-ambiente)
    - [Configuração de API Keys](#configuração-de-api-keys)
  - [Quick Start](#quick-start)
  - [Validação de Requisitos](#validação-de-requisitos)
  - [Test Cases](#test-cases)
  - [Troubleshooting](#troubleshooting)
    - ["ModuleNotFoundError: No module named 'src'"](#modulenotfounderror-no-module-named-src)
    - ["Connection refused" (Database)](#connection-refused-database)
    - ["OPENAI\_API\_KEY not found"](#openai_api_key-not-found)
  - [Arquitetura](#arquitetura)
    - [Fase 1: Ingestão](#fase-1-ingestão)
    - [Fase 2: Busca](#fase-2-busca)
  - [Estrutura do Projeto](#estrutura-do-projeto)
    - [PDF Ingestion (src/ingest.py)](#pdf-ingestion-srcingestpy)
    - [Vector Search (src/search.py)](#vector-search-srcsearchpy)
    - [Interactive Chat (src/chat.py)](#interactive-chat-srcchatpy)
  - [Tecnologias utilizadas](#tecnologias-utilizadas)
  - [Key Features](#key-features)
  - [Performance Metrics](#performance-metrics)
    - [Embeddings taking long time](#embeddings-taking-long-time)
  - [Security Notes](#security-notes)
  - [API Contracts](#api-contracts)
    - [search\_prompt(question: str) → str](#search_promptquestion-str--str)
    - [ingest\_pdf() → None](#ingest_pdf--none)
    - [chat.py](#chatpy)
  - [License](#license)


<!-- TOC -->

# Introdução

Projeto de ingestão de PDF, armazenamento de embeddings em PostgreSQL+pgVector e busca semântica via CLI usando LangChain.

## Objetivo

Implementar um pipeline end-to-end que:

- **Ingere PDFs** e divide em chunks semanticamente coerentes
- **Gera embeddings** usando modelos offline (SentenceTransformer) - sem dependência de APIs
- **Armazena** chunks com vetores em PostgreSQL+pgvector
- **Busca** semanticamente documentos relevantes
- **Responde** perguntas baseado apenas no contexto ingerido (zero hallucination)

## Requisitos de Software

| Requisito | Versão | Status |
|-----------|--------|--------|
| **Python** | 3.10+ | ✅ Testado em 3.10.12 |
| **Docker** | 20.10+ | ✅ Necessário para Database |
| **Docker Compose** | 1.29+ | ✅ Para orquestração |
| **PostgreSQL** | 17 (pgvector) | ✅ Via Docker |
| **pip** | 23.0+ | ✅ Para pacotes |

## Variáveis de Ambiente

| Variável | Propósito | Padrão | Obrigatório |
|----------|----------|--------|------------|
| `OPENAI_API_KEY` | OpenAI API key | - | ❌ (se usar OpenAI) |
| `GOOGLE_API_KEY` | Google Generative AI key | - | ❌ (se usar Google) |
| `DATABASE_URL` | PostgreSQL connection | `postgresql+psycopg2://postgres:postgres@localhost:5433/rag` | ❌ |
| `PDF_PATH` | Path to PDF file | `./document.pdf` | ❌ |
| `PG_VECTOR_COLLECTION_NAME` | Collection name | `documents` | ❌ |
| `LLM_PROVIDER` | Default LLM | `google` | ❌ |

### Configuração de API Keys

Configure as credenciais nos arquivos `openai.yaml` e `gemini.yaml`, ou nas variáveis de ambiente `OPENAI_API_KEY` / `GOOGLE_API_KEY`.

**Opção 1**: Arquivos de configuração `openai.yaml` e `gemini.yaml`

Exemplo do arquivo `openai.yaml`

```yaml
site: "https://platform.openai.com/settings/organization/api-keys"
id: "key_..."
secret: "sk-proj-..."
```

Exemplo do arquivo `gemini.yaml`:

```yaml
site: "https://aistudio.google.com/api-keys"
nome: "Gemini API"
projeto: "1234567890"
secret: "AQ.Ab8R..."
```

**Opção 2**: Variáveis de Ambiente

```bash
export OPENAI_API_KEY=sk-proj-...
export GOOGLE_API_KEY=AQ.Ab8R...
```

## Quick Start

Clone o repositório:

```bash
git clone https://github.com/aeciopires/mba-ia-desafio-ingestao-busca
cd mba-ia-desafio-ingestao-busca
```

Crie e ative um ambiente virtual antes de instalar dependências:

```yaml
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure API keys (edit openai.yaml and/or gemini.yaml)
# OR set environment variables
```

Inicialize o banco de dados:

```bash
# Start PostgreSQL+pgvector
docker compose up -d

# Verify
docker compose ps
# Expected: postgres_rag ... Up (healthy)
```

Ingestão do PDF:

```bash
export PYTHONPATH=$PWD
python src/ingest.py

# Expected output:
# INFO: PDF carregado com 34 páginas
# INFO: PDF dividido em 67 chunks
# Batches: 100%|██████████| 3/3
# INFO: Ingestão concluída
```

Chat (CLI) para busca:

```bash
python -c "
from src.search import search_prompt
resposta = search_prompt('O que é a empresa?')
print('Resposta:', resposta)
"
```

Chat interativo:

```bash
python src/chat.py
# PERGUNTA: O que é a empresa?
# RESPOSTA: [Contexto-based answer]
# PERGUNTA: sair
```

## Validação de Requisitos

```bash
python src/validate.py
```

Saída esperada:

```
✓ Python 3.10.12 ✓
✓ docker instalado ✓
✓ docker-compose instalado ✓
✓ PDF encontrado ✓
✓ Todas as dependências instaladas ✓
✓ DATABASE_URL configurada ✓
✓ OpenAI API key configurada ✓
✓ Google API key configurada ✓
✓ ✓ TODOS OS REQUISITOS VALIDADOS
```

## Test Cases

```bash
# 1. Validate requirements
python src/validate.py

# 2. Ingest PDF
python src/ingest.py

# 3. Test searches
python -c "
from src.search import search_prompt

tests = [
    ('O que é a empresa?', 'Should have context'),
    ('Qual é a capital da França?', 'Should return fallback'),
]

for q, expected in tests:
    resp = search_prompt(q)
    print(f'Q: {q}')
    print(f'A: {resp[:80]}...')
    print()
"

# 4. Interactive chat
python src/chat.py
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'src'"

```bash
export PYTHONPATH=$PWD
python src/ingest.py
```

### "Connection refused" (Database)

```bash
docker compose ps
docker compose up -d
docker compose logs postgres
```

### "OPENAI_API_KEY not found"

```bash
# Use environment variable
export OPENAI_API_KEY=sk-proj-...

# OR use Google (default)
export LLM_PROVIDER=google
```

## Arquitetura

```
PDF → Split Chunks → Generate Embeddings → Store in PGVector
                                               ↓
                                        Vector Search (k=10)
                                               ↓
                                        Build Prompt Context
                                               ↓
                                        LLM Inference (OpenAI/Google)
                                               ↓
                                        Context-based Response
```

Workflow

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

Workflow resumido

1. **Setup**: Environment, dependencies, configs
2. **Start DB**: Docker containers
3. **Ingest**: PDF → chunks → embeddings → storage
4. **Chat**: User queries → vector search → LLM → response


### Fase 1: Ingestão

```
1. load_pdf(path) → PyPDFLoader
2. split_documents(docs) → RecursiveCharacterTextSplitter
3. create_vector_store() → PGVector + SentenceTransformer
4. store.add_documents(chunks) → PostgreSQL + pgvector extension
```

### Fase 2: Busca

```
1. search_prompt(question)
2. embed_query(question) → SentenceTransformer
3. similarity_search_with_score(k=10) → PGVector
4. _build_context(results)
5. llm.invoke(prompt) → GoogleGenerativeAI/ChatOpenAI
6. return answer
```

## Estrutura do Projeto

```
mba-ia-desafio-ingestao-busca/
├── src/
│   ├── config.py                 # Configuration loader (YAML/env vars)
│   ├── ingest.py                 # PDF ingestion pipeline
│   ├── search.py                 # Vector search + LLM response
│   ├── chat.py                   # Interactive CLI
│   ├── validate.py               # Requirements validation
│   └── simple_embeddings.py       # SentenceTransformer wrapper
├── docker-compose.yml            # PostgreSQL+pgvector stack
├── requirements.txt              # Python dependencies
├── document.pdf                  # Test PDF (34 pages, 67 chunks)
├── openai.yaml                   # OpenAI API key config
├── gemini.yaml                   # Google API key config
└── README.md                     # This file
```

### PDF Ingestion (src/ingest.py)

- **Loader**: PyPDFLoader → 34 páginas
- **Splitter**: RecursiveCharacterTextSplitter (1000 chars, 150 overlap)
- **Output**: 67 chunks semanticamente coerentes
- **Embeddings**: SentenceTransformer (384-dim vectors, offline)
- **Storage**: PGVector (PostgreSQL + pgvector extension)

### Vector Search (src/search.py)

- **Query Embedding**: SentenceTransformer (same model as storage)
- **Vector Search**: `similarity_search_with_score(k=10)` via pgvector
- **Context Building**: Format top-10 chunks with source + page
- **LLM Inference**: ChatOpenAI or GoogleGenerativeAI
- **Prompt Template**: CONTEXTO + REGRAS + EXEMPLOS + PERGUNTA

### Interactive Chat (src/chat.py)

```python
while True:
    question = input("PERGUNTA: ")
    if question.lower() in ["sair", "exit", "quit"]:
        break
    answer = search_prompt(question)
    print(f"RESPOSTA: {answer}")
```

## Tecnologias utilizadas

| Componente | Tech | Versão |
|-----------|------|---------|
| **Framework** | LangChain | 0.3.27 |
| **Embeddings** | SentenceTransformer | 3.3.1 |
| **Vector DB** | pgvector | 0.9.0 |
| **Database** | PostgreSQL | 17 |
| **LLM (Primary)** | GoogleGenerativeAI | - |
| **LLM (Secondary)** | ChatOpenAI | - |
| **PDF Parser** | PyPDF | 6.0.0 |
| **Python** | 3.10+ | - |

## Key Features

- **Offline Embeddings**: No API calls, no quota limits  
- **Vector Search**: Semantic similarity via pgvector  
- **Flexible LLM**: Switch between OpenAI/Google at runtime  
- **Zero Hallucination**: Responses only from ingested context  
- **Validation**: Pre-flight checks for all requirements  
- **Docker Support**: Fully containerized database  
- **CLI Interface**: Interactive chat for end users  

## Performance Metrics

- **PDF Loading**: ~100ms (34 pages)
- **Chunking**: ~50ms (67 chunks)
- **Embedding Generation**: ~2-3 seconds (all-MiniLM-L6-v2)
- **Vector Search**: ~10-50ms (pgvector cosine similarity)
- **LLM Response**: ~2-5 seconds (depends on API)

### Embeddings taking long time

- First run: downloads 22MB model (~30s)
- Subsequent runs: uses local cache
- Embeddings processed in batches (very fast after caching)

## Security Notes

- ⚠️ Never commit API keys in openai.yaml/gemini.yaml
- ✅ Use environment variables for production
- ✅ System extracts only from ingested documents
- ✅ No external knowledge base queries

## API Contracts

### search_prompt(question: str) → str

Returns context-based answer or fallback message

### ingest_pdf() → None

Loads PDF, generates embeddings, stores in database

### chat.py

Interactive CLI with "sair"/"exit" to quit

## License

MIT License
