import json
import hashlib
from pathlib import Path
from typing import List, Dict

import spacy

from utils.config import config
from utils.logger import logger
from utils.helpers import ensure_dir


class SemanticChunker:
    """
    Семантический chunker для RAG
    """

    def __init__(self):

        logger.info("Загрузка spaCy модели")

        self.nlp = spacy.load("ru_core_news_sm")

        self.input_dir = config.TXT_DIR
        self.output_dir = config.CHUNKS_DIR

        ensure_dir(self.output_dir)

        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP

    # =========================================
    # SENTENCE PARSING
    # =========================================

    def split_sentences(self, text: str) -> List[str]:

        doc = self.nlp(text)

        sentences = []

        for sent in doc.sents:
            s = sent.text.strip()

            if len(s) > 0:
                sentences.append(s)

        return sentences

    # =========================================
    # BUILD CHUNKS
    # =========================================

    def build_chunks(self, sentences: List[str]) -> List[str]:

        chunks = []

        current_chunk = []
        current_length = 0

        for sentence in sentences:

            sent_len = len(sentence)

            if current_length + sent_len <= self.chunk_size:

                current_chunk.append(sentence)
                current_length += sent_len + 1

            else:

                chunks.append(" ".join(current_chunk))

                # overlap
                overlap = []

                overlap_length = 0

                for s in reversed(current_chunk):

                    s_len = len(s)

                    if overlap_length + s_len <= self.chunk_overlap:
                        overlap.insert(0, s)
                        overlap_length += s_len
                    else:
                        break

                current_chunk = overlap + [sentence]
                current_length = overlap_length + sent_len

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    # =========================================
    # METADATA EXTRACTION
    # =========================================

    def extract_metadata(self, text: str, chunk_index: int, document: str):

        doc = self.nlp(text)

        entities = []

        for ent in doc.ents:

            entities.append({
                "text": ent.text,
                "label": ent.label_
            })

        keywords = []

        for token in doc:

            if token.pos_ in ["NOUN", "PROPN", "ADJ"] and not token.is_stop:

                word = token.lemma_.lower()

                if len(word) > 2:
                    keywords.append(word)

        keywords = list(set(keywords))[:10]

        chunk_id = hashlib.md5(
            f"{document}_{chunk_index}_{text[:100]}".encode()
        ).hexdigest()

        metadata = {

            "chunk_id": chunk_id,
            "document": document,
            "chunk_index": chunk_index,
            "text": text,
            "entities": entities,
            "keywords": keywords,
            "length": len(text)
        }

        return metadata

    # =========================================
    # PROCESS FILE
    # =========================================

    def process_file(self, txt_path: Path):

        logger.info(f"Chunking файла: {txt_path.name}")

        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()

        sentences = self.split_sentences(text)

        logger.info(f"Найдено предложений: {len(sentences)}")

        chunks = self.build_chunks(sentences)

        logger.info(f"Создано чанков: {len(chunks)}")

        document = txt_path.stem

        chunk_objects = []

        for i, chunk_text in enumerate(chunks):

            metadata = self.extract_metadata(
                chunk_text,
                i,
                document
            )

            chunk_objects.append(metadata)

        output_path = self.output_dir / f"{document}.json"

        with open(output_path, "w", encoding="utf-8") as f:

            json.dump(
                chunk_objects,
                f,
                ensure_ascii=False,
                indent=2
            )

        logger.info(f"Chunks сохранены: {output_path}")

        return chunk_objects

    # =========================================
    # PROCESS ALL
    # =========================================

    def process_all(self):

        txt_files = list(self.input_dir.glob("*.txt"))

        if not txt_files:

            logger.warning("TXT файлы не найдены")

            return []

        results = []

        for txt_file in txt_files:

            chunks = self.process_file(txt_file)

            results.append(chunks)

        logger.info("Chunking завершён")

        return results


# =========================================
# QUICK RUN
# =========================================

def run_chunking():

    chunker = SemanticChunker()

    return chunker.process_all()