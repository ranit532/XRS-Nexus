import os
import sys
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.lineage_graph import LineageGraph

def generate_mermaid():
    output_path = "lineage_graph.mmd"
    mermaid_lines = ["graph TD"]
    
    # Try Neo4j first
    graph_db = LineageGraph()
    if graph_db.driver:
        print("Connected to Neo4j. Fetching graph data...")
        query = "MATCH (n)-[r]->(m) RETURN n.name, type(r), m.name"
        with graph_db.driver.session() as session:
            results = session.run(query)
            for record in results:
                source = record["n.name"]
                target = record["m.name"]
                rel = record["type(r)"]
                
                s_id = sanitize(source)
                t_id = sanitize(target)
                mermaid_lines.append(f"    {s_id}[\"{source}\"] -- {rel} --> {t_id}[\"{target}\"]")
        graph_db.close()
    else:
        print("Neo4j unavailable. Falling back to ETL logs for visualization...")
        log_path = "data/simulation/etl_lineage_log.json"
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                logs = json.load(f)
            for entry in logs:
                source = entry.get('source')
                target = entry.get('target')
                # Transformation becomes the edge label
                transformation = entry.get('transformation', 'FLOWS_TO')
                # Shorten transformation for display
                rel_label = "FLOWS_TO"
                
                s_id = sanitize(source)
                t_id = sanitize(target)
                mermaid_lines.append(f"    {s_id}[\"{source}\"] -- {rel_label} --> {t_id}[\"{target}\"]")
        else:
            print("No ETL logs found to generate graph.")
            return

    with open(output_path, "w") as f:
        f.write("\n".join(mermaid_lines))
    
    print(f"Mermaid graph saved to {output_path}")

def sanitize(name):
    return name.replace(" ", "_").replace("/", "_").replace(".", "_").replace(":", "_").replace("-", "_")

if __name__ == "__main__":
    generate_mermaid()
