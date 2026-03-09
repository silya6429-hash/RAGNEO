import json

from utils.logger import logger
from database.graph_store import GraphStore
from rag.llm_interface import LLMInterface


class GraphExtractor:

    def __init__(self):

        self.graph = GraphStore()
        self.llm = LLMInterface()

    # ==================================
    # EXTRACT RELATIONS
    # ==================================

    def extract_relations(self, text):

        prompt = f"""
Извлеки сущности и отношения из текста.

Формат ответа JSON:

[
  {{"entity1":"...", "relation":"...", "entity2":"..."}}
]

Текст:
{text}
"""

        response = self.llm.generate(prompt, "")

        try:

            relations = json.loads(response)

        except Exception:

            logger.warning("Не удалось распарсить JSON")

            relations = []

        return relations

    # ==================================
    # BUILD GRAPH
    # ==================================

    def process_chunk(self, text):

        relations = self.extract_relations(text)

        logger.info(f"Найдено связей: {len(relations)}")

        for rel in relations:
            
            e1 = rel.get("entity1")
            r = rel.get("relation")
            e2 = rel.get("entity2")

            # проверяем что значения существуют
            if not e1 or not r or not e2:
                continue

            # проверяем что это строки
            if not isinstance(e1, str) or not isinstance(r, str) or not isinstance(e2, str):
                continue

            e1 = e1.strip()
            e2 = e2.strip()
            r = r.strip().replace(" ", "_").upper()
            # пропускаем пустые строки
            if not e1 or not r or not e2:
                continue

            self.graph.create_relation(e1, r, e2)