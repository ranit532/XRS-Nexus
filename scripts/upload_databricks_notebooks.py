#!/usr/bin/env python3
"""
Upload Databricks notebooks to workspace
"""

import os
import base64
from azure.identity import DefaultAzureCredential
from azure.mgmt.databricks import AzureDatabricksManagementClient
import requests

SUBSCRIPTION_ID = "ddfba1ba-a22b-4bb4-b981-033e62bde697"
RESOURCE_GROUP = "xrs-nexus-dev-rg"
WORKSPACE_NAME = "xrs-nexus-dev-dbw-2yd1hw"

def get_databricks_token():
    """Get Databricks access token using Azure AD"""
    credential = DefaultAzureCredential()
    token = credential.get_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default")  # Databricks resource ID
    return token.token

def upload_notebook(workspace_url, token, local_path, remote_path):
    """Upload a notebook to Databricks workspace"""
    
    # Read notebook content
    with open(local_path, 'r') as f:
        content = f.read()
    
    # Encode content
    content_b64 = base64.b64encode(content.encode()).decode()
    
    # Upload via Workspace API
    url = f"{workspace_url}/api/2.0/workspace/import"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "path": remote_path,
        "format": "SOURCE",
        "language": "PYTHON",
        "content": content_b64,
        "overwrite": True
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        print(f"✅ Uploaded: {remote_path}")
    else:
        print(f"❌ Failed to upload {remote_path}: {response.text}")

def create_folder(workspace_url, token, folder_path):
    """Create a folder in Databricks workspace"""
    url = f"{workspace_url}/api/2.0/workspace/mkdirs"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {"path": folder_path}
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        print(f"✅ Created folder: {folder_path}")
    else:
        print(f"⚠️  Folder creation response: {response.text}")

def main():
    print("Uploading Databricks notebooks...")
    
    # Get workspace URL
    credential = DefaultAzureCredential()
    dbw_client = AzureDatabricksManagementClient(credential, SUBSCRIPTION_ID)
    workspace = dbw_client.workspaces.get(RESOURCE_GROUP, WORKSPACE_NAME)
    workspace_url = f"https://{workspace.workspace_url}"
    
    print(f"Workspace URL: {workspace_url}")
    
    # Get token
    token = get_databricks_token()
    
    # Create parent folder
    create_folder(workspace_url, token, "/Workspace/XRS-Nexus")
    
    # Upload notebooks
    notebooks = [
        ("databricks/notebooks/process_bronze.py", "/Workspace/XRS-Nexus/process_bronze"),
        ("databricks/notebooks/process_silver.py", "/Workspace/XRS-Nexus/process_silver"),
        ("databricks/notebooks/ai_orchestration.py", "/Workspace/XRS-Nexus/ai_orchestration")
    ]
    
    for local_path, remote_path in notebooks:
        upload_notebook(workspace_url, token, local_path, remote_path)
    
    print("\n✅ All notebooks uploaded!")

if __name__ == "__main__":
    main()
