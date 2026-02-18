import json
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.lineage_graph import LineageGraph

def seed_graph():
    log_path = "data/simulation/etl_lineage_log.json"
    if not os.path.exists(log_path):
        print(f"No logs found at {log_path}")
        return

    graph_db = LineageGraph()
    if not graph_db.driver:
        print("Could not connect to Neo4j. Skipping seeding.")
        return

    print("Clearing existing graph...")
    graph_db.clear_graph()

    print(f"Reading logs from {log_path}...")
    with open(log_path, 'r') as f:
        logs = json.load(f)

    print("Seeding graph...")
    for entry in logs:
        source = entry.get('source')
        target = entry.get('target')
        transformation = entry.get('transformation')
        
        if source and target:
            # Create Nodes
            graph_db.add_node("DataArtifact", source, {"type": "source" if "file" in source else "intermediate"})
            graph_db.add_node("DataArtifact", target, {"type": "target" if "sqlite" in target else "intermediate"})
            
            # Create Edge
            graph_db.add_relationship(source, target, "FLOWS_TO", {"transformation": transformation})
            print(f"Linked {source} -> {target}")

    print("Seeding complete.")
    graph_db.close()

if __name__ == "__main__":
    seed_graph()
