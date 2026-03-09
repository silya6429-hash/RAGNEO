import json
from pathlib import Path

import faiss
import numpy as np

from utils.config import config
from utils.logger import logger
from utils.helpers import ensure_dir
from rag.graph_expansion import GraphExtractor

class VectorStore:
    """
    Векторное хранилище на базе FAISS
    """

    def __init__(self):
        self.embeddings_dir = config.EMBEDDINGS_DIR

        self.data_dir = config.DATA_DIR
        self.faiss_dir = self.data_dir / "faiss"

        ensure_dir(self.data_dir)
        ensure_dir(self.faiss_dir)

        self.index_path = self.faiss_dir / "faiss.index"
        self.metadata_path = self.faiss_dir / "metadata.json"

        self.index = None
        self.metadata = []
        

    # ============================
    # LOAD EMBEDDINGS
    # ============================

    def load_embeddings(self):

        vectors = []
        metadata = []

        files = list(self.embeddings_dir.glob("*.json"))

        if not files:
            logger.warning("Embeddings не найдены")
            return vectors, metadata

        for file in files:

            logger.info(f"Загрузка embeddings: {file.name}")

            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for item in data:

                vectors.append(item["embedding"])

                metadata.append({
                    "chunk_id": item["chunk_id"],
                    "text": item["text"]
                })

        return vectors, metadata

    # ============================
    # BUILD INDEX
    # ============================

    def build_index(self):

        logger.info("Создание FAISS индекса")

        vectors, metadata = self.load_embeddings()

        if not vectors:
            raise Exception("Нет embeddings для индекса")
        
        graph_builder = GraphExtractor()

        for item in metadata:

            text = item["text"]

            logger.info("Извлечение связей из chunk")

            graph_builder.process_chunk(text)

        vectors = np.array(vectors).astype("float32")

        dimension = vectors.shape[1]

        logger.info(f"Размерность embedding: {dimension}")

        self.index = faiss.IndexFlatL2(dimension)

        self.index.add(vectors)

        self.metadata = metadata

        logger.info(f"Добавлено векторов: {len(vectors)}")

    # ============================
    # SAVE INDEX
    # ============================

    def save_index(self):

        if self.index is None:
            raise Exception("Index не создан")

        faiss.write_index(self.index, str(self.index_path))

        with open(self.metadata_path, "w", encoding="utf-8") as f:

            json.dump(
                self.metadata,
                f,
                ensure_ascii=False,
                indent=2
            )

        logger.info("FAISS индекс сохранён")

    # ============================
    # LOAD INDEX
    # ============================

    def load_index(self):

        if not self.index_path.exists():
            raise Exception("FAISS индекс не найден")

        self.index = faiss.read_index(str(self.index_path))

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        logger.info("FAISS индекс загружен")

    # ============================
    # SEARCH
    # ============================

    def search(self, query_vector, top_k=5):

        if self.index is None:
            raise Exception("Индекс не загружен")

        query_vector = np.array([query_vector]).astype("float32")

        distances, indices = self.index.search(query_vector, top_k)

        results = []

        for i in indices[0]:

            if i < len(self.metadata):
                results.append(self.metadata[i])

        return results


# ============================
# BUILD PIPELINE
# ============================

def build_vector_store():
    
    graph_builder = GraphExtractor()
    
    store = VectorStore()

    store.build_index()

    store.save_index()

    return store