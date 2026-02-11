#!/usr/bin/env python3
"""
Setup ADF Pipelines for Synapse Spark
"""

from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import *

SUBSCRIPTION_ID = "ddfba1ba-a22b-4bb4-b981-033e62bde697"
RESOURCE_GROUP = "xrs-nexus-dev-rg"
DATA_FACTORY_NAME = "xrs-nexus-dev-adf-2yd1hw"
SYNAPSE_WORKSPACE_NAME = "xrs-nexus-dev-synapse-2yd1hw"
SPARK_POOL_NAME = "sparkpool01"
STORAGE_ACCOUNT_NAME = "xrsnexusdevstg2yd1hw"

def create_synapse_linked_service(client):
    """Create Azure Synapse linked service"""
    print("Creating Synapse Linked Service...")
    
    ls_name = "LS_Synapse"
    
    # Get Synapse workspace endpoint
    from azure.mgmt.synapse import SynapseManagementClient
    credential = DefaultAzureCredential()
    synapse_client = SynapseManagementClient(credential, SUBSCRIPTION_ID)
    workspace = synapse_client.workspaces.get(RESOURCE_GROUP, SYNAPSE_WORKSPACE_NAME)
    workspace_endpoint = f"https://{workspace.connectivity_endpoints['dev']}"
    
    ls_synapse = LinkedServiceResource(
        properties=AzureSynapseArtifactsLinkedService(
            endpoint=workspace_endpoint,
            authentication="MSI"
        )
    )
    
    ls = client.linked_services.create_or_update(
        RESOURCE_GROUP, DATA_FACTORY_NAME, ls_name, ls_synapse
    )
    print(f"✅ Created Linked Service: {ls_name}")
    return ls_name

def create_synapse_pipeline(client, adls_ls_name, synapse_ls_name):
    """Create ADF pipeline using Synapse Spark"""
    print("Creating Synapse Spark Pipeline...")
    
    pipeline_name = "PL_ETL_Synapse_Bronze_to_Gold"
    
    # Activity 1: Bronze to Silver
    activity1 = SynapseNotebookActivity(
        name="Process_Bronze_to_Silver_Synapse",
        notebook=SynapseNotebookReference(
            type="NotebookReference",
            reference_name="process_bronze"
        ),
        spark_pool=BigDataPoolReference(
            type="BigDataPoolReference",
            reference_name=SPARK_POOL_NAME
        ),
        linked_service_name=LinkedServiceReference(
            type="LinkedServiceReference",
            reference_name=synapse_ls_name
        ),
        parameters={
            "input_path": f"abfss://bronze@{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
            "output_path": f"abfss://silver@{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net"
        }
    )
    
    # Activity 2: Silver to Gold
    activity2 = SynapseNotebookActivity(
        name="Process_Silver_to_Gold_Synapse",
        notebook=SynapseNotebookReference(
            type="NotebookReference",
            reference_name="process_silver"
        ),
        spark_pool=BigDataPoolReference(
            type="BigDataPoolReference",
            reference_name=SPARK_POOL_NAME
        ),
        linked_service_name=LinkedServiceReference(
            type="LinkedServiceReference",
            reference_name=synapse_ls_name
        ),
        parameters={
            "input_path": f"abfss://silver@{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
            "output_path": f"abfss://gold@{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net"
        },
        depends_on=[DependencyReference(activity="Process_Bronze_to_Silver_Synapse")]
    )
    
    pipeline = PipelineResource(
        activities=[activity1, activity2]
    )
    
    p = client.pipelines.create_or_update(
        RESOURCE_GROUP, DATA_FACTORY_NAME, pipeline_name, pipeline
    )
    print(f"✅ Created Pipeline: {pipeline_name}")
    return pipeline_name

def main():
    print("=" * 60)
    print("XRS-Nexus: ADF + Synapse Spark Setup")
    print("=" * 60)
    
    credential = DefaultAzureCredential()
    client = DataFactoryManagementClient(credential, SUBSCRIPTION_ID)
    
    # Create ADLS Gen2 linked service (reuse existing)
    adls_ls_name = "LS_ADLS_Gen2"
    
    # Create Synapse linked service
    synapse_ls_name = create_synapse_linked_service(client)
    
    # Create pipeline
    pipeline_name = create_synapse_pipeline(client, adls_ls_name, synapse_ls_name)
    
    print("\n" + "=" * 60)
    print("✅ Synapse ADF Setup Complete!")
    print("=" * 60)
    print(f"\nCreated Resources:")
    print(f"  - Linked Service: {synapse_ls_name}")
    print(f"  - Pipeline: {pipeline_name}")
    print(f"\nNext Steps:")
    print(f"  1. Upload notebooks to Synapse workspace")
    print(f"  2. Run pipeline: az datafactory pipeline create-run \\")
    print(f"       --factory-name {DATA_FACTORY_NAME} \\")
    print(f"       --name {pipeline_name}")

if __name__ == "__main__":
    main()
