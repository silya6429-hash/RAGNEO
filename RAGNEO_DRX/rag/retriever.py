import requests

from database.vector_store import VectorStore, build_vector_store
from utils.logger import logger


class Retriever:
    """
    Semantic Retriever для RAG
    """

    def __init__(self):

        self.vector_store = VectorStore()

        # ==============================
        # ПРОВЕРКА НАЛИЧИЯ FAISS ИНДЕКСА
        # ==============================

        try:

            self.vector_store.load_index()

            logger.info("FAISS индекс успешно загружен")

        except Exception:

            logger.warning("FAISS индекс не найден. Создаём новый...")

            build_vector_store()

            self.vector_store.load_index()

            logger.info("FAISS индекс создан и загружен")

        # ==============================
        # OLLAMA SETTINGS
        # ==============================

        self.ollama_url = "http://localhost:11434/api/embeddings"
        self.embedding_model = "nomic-embed-text"

    # ==================================
    # QUERY EMBEDDING
    # ==================================

    def embed_query(self, query: str):

        payload = {
            "model": self.embedding_model,
            "prompt": query
        }

        response = requests.post(
            self.ollama_url,
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.text}")

        return response.json()["embedding"]

    # ==================================
    # SEARCH
    # ==================================

    def search(self, query: str, top_k: int = 5):

        logger.info(f"Поиск по запросу: {query}")

        query_vector = self.embed_query(query)

        results = self.vector_store.search(query_vector, top_k)

        logger.info(f"Найдено chunks: {len(results)}")

        return results

    # ==================================
    # CONTEXT BUILDER
    # ==================================

    def build_context(self, query: str, top_k: int = 5):

        results = self.search(query, top_k)

        context = "\n\n".join(
            [r["text"] for r in results]
        )

        return context