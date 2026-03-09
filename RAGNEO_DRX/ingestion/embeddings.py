import json
from pathlib import Path
from typing import List, Dict

import requests

from utils.config import config
from utils.logger import logger
from utils.helpers import ensure_dir


class EmbeddingEngine:
    """
    Генерация embeddings через Ollama
    """

    def __init__(self):

        self.chunks_dir = config.CHUNKS_DIR
        self.output_dir = config.EMBEDDINGS_DIR

        ensure_dir(self.output_dir)

        self.model = "nomic-embed-text"
        self.ollama_url = "http://localhost:11434/api/embeddings"

    # =====================================
    # GENERATE EMBEDDING
    # =====================================

    def generate_embedding(self, text: str):

        payload = {
            "model": self.model,
            "prompt": text
        }

        response = requests.post(
            self.ollama_url,
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.text}")

        data = response.json()

        return data["embedding"]

    # =====================================
    # PROCESS FILE
    # =====================================

    def process_file(self, chunk_file: Path):

        logger.info(f"Embedding файла: {chunk_file.name}")

        with open(chunk_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        embeddings = []

        for chunk in chunks:

            text = chunk["text"]

            embedding = self.generate_embedding(text)

            embeddings.append({
                "chunk_id": chunk["chunk_id"],
                "text": text,
                "embedding": embedding
            })

        output_file = self.output_dir / chunk_file.name

        with open(output_file, "w", encoding="utf-8") as f:

            json.dump(
                embeddings,
                f,
                ensure_ascii=False,
                indent=2
            )

        logger.info(f"Embeddings сохранены: {output_file}")

        return embeddings

    # =====================================
    # PROCESS ALL
    # =====================================

    def process_all(self):

        chunk_files = list(self.chunks_dir.glob("*.json"))

        if not chunk_files:
            logger.warning("Chunks не найдены")
            return []

        results = []

        for chunk_file in chunk_files:

            embeddings = self.process_file(chunk_file)

            results.append(embeddings)

        logger.info("Embedding pipeline завершён")

        return results


# =====================================
# QUICK RUN
# =====================================

def run_embeddings():

    engine = EmbeddingEngine()

    return engine.process_all()