#!/usr/bin/env python3
"""
Upload Synapse Spark notebooks to workspace
"""

import requests
from azure.identity import DefaultAzureCredential
from azure.mgmt.synapse import SynapseManagementClient

SUBSCRIPTION_ID = "ddfba1ba-a22b-4bb4-b981-033e62bde697"
RESOURCE_GROUP = "xrs-nexus-dev-rg"
WORKSPACE_NAME = "xrs-nexus-dev-synapse-2yd1hw"

def upload_notebook(workspace_dev_endpoint, token, local_path, notebook_name):
    """Upload a notebook to Synapse workspace"""
    url = f"{workspace_dev_endpoint}/notebooks/{notebook_name}?api-version=2020-12-01"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    with open(local_path, 'r') as f:
        notebook_content = f.read()
    
    payload = {
        "name": notebook_name,
        "properties": {
            "nbformat": 4,
            "nbformat_minor": 2,
            "metadata": {
                "language_info": {
                    "name": "python"
                }
            },
            "cells": [
                {
                    "cell_type": "code",
                    "source": notebook_content.split('\n'),
                    "metadata": {},
                    "outputs": [],
                    "execution_count": None
                }
            ]
        }
    }
    
    response = requests.put(url, headers=headers, json=payload)
    
    if response.status_code in [200, 202]:
        print(f"✅ Uploaded: {notebook_name}")
    else:
        print(f"❌ Failed to upload {notebook_name}: {response.status_code}")
        print(response.text)

def main():
    print("Uploading Synapse Spark notebooks...")
    
    # Get workspace dev endpoint
    credential = DefaultAzureCredential()
    synapse_client = SynapseManagementClient(credential, SUBSCRIPTION_ID)
    workspace = synapse_client.workspaces.get(RESOURCE_GROUP, WORKSPACE_NAME)
    workspace_dev_endpoint = f"https://{workspace.connectivity_endpoints['dev']}"
    
    print(f"Workspace Dev Endpoint: {workspace_dev_endpoint}")
    
    # Get access token
    token = credential.get_token("https://dev.azuresynapse.net/.default").token
    
    # Upload notebooks
    notebooks = [
        ("synapse/notebooks/process_bronze.py", "process_bronze"),
        ("synapse/notebooks/process_silver.py", "process_silver")
    ]
    
    for local_path, notebook_name in notebooks:
        upload_notebook(workspace_dev_endpoint, token, local_path, notebook_name)
    
    print("\n✅ All notebooks uploaded!")

if __name__ == "__main__":
    main()
