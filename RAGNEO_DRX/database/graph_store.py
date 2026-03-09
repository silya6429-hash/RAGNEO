from neo4j import GraphDatabase
from utils.logger import logger


class GraphStore:

    def __init__(self):

        self.uri = "bolt://localhost:7687"
        self.user = "neo4j"
        self.password = "314a314a"

        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )

        logger.info("Подключение к Neo4j установлено")

    # ==================================
    # CLOSE
    # ==================================

    def close(self):

        self.driver.close()

    # ==================================
    # CREATE ENTITY
    # ==================================

    def create_entity(self, name):

        query = """
        MERGE (e:Entity {name: $name})
        RETURN e
        """

        with self.driver.session() as session:

            session.run(query, name=name)

    # ==================================
    # CREATE RELATIONSHIP
    # ==================================

    def create_relation(self, entity1, relation, entity2):

        query = f"""
        MERGE (a:Entity {{name:$e1}})
        MERGE (b:Entity {{name:$e2}})
        MERGE (a)-[:{relation}]->(b)
        """

        with self.driver.session() as session:

            session.run(
                query,
                e1=entity1,
                e2=entity2
            )

    # ==================================
    # GET NEIGHBORS
    # ==================================

    def get_neighbors(self, entity):

        query = """
        MATCH (a:Entity {name:$name})-[r]-(b)
        RETURN b.name AS neighbor
        """

        with self.driver.session() as session:

            result = session.run(query, name=entity)

            return [r["neighbor"] for r in result]
    def search_graph(self, entity, depth=2):
        

        query = f"""
        MATCH (n {{name:$entity}})-[*1..{depth}]-(m)
        RETURN n,r,m LIMIT 20
        """

        with self.driver.session() as session:
            result = session.run(query, entity=entity)

            triples = []

            for record in result:
                triples.append(str(record))

            return triples