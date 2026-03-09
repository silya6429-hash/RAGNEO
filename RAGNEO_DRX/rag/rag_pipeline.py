import json

from rag.retriever import Retriever
from rag.llm_interface import LLMInterface
from rag.reranker import Reranker
from rag.graph_retriever import GraphRetriever

from utils.logger import logger


class RAGPipeline:
    """
    Основной RAG pipeline
    """

    def __init__(self):

        logger.info("Инициализация RAG Pipeline")

        self.retriever = Retriever()
        #self.reranker = Reranker()
        self.llm = LLMInterface()
        self.graph_retriever = GraphRetriever()

    # ==================================
    # ENTITY EXTRACTION
    # ==================================

    def extract_entities(self, question: str):

        prompt = f"""
Extract key entities from the question.

Return ONLY JSON list.

Example:
["entity1","entity2"]

Question:
{question}
"""

        try:
            response = self.llm.generate(prompt, "")

            entities = json.loads(response)

            if isinstance(entities, list):
                return entities

        except Exception as e:
            logger.warning(f"Ошибка извлечения сущностей: {e}")

        return []

    # ==================================
    # ASK QUESTION
    # ==================================

    def ask(self, question: str):

        logger.info(f"Получен вопрос: {question}")

        # 1. Vector поиск
        results = self.retriever.search(question)

        logger.info(f"Найдено чанков: {len(results)}")

        # 2. Reranking
        #reranked = self.reranker.rerank(question, results)
        reranked = results
        logger.info("Reranking завершён")

        # 3. Формируем vector context
        vector_context = "\n\n".join(
            [chunk["text"] for chunk in reranked[:2]] #было reranked[:3]]
        )

        # ==================================
        # GRAPH RETRIEVAL (NEW)
        # ==================================

        entities = self.extract_entities(question)

        logger.info(f"Извлечены сущности: {entities}")

        graph_context = []

        for entity in entities:

            try:
                triples = self.graph_retriever.search(entity)

                graph_context.extend(triples)

            except Exception as e:
                logger.warning(f"Ошибка graph retrieval: {e}")

        graph_text = "\n".join(graph_context)

        # ==================================
        # FINAL CONTEXT
        # ==================================

        context = vector_context + "\n\nGRAPH KNOWLEDGE:\n" + graph_text

        logger.info("Контекст сформирован")

        # 4. Генерация ответа
        answer = self.llm.generate(question, context)

        logger.info("Ответ сгенерирован")

        return {
            "question": question,
            "context": context,
            "answer": answer
        }