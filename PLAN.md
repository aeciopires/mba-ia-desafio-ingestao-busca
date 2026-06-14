# Plano de implementação

## Objetivo

Criar uma solução Python que faça ingestão de um PDF, armazene embeddings no PostgreSQL com pgVector e permita buscas semânticas via CLI usando LangChain.

## Escopo

- Ingestão de `document.pdf` em chunks de 1000 caracteres com overlap de 150.
- Criação de embeddings usando as credenciais em `openai.yaml` ou `gemini.yaml`.
- Armazenamento dos vetores no PostgreSQL via pgVector.
- Consulta via CLI que busca os 10 resultados mais relevantes e gera a resposta com LLM.
- Resposta baseada apenas no contexto retornado pelo banco de dados.

## Arquivos principais

- `docker-compose.yml` - orquestra o PostgreSQL com pgVector.
- `requirements.txt` - dependências Python.
- `.env.example` - exemplo de variável de ambiente para `OPENAI_API_KEY`.
- `src/ingest.py` - script de ingestão do PDF para o banco de dados.
- `src/search.py` - busca semântica no banco de dados.
- `src/chat.py` - interface de chat CLI para perguntas do usuário.
- `README.md` - instruções de uso.

## Passos

1. Validar ambiente
   - Verificar se o banco PostgreSQL com pgVector está configurado no `docker-compose.yml`.
   - Certificar que `requirements.txt` inclui `langchain`, `langchain_text_splitters`, `langchain_openai`, `langchain_community`, `langchain_postgres`, `psycopg2-binary`, `PyPDF2` ou similares.
   - Criar `.env.example` com `OPENAI_API_KEY` se ainda não existir.

2. Implementar ingestão (`src/ingest.py`)
   - Carregar `document.pdf` com `PyPDFLoader`.
   - Dividir texto com `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)`.
   - Gerar embeddings com `OpenAIEmbeddings` ou `GoogleGenerativeAIEmbeddings`.
   - Salvar os vetores em PostgreSQL usando `PGVector`.
   - Garantir que cada chunk armazene texto original e metadados úteis.

3. Implementar busca semântica (`src/search.py`)
   - Conectar ao banco vetorial.
   - Carregar o vetor store existente.
   - Executar `similarity_search_with_score(query, k=10)`.
   - Retornar o conjunto de resultados para montagem do prompt.

4. Implementar interface CLI (`src/chat.py`)
   - Perguntar ao usuário por uma pergunta.
   - Vetorizar a pergunta.
   - Buscar os 10 resultados mais relevantes.
   - Construir o prompt com o formato exigido:
     - `CONTEXTO:` com resultados concatenados
     - `REGRAS:` com instrução de responder apenas com base no contexto
     - Exemplo de perguntas fora do contexto
     - `PERGUNTA DO USUÁRIO:`
   - Chamar a LLM (`gpt-5-nano` ou equivalente Gemini) para gerar a resposta.
   - Exibir a resposta no terminal.
   - Caso a resposta inclua informação fora do contexto, forçar a mensagem padrão.

5. Garantir robustez
   - Tratar falhas de conexão ao banco e ausência da base de dados.
   - Tratar perguntas vazias.
   - Evitar duplicatas de chunks ou prompts mal formatados.

6. Documentação (`README.md`)
   - Instruções para criar/ativar `venv`.
   - Comandos para subir o banco com `docker compose up -d`.
   - Passos para rodar ingestão e chat.
   - Descrição dos arquivos de configuração `openai.yaml` e `gemini.yaml`.

## Critérios de aceitação

- O PDF é dividido em chunks de 1000 caracteres com 150 de overlap.
- Cada chunk gera embedding e é persistido em PostgreSQL com pgVector.
- A busca retorna os 10 vetores mais relevantes.
- O chat responde apenas com base no contexto e devolve a mensagem de não-saber quando não há informação.
- A solução usa Python, LangChain e PostgreSQL+pgVector.
- O fluxo segue:
  1. `docker compose up -d`
  2. `python src/ingest.py`
  3. `python src/chat.py`
