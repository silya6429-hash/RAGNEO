from database.graph_store import GraphStore
from utils.logger import logger


class GraphRetriever:

    def __init__(self):

        self.graph = GraphStore()

    # ==================================
    # EXTRACT ENTITIES FROM QUESTION
    # ==================================

    def extract_entities(self, question):

        words = question.split()

        entities = []

        for w in words:

            if w[0].isupper():
                entities.append(w)

        return entities

    # ==================================
    # GRAPH SEARCH
    # ==================================

    def search(self, question):

        entities = self.extract_entities(question)

        logger.info(f"Entities из вопроса: {entities}")

        graph_context = []

        for entity in entities:

            neighbors = self.graph.get_neighbors(entity)

            for n in neighbors:

                graph_context.append(
                    f"{entity} связан с {n}"
                )

        return graph_context