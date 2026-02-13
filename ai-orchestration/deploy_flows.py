import os
from promptflow.azure import PFClient
from dotenv import load_dotenv

# Load env (though we will largely rely on az login)
load_dotenv("../.env")

# Azure Configuration
SUBSCRIPTION_ID = "ddfba1ba-a22b-4bb4-b981-033e62bde697"
RESOURCE_GROUP = "xrs-nexus-dev-rg"
WORKSPACE_NAME = "xrs-nexus-dev-ai-project"

def deploy_flow(pf_client, flow_path, flow_name):
    print(f"\n--- Deploying {flow_name} ---")
    try:
        # Create or Update the flow in Azure AI Project
        # Note: 'create_or_update' uploads the flow definition to the cloud
        flow = pf_client.flows.create_or_update(
            flow=flow_path,
            display_name=flow_name,
            type="chat" # Most of our flows are chat/standard
        )
        print(f"✅ Successfully deployed {flow_name}")
        print(f"Flow ID: {flow.name}")
        print(f"Portal URL: https://ai.azure.com/project/flows/{flow.name}?wsid=/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}/providers/Microsoft.MachineLearningServices/workspaces/{WORKSPACE_NAME}")
    except Exception as e:
        print(f"❌ Failed to deploy {flow_name}")
        print(e)

from azure.identity import DefaultAzureCredential

# ...

if __name__ == "__main__":
    print(f"Connecting to Azure AI Project: {WORKSPACE_NAME}...")
    
    # Initialize Azure PF Client
    credential = DefaultAzureCredential()
    pf = PFClient(
        credential=credential,
        subscription_id=SUBSCRIPTION_ID,
        resource_group_name=RESOURCE_GROUP,
        workspace_name=WORKSPACE_NAME
    )
    
    # List of flows to deploy
    flows = [
        ("flows/advanced_schema_mapping", "Advanced Schema Mapping"),
        ("flows/context_aware_nl2sql", "Context-Aware NL2SQL"),
        ("flows/pii_redaction", "Intelligent PII Redaction"),
        ("flows/pii_detection", "PII Detection"),
        ("flows/error_rca", "Automated Error RCA"),
        ("flows/dq_rules", "Natural Language DQ Rules"),
        ("flows/adf_data_validation", "ADF Data Validation")
    ]
    
    for path, name in flows:
        deploy_flow(pf, path, name)
        
    print("\n🎉 Deployment Script Complete!")
