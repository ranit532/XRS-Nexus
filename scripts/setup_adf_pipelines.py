#!/usr/bin/env python3
"""
Setup Azure Data Factory Pipelines for XRS-Nexus Alternative Architecture
Creates linked services, datasets, and pipelines to orchestrate ETL workflows
"""

import os
import sys
from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import *

# Configuration
SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID", "ddfba1ba-a22b-4bb4-b981-033e62bde697")
RESOURCE_GROUP = "xrs-nexus-dev-rg"
DATA_FACTORY_NAME = "xrs-nexus-dev-adf-2yd1hw"
STORAGE_ACCOUNT_NAME = "xrsnexusdevstg2yd1hw"
DATABRICKS_WORKSPACE_NAME = "xrs-nexus-dev-dbw-2yd1hw"

def get_adf_client():
    """Initialize ADF client with DefaultAzureCredential"""
    credential = DefaultAzureCredential()
    return DataFactoryManagementClient(credential, SUBSCRIPTION_ID)

def create_adls_linked_service(client):
    """Create ADLS Gen2 linked service"""
    print("Creating ADLS Gen2 Linked Service...")
    
    ls_name = "LS_ADLS_Gen2"
    ls_azure_storage = LinkedServiceResource(
        properties=AzureBlobFSLinkedService(
            url=f"https://{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net"
        )
    )
    
    ls = client.linked_services.create_or_update(
        RESOURCE_GROUP, DATA_FACTORY_NAME, ls_name, ls_azure_storage
    )
    print(f"✅ Created Linked Service: {ls_name}")
    return ls_name

def create_databricks_linked_service(client):
    """Create Azure Databricks linked service"""
    print("Creating Databricks Linked Service...")
    
    # Get Databricks workspace URL
    from azure.mgmt.databricks import AzureDatabricksManagementClient
    credential = DefaultAzureCredential()
    dbw_client = AzureDatabricksManagementClient(credential, SUBSCRIPTION_ID)
    workspace = dbw_client.workspaces.get(RESOURCE_GROUP, DATABRICKS_WORKSPACE_NAME)
    workspace_url = f"https://{workspace.workspace_url}"
    
    ls_name = "LS_Databricks"
    
    # Create linked service with new cluster configuration
    ls_databricks = LinkedServiceResource(
        properties=AzureDatabricksLinkedService(
            domain=workspace_url,
            new_cluster_node_type="Standard_DS3_v2",
            new_cluster_num_of_worker="1",
            new_cluster_spark_version="13.3.x-scala2.12",
            new_cluster_spark_conf={
                "spark.speculation": "false"
            },
            new_cluster_custom_tags={
                "project": "xrs-nexus"
            }
        )
    )
    
    ls = client.linked_services.create_or_update(
        RESOURCE_GROUP, DATA_FACTORY_NAME, ls_name, ls_databricks
    )
    print(f"✅ Created Linked Service: {ls_name}")
    return ls_name

def create_datasets(client, adls_ls_name):
    """Create datasets for Bronze, Silver, and Gold layers"""
    print("Creating Datasets...")
    
    datasets = {}
    
    for layer in ["bronze", "silver", "gold"]:
        ds_name = f"DS_{layer.capitalize()}"
        
        ds = DatasetResource(
            properties=DelimitedTextDataset(
                linked_service_name=LinkedServiceReference(
                    type="LinkedServiceReference",
                    reference_name=adls_ls_name
                ),
                location=AzureBlobFSLocation(
                    file_system=layer
                )
            )
        )
        
        client.datasets.create_or_update(
            RESOURCE_GROUP, DATA_FACTORY_NAME, ds_name, ds
        )
        datasets[layer] = ds_name
        print(f"✅ Created Dataset: {ds_name}")
    
    return datasets

def create_etl_pipeline(client, datasets, databricks_ls_name):
    """Create main ETL pipeline"""
    print("Creating ETL Pipeline...")
    
    pipeline_name = "PL_ETL_Bronze_to_Gold"
    
    # Activity 1: Process Bronze to Silver (Databricks Notebook)
    activity_bronze_silver = DatabricksNotebookActivity(
        name="Process_Bronze_to_Silver",
        linked_service_name=LinkedServiceReference(
            type="LinkedServiceReference",
            reference_name=databricks_ls_name
        ),
        notebook_path="/Workspace/XRS-Nexus/process_bronze",
        base_parameters={
            "input_path": f"abfss://bronze@{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net/",
            "output_path": f"abfss://silver@{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net/"
        }
    )
    
    # Activity 2: Process Silver to Gold (Databricks Notebook)
    activity_silver_gold = DatabricksNotebookActivity(
        name="Process_Silver_to_Gold",
        linked_service_name=LinkedServiceReference(
            type="LinkedServiceReference",
            reference_name=databricks_ls_name
        ),
        notebook_path="/Workspace/XRS-Nexus/process_silver",
        base_parameters={
            "input_path": f"abfss://silver@{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net/",
            "output_path": f"abfss://gold@{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net/"
        },
        depends_on=[ActivityDependency(
            activity=activity_bronze_silver.name,
            dependency_conditions=["Succeeded"]
        )]
    )
    
    # Create pipeline
    pipeline = PipelineResource(
        activities=[activity_bronze_silver, activity_silver_gold],
        parameters={
            "triggerTime": ParameterSpecification(type="String")
        }
    )
    
    client.pipelines.create_or_update(
        RESOURCE_GROUP, DATA_FACTORY_NAME, pipeline_name, pipeline
    )
    print(f"✅ Created Pipeline: {pipeline_name}")
    return pipeline_name

def create_prompt_flow_integration_pipeline(client, databricks_ls_name):
    """Create pipeline that integrates with Prompt Flow"""
    print("Creating Prompt Flow Integration Pipeline...")
    
    pipeline_name = "PL_AI_Orchestration"
    
    # Activity: Run AI Orchestration (Databricks Notebook calling Prompt Flow)
    activity_ai = DatabricksNotebookActivity(
        name="Run_AI_Orchestration",
        linked_service_name=LinkedServiceReference(
            type="LinkedServiceReference",
            reference_name=databricks_ls_name
        ),
        notebook_path="/Workspace/XRS-Nexus/ai_orchestration",
        base_parameters={
            "storage_account": STORAGE_ACCOUNT_NAME,
            "bronze_path": f"abfss://bronze@{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net/"
        }
    )
    
    pipeline = PipelineResource(
        activities=[activity_ai]
    )
    
    client.pipelines.create_or_update(
        RESOURCE_GROUP, DATA_FACTORY_NAME, pipeline_name, pipeline
    )
    print(f"✅ Created Pipeline: {pipeline_name}")
    return pipeline_name

def main():
    print("=" * 60)
    print("XRS-Nexus: ADF Pipeline Setup")
    print("=" * 60)
    
    try:
        # Initialize client
        client = get_adf_client()
        
        # Create linked services
        adls_ls = create_adls_linked_service(client)
        databricks_ls = create_databricks_linked_service(client)
        
        # Create datasets
        datasets = create_datasets(client, adls_ls)
        
        # Create pipelines
        etl_pipeline = create_etl_pipeline(client, datasets, databricks_ls)
        ai_pipeline = create_prompt_flow_integration_pipeline(client, databricks_ls)
        
        print("\n" + "=" * 60)
        print("✅ ADF Setup Complete!")
        print("=" * 60)
        print(f"\nCreated Resources:")
        print(f"  - Linked Services: {adls_ls}, {databricks_ls}")
        print(f"  - Datasets: {', '.join(datasets.values())}")
        print(f"  - Pipelines: {etl_pipeline}, {ai_pipeline}")
        print(f"\nNext Steps:")
        print(f"  1. Upload Databricks notebooks to workspace")
        print(f"  2. Run pipeline: az datafactory pipeline create-run \\")
        print(f"       --factory-name {DATA_FACTORY_NAME} \\")
        print(f"       --name {etl_pipeline}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
