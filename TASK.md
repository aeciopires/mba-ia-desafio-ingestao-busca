# Ingestão e Busca Semântica com LangChain e Postgres

## Objetivo

Você deve entregar um software capaz de:

- Ingestão: Ler um arquivo PDF e salvar suas informações em um banco de dados PostgreSQL com extensão pgVector.
- Busca: Permitir que o usuário faça perguntas via linha de comando (CLI) e receba respostas baseadas apenas no conteúdo do PDF.
- Exemplo no CLI

```bash
Faça sua pergunta:

PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.
```

Exemplo de perguntas fora do contexto:

```bash
PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

## Tecnologias obrigatórias

- Linguagem: Python
- Framework: LangChain
- Banco de dados: PostgreSQL + pgVector
- Execução do banco de dados: Docker & Docker Compose (docker-compose fornecido no repositório de exemplo)

## Pacotes recomendados

- Split: from langchain_text_splitters import RecursiveCharacterTextSplitter
- Embeddings (OpenAI): from langchain_openai import OpenAIEmbeddings
- Embeddings (Gemini): from langchain_google_genai import - GoogleGenerativeAIEmbeddings
- PDF: from langchain_community.document_loaders import PyPDFLoader
- Ingestãofrom langchain_postgres import PGVector
- Busca: similarity_search_with_score(query, k=10)

## OpenAI

- Use as credenciais disponiveis em: openai.yaml
- Modelo de embeddings: text-embedding-3-small
- Modelo de LLM para responder: gpt-5-nano

## Gemini

- Use as credenciais disponiveis em: gemini.yaml
- Modelo de embeddings: models/embedding-001
- Sugestão de modelo de LLM para responder: gemini-2.5-flash-lite ou gemini-3.1-flash-lite-preview. Você pode utilizar outro modelo do Gemini de sua preferência, desde que atinja os resultados esperados.
- Os limites de requisições gratuitas dos modelos podem mudar com frequência. Para informações atualizadas, consulte a documentação oficial do Google.

## Requisitos

Ingestão do PDF
- O PDF deve ser dividido em chunks de 1000 caracteres com overlap de 150.
- Cada chunk deve ser convertido em embedding.
- Os vetores devem ser armazenados no banco de dados PostgreSQL com pgVector.

Consulta via CLI
- Criar um script Python para simular um chat no terminal.
- Passos ao receber uma pergunta:
  - Vetorizar a pergunta.
  - Buscar os 10 resultados mais relevantes (k=10) no banco vetorial.
  - Montar o prompt e chamar a LLM.
  - Retornar a resposta ao usuário.

Prompt a ser utilizado:

```bash
CONTEXTO:
{resultados concatenados do banco de dados}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta do usuário}

RESPONDA A "PERGUNTA DO USUÁRIO"
```

## Estrutura obrigatória do projeto

Utilize a estrutura abaixo:

```
├── docker-compose.yml
├── requirements.txt      # Dependências
├── .env.example          # Template da variável OPENAI_API_KEY
├── src/
│   ├── ingest.py         # Script de ingestão do PDF
│   ├── search.py         # Script de busca
│   ├── chat.py           # CLI para interação com usuário
├── document.pdf          # PDF para ingestão
└── README.md             # Instruções de execução
```

Repositorio util com conteudo e exemplos: https://github.com/devfullcycle/mba-ia-niv-introducao-langchain

## VirtualEnv para Python

Crie e ative um ambiente virtual antes de instalar dependências:

```bash
python3 -m venv venv
source venv/bin/activate
```

## Ordem de execução

Subir o banco de dados:

```bash
docker compose up -d
```

Executar ingestão do PDF:

```bash
python src/ingest.py
```

Rodar o chat:

```bash
python src/chat.py
```
