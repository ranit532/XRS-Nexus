"""
Lineage Agent: Tracks and calculates data lineage using Neo4j and Cypher queries.
"""
from neo4j import GraphDatabase

class LineageAgent:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_lineage(self, source, target, transformation):
        with self.driver.session() as session:
            session.run(
                "CREATE (s:Source {name: $source})-[:TRANSFORMED_TO {rule: $transformation}]->(t:Target {name: $target})",
                source=source, target=target, transformation=transformation
            )

    def get_lineage(self):
        with self.driver.session() as session:
            result = session.run("MATCH (s:Source)-[r:TRANSFORMED_TO]->(t:Target) RETURN s.name, r.rule, t.name")
            return [record for record in result]
