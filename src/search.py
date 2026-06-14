import logging
import os
from typing import List, Optional

from langchain_openai import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.vectorstores.pgvector import PGVector

from src.config import (
    get_database_url,
    get_document_table_name,
    get_llm_provider,
    get_openai_api_key,
    get_google_api_key,
    get_openai_llm_model,
    get_google_llm_model,
)
from src.simple_embeddings import SentenceTransformerEmbeddings

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

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
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

NO_INFO_RESPONSE = "Não tenho informações necessárias para responder sua pergunta."


def _ensure_api_key(provider: str) -> None:
    if provider == "openai":
        key = get_openai_api_key()
        if not key:
            raise EnvironmentError("OPENAI_API_KEY não encontrado. Configure openai.yaml ou variável de ambiente.")
        os.environ.setdefault("OPENAI_API_KEY", key)
    elif provider == "google":
        key = get_google_api_key()
        if not key:
            raise EnvironmentError("GOOGLE_API_KEY não encontrado. Configure gemini.yaml ou variável de ambiente.")
        os.environ.setdefault("GOOGLE_API_KEY", key)
    else:
        raise ValueError("LLM_PROVIDER inválido")


def _get_embeddings(provider: str):
    return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


def _get_llm(provider: str):
    if provider == "openai":
        return ChatOpenAI(model_name=get_openai_llm_model())
    return GoogleGenerativeAI(model=get_google_llm_model())


def _load_vector_store(provider: str) -> PGVector:
    embeddings = _get_embeddings(provider)
    db_url = get_database_url()
    collection = get_document_table_name()
    store = PGVector(
        connection_string=db_url,
        embedding_function=embeddings,
        collection_name=collection,
        use_jsonb=True,
        create_extension=False,
    )
    return store


def _build_context(results: List[tuple]) -> str:
    parts: List[str] = []
    for doc, score in results:
        src = doc.metadata.get("source", "document")
        page = doc.metadata.get("page") or doc.metadata.get("page_number")
        header = f"Fonte: {src}"
        if page is not None:
            header += f" / página {page}"
        parts.append(f"{header}\n{doc.page_content.strip()}")
    return "\n\n".join(parts).strip()


def search_prompt(question: Optional[str] = None) -> str:
    if not question or not question.strip():
        raise ValueError("Pergunta vazia")

    provider = get_llm_provider()
    _ensure_api_key(provider)

    store = _load_vector_store(provider)
    logging.info("Executando busca vetorial k=10")
    results = store.similarity_search_with_score(question, k=10)
    if not results:
        return NO_INFO_RESPONSE

    context = _build_context(results)
    if not context:
        return NO_INFO_RESPONSE

    prompt = PROMPT_TEMPLATE.format(contexto=context, pergunta=question)
    llm = _get_llm(provider)

    try:
        # Use invoke with message format for ChatOpenAI and GoogleGenerativeAI
        from langchain_core.messages import HumanMessage
        answer = llm.invoke([HumanMessage(content=prompt)])
        if hasattr(answer, 'content'):
            answer = answer.content
    except Exception as e:
        logging.error("Erro ao invocar LLM: %s", e)
        return NO_INFO_RESPONSE

    if not answer:
        return NO_INFO_RESPONSE
    return str(answer).strip()
