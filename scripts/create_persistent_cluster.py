#!/usr/bin/env python3
"""
Create a persistent Databricks cluster to avoid capacity issues
"""

import requests
from azure.identity import DefaultAzureCredential

WORKSPACE_URL = "https://adb-7405606665021845.5.azuredatabricks.net"
TOKEN = os.environ.get("DATABRICKS_TOKEN", "YOUR_TOKEN_HERE")  # Set via environment variable

def create_cluster():
    """Create a persistent cluster in Databricks"""
    
    url = f"{WORKSPACE_URL}/api/2.0/clusters/create"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "cluster_name": "xrs-nexus-persistent-cluster",
        "spark_version": "13.3.x-scala2.12",
        "node_type_id": "Standard_D3_v2",
        "num_workers": 1,
        "autoscale": {
            "min_workers": 0,
            "max_workers": 2
        },
        "autotermination_minutes": 30,
        "spark_conf": {
            "spark.speculation": "false"
        }
    }
    
    print("Creating persistent Databricks cluster...")
    print(f"Name: {payload['cluster_name']}")
    print(f"Node Type: {payload['node_type_id']}")
    print(f"Workers: {payload['num_workers']}")
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        cluster_id = result.get('cluster_id')
        print(f"\n✅ Cluster created successfully!")
        print(f"Cluster ID: {cluster_id}")
        print(f"\nNow update the ADF linked service to use this cluster:")
        print(f"  - Remove 'newCluster*' properties")
        print(f"  - Add 'existingClusterId': '{cluster_id}'")
        return cluster_id
    else:
        print(f"❌ Failed to create cluster: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    create_cluster()
