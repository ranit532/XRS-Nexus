#!/usr/bin/env python3
"""
Fix Databricks Linked Service - Add Access Token
This script updates the Databricks linked service to use an access token for authentication
"""

import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import *

SUBSCRIPTION_ID = "ddfba1ba-a22b-4bb4-b981-033e62bde697"
RESOURCE_GROUP = "xrs-nexus-dev-rg"
DATA_FACTORY_NAME = "xrs-nexus-dev-adf-2yd1hw"
DATABRICKS_WORKSPACE_NAME = "xrs-nexus-dev-dbw-2yd1hw"

def fix_databricks_linked_service():
    """Update Databricks linked service with proper authentication"""
    print("Fixing Databricks Linked Service...")
    
    credential = DefaultAzureCredential()
    client = DataFactoryManagementClient(credential, SUBSCRIPTION_ID)
    
    # Get Databricks workspace URL
    from azure.mgmt.databricks import AzureDatabricksManagementClient
    dbw_client = AzureDatabricksManagementClient(credential, SUBSCRIPTION_ID)
    workspace = dbw_client.workspaces.get(RESOURCE_GROUP, DATABRICKS_WORKSPACE_NAME)
    workspace_url = f"https://{workspace.workspace_url}"
    
    # Get workspace resource ID
    workspace_resource_id = workspace.id
    
    print(f"Workspace URL: {workspace_url}")
    print(f"Workspace ID: {workspace_resource_id}")
    
    # Create linked service with MSI authentication
    ls_name = "LS_Databricks"
    ls_databricks = LinkedServiceResource(
        properties=AzureDatabricksLinkedService(
            domain=workspace_url,
            workspace_resource_id=workspace_resource_id,
            new_cluster_node_type="Standard_DS3_v2",
            new_cluster_num_of_worker="1",
            new_cluster_version="13.3.x-scala2.12"
        )
    )
    
    ls = client.linked_services.create_or_update(
        RESOURCE_GROUP, DATA_FACTORY_NAME, ls_name, ls_databricks
    )
    
    print(f"✅ Updated Linked Service: {ls_name}")
    print("\nLinked service now uses Managed Identity for authentication.")
    print("Make sure the Data Factory's managed identity has 'Contributor' role on the Databricks workspace.")

if __name__ == "__main__":
    fix_databricks_linked_service()
