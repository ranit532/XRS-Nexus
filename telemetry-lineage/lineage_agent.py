import logging
import json
from typing import Dict, Any, List, Set

logger = logging.getLogger(__name__)

class LineageAgent:
    """
    Agent responsible for maintaining lineage graphs and performing impact analysis.
    """
    def __init__(self):
        # In a real scenario, this would connect to Purview or a Graph DB
        self.lineage_store = {} 

    def register_lineage(self, source_id: str, target_id: str, transformation_id: str):
        """
        Registers a lineage relationship.
        """
        if source_id not in self.lineage_store:
            self.lineage_store[source_id] = {"downstream": set()}
        
        self.lineage_store[source_id]["downstream"].add(target_id)
        logger.info(f"Registered lineage: {source_id} -> {target_id}")

    def analyze_impact(self, modified_object_id: str) -> Dict[str, Any]:
        """
        Identifies all downstream objects affected by a change in the source object.
        Performs a BFS traversal of the dependency graph.
        
        Args:
            modified_object_id: The ID of the changed source (e.g., SAP_ECC_KNA1).
            
        Returns:
            Dict containing list of impacted assets and depth of impact.
        """
        impacted_assets = set()
        queue = [modified_object_id]
        visited = set()
        
        # Simulated graph for demo purposes if store is empty
        if not self.lineage_store:
             self._populate_demo_graph()

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            # Find downstream
            node = self.lineage_store.get(current)
            if node:
                downstream = node.get("downstream", set())
                for child in downstream:
                    if child not in visited:
                        impacted_assets.add(child)
                        queue.append(child)
                        
        return {
            "source_change": modified_object_id,
            "impacted_count": len(impacted_assets),
            "impacted_assets": list(impacted_assets),
            "risk_level": "HIGH" if len(impacted_assets) > 5 else "LOW"
        }

    def _populate_demo_graph(self):
        """Populate some dummy data for demonstration."""
        # SAP -> Bronze -> Silver -> Gold -> Dashboard
        self.register_lineage("SAP_ECC_KNA1", "LAKE_BRONZE_KNA1", "INGEST_PIPE_001")
        self.register_lineage("LAKE_BRONZE_KNA1", "LAKE_SILVER_CUSTOMER", "CLEANSE_NB_001")
        self.register_lineage("LAKE_SILVER_CUSTOMER", "LAKE_GOLD_SALES_MART", "AGG_NB_002")
        self.register_lineage("LAKE_GOLD_SALES_MART", "PBI_SALES_DASHBOARD", "DATASET_REFRESH")

# @tool
def lineage_impact_tool(modified_object_id: str) -> Dict[str, Any]:
    agent = LineageAgent()
    return agent.analyze_impact(modified_object_id)

if __name__ == "__main__":
    # Test
    print(json.dumps(lineage_impact_tool("SAP_ECC_KNA1"), indent=2))
