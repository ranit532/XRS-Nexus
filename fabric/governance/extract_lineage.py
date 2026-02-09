# ==============================================================================
# Fabric Governance - Lineage Extractor
# Description: Queries Fabric REST API to extract artifact lineage.
#              Useful for feeding into Purview or custom metadata catalogs.
# ==============================================================================

import requests
import json
import os

class FabricLineageExtractor:
    def __init__(self, workspace_id, token):
        self.workspace_id = workspace_id
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.fabric.microsoft.com/v1"

    def get_items(self):
        """List all items in the workspace."""
        url = f"{self.base_url}/workspaces/{self.workspace_id}/items"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get('value', [])
        else:
            print(f"Error fetching items: {response.text}")
            return []

    def export_lineage(self, output_file="lineage_graph.json"):
        """Extracts items and builds a simple lineage map."""
        items = self.get_items()
        lineage_map = {
            "workspace_id": self.workspace_id,
            "items": [],
            "relationships": []
        }

        print(f"Found {len(items)} items in workspace.")
        
        for item in items:
            item_info = {
                "id": item.get('id'),
                "type": item.get('type'),
                "displayName": item.get('displayName')
            }
            lineage_map["items"].append(item_info)
            
            # Hypothetical: Extract relationships if available in item definition
            # In real Fabric API, lineage is often a separate scanner API call (PostScanner)
            # This is a simplified representation for the project.
        
        with open(output_file, 'w') as f:
            json.dump(lineage_map, f, indent=4)
        
        print(f"Lineage exported to {output_file}")

if __name__ == "__main__":
    # Env vars would be set by the orchestration pipeline
    WORKSPACE_ID = os.getenv("FABRIC_WORKSPACE_ID", "default-workspace-guid")
    ACCESS_TOKEN = os.getenv("FABRIC_ACCESS_TOKEN", "your-access-token")
    
    extractor = FabricLineageExtractor(WORKSPACE_ID, ACCESS_TOKEN)
    extractor.export_lineage("data/fabric_lineage_export.json")
