from neo4j import GraphDatabase
import os

class LineageGraph:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        try:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            self.verify_connection()
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def verify_connection(self):
        if self.driver:
            self.driver.verify_connectivity()
            print("Connected to Neo4j.")

    def add_node(self, label, name, properties=None):
        if not self.driver: return None
        if properties is None: properties = {}
        
        query = (
            f"MERGE (n:{label} {{name: $name}}) "
            "SET n += $properties "
            "RETURN n"
        )
        with self.driver.session() as session:
            result = session.run(query, name=name, properties=properties)
            return result.single()[0]

    def add_relationship(self, from_name, to_name, relation_type, properties=None):
        if not self.driver: return None
        if properties is None: properties = {}

        query = (
            "MATCH (a), (b) "
            "WHERE a.name = $from_name AND b.name = $to_name "
            f"MERGE (a)-[r:{relation_type}]->(b) "
            "SET r += $properties "
            "RETURN type(r)"
        )
        with self.driver.session() as session:
            result = session.run(query, from_name=from_name, to_name=to_name, properties=properties)
            return result.single()

    def get_lineage(self, node_name):
        if not self.driver: return []
        query = (
            "MATCH path = (start {name: $node_name})-[*]-(end) "
            "RETURN path"
        )
        with self.driver.session() as session:
            result = session.run(query, node_name=node_name)
            return [record["path"] for record in result]

    def clear_graph(self):
        if not self.driver: return
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Graph cleared.")
