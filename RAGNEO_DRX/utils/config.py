import os
from pathlib import Path

class Config:
    """
    Глобальная конфигурация системы GraphRAG
    """

    # ==========================
    # ROOT PATHS
    # ==========================

    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    DATA_DIR = PROJECT_ROOT / "data"

    PDF_DIR = DATA_DIR / "pdf"
    TXT_DIR = DATA_DIR / "txt"
    CHUNKS_DIR = DATA_DIR / "chunks"
    EMBEDDINGS_DIR = DATA_DIR / "embeddings"
    FAISS_DIR = DATA_DIR / "faiss"
    CACHE_DIR = DATA_DIR / "cache"

    LOG_DIR = PROJECT_ROOT / "logs"

    # ==========================
    # VECTOR SETTINGS
    # ==========================

    EMBEDDING_MODEL = "nomic-embed-text"

    EMBEDDING_DIMENSION = 768

    BATCH_SIZE = 32

    TOP_K_RETRIEVAL = 20

    TOP_K_RERANK = 5

    # ==========================
    # LLM SETTINGS
    # ==========================

    OLLAMA_BASE_URL = "http://localhost:11434"

    LLM_MODEL = "mistral"

    MAX_CONTEXT_CHUNKS = 8

    TEMPERATURE = 0.1

    # ==========================
    # NEO4J SETTINGS
    # ==========================

    NEO4J_URI = "bolt://localhost:7687"

    NEO4J_USER = "neo4j"

    NEO4J_PASSWORD = "314a314a"

    # ==========================
    # CHUNKING SETTINGS
    # ==========================

    CHUNK_SIZE = 500

    CHUNK_OVERLAP = 100

    # ==========================
    # FILES
    # ==========================

    FAISS_INDEX_FILE = FAISS_DIR / "index.faiss"

    METADATA_FILE = FAISS_DIR / "metadata.json"

    EMBEDDING_CACHE_FILE = CACHE_DIR / "embedding_cache.pkl"


config = Config()