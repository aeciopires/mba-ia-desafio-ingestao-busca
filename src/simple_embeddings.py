"""
Embeddings usando sentence-transformers - modelo offline e gratuito.
"""

from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbeddings(Embeddings):
    """Embeddings usando modelos sentença transformers (offline)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed search docs."""
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return [emb.tolist() for emb in embeddings]

    def embed_query(self, text: str) -> list[float]:
        """Embed query text."""
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

