"""
Lineage Tracking and Impact Analysis Module
- Tracks field-level lineage across pipelines
- Supports upstream and downstream queries
- Allows "what-if" impact analysis
- Integrates with metadata store (e.g., Cosmos DB, Delta Lake)
"""
from typing import Dict, List, Any, Set

class LineageTracker:
    def __init__(self):
        # In production, use Cosmos DB or Delta Lake; here, use in-memory dict
        self.lineage_graph = {  # node: {field: [(upstream_node, upstream_field)]}
            # Example structure
        }

    def add_lineage(self, pipeline_id: str, mappings: List[Dict[str, Any]]):
        """Add field-level lineage mappings for a pipeline.
        mappings: [{"source": {"node": str, "field": str}, "target": {"node": str, "field": str}}]
        """
        for mapping in mappings:
            tgt_node = mapping['target']['node']
            tgt_field = mapping['target']['field']
            src_node = mapping['source']['node']
            src_field = mapping['source']['field']
            if tgt_node not in self.lineage_graph:
                self.lineage_graph[tgt_node] = {}
            if tgt_field not in self.lineage_graph[tgt_node]:
                self.lineage_graph[tgt_node][tgt_field] = []
            self.lineage_graph[tgt_node][tgt_field].append((src_node, src_field))

    def get_upstream(self, node: str, field: str) -> List[Any]:
        """Return all direct upstream sources for a field."""
        return self.lineage_graph.get(node, {}).get(field, [])

    def get_downstream(self, node: str, field: str) -> List[Any]:
        """Return all direct downstream targets for a field."""
        downstream = []
        for tgt_node, fields in self.lineage_graph.items():
            for tgt_field, sources in fields.items():
                for src_node, src_field in sources:
                    if src_node == node and src_field == field:
                        downstream.append((tgt_node, tgt_field))
        return downstream

    def what_if_impact(self, node: str, field: str) -> Set[Any]:
        """Return all downstream fields impacted by a change to (node, field)."""
        impacted = set()
        to_visit = [(node, field)]
        while to_visit:
            current = to_visit.pop()
            for downstream in self.get_downstream(*current):
                if downstream not in impacted:
                    impacted.add(downstream)
                    to_visit.append(downstream)
        return impacted

    def as_graph_json(self) -> Dict[str, Any]:
        """Return the lineage graph as a JSON-serializable object."""
        nodes = set()
        edges = []
        for tgt_node, fields in self.lineage_graph.items():
            for tgt_field, sources in fields.items():
                nodes.add((tgt_node, tgt_field))
                for src_node, src_field in sources:
                    nodes.add((src_node, src_field))
                    edges.append({
                        "from": {"node": src_node, "field": src_field},
                        "to": {"node": tgt_node, "field": tgt_field}
                    })
        return {
            "nodes": [ {"node": n[0], "field": n[1]} for n in nodes ],
            "edges": edges
        }

# Example usage
if __name__ == "__main__":
    tracker = LineageTracker()
    tracker.add_lineage("pipeline-1", [
        {"source": {"node": "SAP_EKPO", "field": "EBELN"}, "target": {"node": "Lakehouse_PurchaseOrder", "field": "PurchaseOrderId"}},
        {"source": {"node": "SAP_EKPO", "field": "MATNR"}, "target": {"node": "Lakehouse_PurchaseOrder", "field": "MaterialId"}}
    ])
    tracker.add_lineage("pipeline-2", [
        {"source": {"node": "Lakehouse_PurchaseOrder", "field": "PurchaseOrderId"}, "target": {"node": "Analytics_PurchaseOrder", "field": "PO_ID"}}
    ])
    print("Lineage graph:")
    print(tracker.as_graph_json())
    print("Upstream for Analytics_PurchaseOrder.PO_ID:")
    print(tracker.get_upstream("Analytics_PurchaseOrder", "PO_ID"))
    print("Downstream for SAP_EKPO.EBELN:")
    print(tracker.get_downstream("SAP_EKPO", "EBELN"))
    print("What-if impact for SAP_EKPO.EBELN:")
    print(tracker.what_if_impact("SAP_EKPO", "EBELN"))
