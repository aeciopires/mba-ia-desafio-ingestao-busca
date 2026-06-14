import logging
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores.pgvector import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.pdf import PyPDFLoader

from src.config import (
    get_database_url,
    get_document_table_name,
    get_pdf_path,
)
from src.simple_embeddings import SentenceTransformerEmbeddings

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def load_pdf(path: str) -> list[Document]:
    loader = PyPDFLoader(path)
    pages = loader.load()
    logging.info('PDF carregado com %d páginas', len(pages))
    return pages


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    split_docs = splitter.split_documents(documents)
    logging.info('PDF dividido em %d chunks', len(split_docs))
    return split_docs


def create_vector_store(collection_name: str, connection: str) -> PGVector:
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    store = PGVector(
        connection_string=connection,
        embedding_function=embeddings,
        collection_name=collection_name,
        use_jsonb=True,
        create_extension=True,
        pre_delete_collection=False,
    )
    return store


def ingest_pdf():
    pdf_path = get_pdf_path()
    collection_name = get_document_table_name()
    database_url = get_database_url()

    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f'PDF não encontrado em: {pdf_path}')

    documents = load_pdf(str(path))
    split_docs = split_documents(documents)
    store = create_vector_store(
        collection_name=collection_name,
        connection=database_url,
    )
    ids = [f'doc-{index+1}' for index in range(len(split_docs))]
    logging.info('Armazenando %d chunks no banco de dados', len(split_docs))
    store.add_documents(documents=split_docs, ids=ids)
    logging.info('Ingestão concluída')


if __name__ == '__main__':
    ingest_pdf()
