"""
AI-driven Logical Flow Generator
- Takes normalized metadata as input
- Determines extraction, transformation, and load steps
- Identifies upstream and downstream dependencies
- Produces a baseline logical execution plan (tech-agnostic)
"""
from typing import Dict, Any, List

class LogicalFlowGenerator:
    def __init__(self):
        self.rules = [
            {
                "name": "SAP CDC Load",
                "match": lambda meta: meta['sourceSystem']['type'] == 'SAP' and meta.get('cdc', {}).get('enabled', False),
                "steps": ["extract_cdc", "transform", "load_incremental"]
            },
            {
                "name": "Salesforce Full Refresh",
                "match": lambda meta: meta['sourceSystem']['type'] == 'Salesforce' and not meta.get('cdc', {}).get('enabled', False),
                "steps": ["extract_full", "transform", "load_full"]
            },
            {
                "name": "Default Full Load",
                "match": lambda meta: True,
                "steps": ["extract_full", "transform", "load_full"]
            }
        ]

    def generate_logical_flow(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        # Determine rule
        for rule in self.rules:
            if rule['match'](metadata):
                selected_rule = rule
                break
        steps = selected_rule['steps']
        # Build nodes and edges
        nodes = []
        edges = []
        node_ids = []
        # Extraction node
        extract_node = {
            "id": "extract",
            "type": "extract",
            "label": f"Extract from {metadata['sourceSystem']['type']}"
        }
        nodes.append(extract_node)
        node_ids.append("extract")
        # Transformation node
        transform_node = {
            "id": "transform",
            "type": "transform",
            "label": "Transform to canonical model"
        }
        nodes.append(transform_node)
        node_ids.append("transform")
        # Load node
        load_node = {
            "id": "load",
            "type": "load",
            "label": "Load to target"
        }
        nodes.append(load_node)
        node_ids.append("load")
        # Edges
        edges.append({"from": "extract", "to": "transform", "step": steps[1]})
        edges.append({"from": "transform", "to": "load", "step": steps[2]})
        # Dependencies
        upstream = metadata.get("dependencies", [])
        downstream = []  # Could be inferred from lineageHints or external config
        logical_flow = {
            "nodes": nodes,
            "edges": edges,
            "upstreamDependencies": upstream,
            "downstreamDependencies": downstream,
            "decisionRule": selected_rule['name']
        }
        return logical_flow

    def explain_decision(self, metadata: Dict[str, Any]) -> str:
        for rule in self.rules:
            if rule['match'](metadata):
                return f"Rule '{rule['name']}' applied based on source type and CDC config."
        return "Default rule applied."

# Example usage
if __name__ == "__main__":
    import json
    with open("../../metadata-ingestion/src/example_sap_metadata.json") as f:
        sap_meta = json.load(f)
    with open("../../metadata-ingestion/src/example_salesforce_metadata.json") as f:
        sf_meta = json.load(f)
    gen = LogicalFlowGenerator()
    sap_flow = gen.generate_logical_flow(sap_meta)
    sf_flow = gen.generate_logical_flow(sf_meta)
    print("SAP CDC Load Example:\n", json.dumps(sap_flow, indent=2))
    print("Salesforce Full Refresh Example:\n", json.dumps(sf_flow, indent=2))
