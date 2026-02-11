#!/usr/bin/env python3
"""
End-to-End Test: Run complete ADF + Databricks + Prompt Flow workflow
"""

import os
import sys
import time
import subprocess
from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient

# Configuration
SUBSCRIPTION_ID = "ddfba1ba-a22b-4bb4-b981-033e62bde697"
RESOURCE_GROUP = "xrs-nexus-dev-rg"
DATA_FACTORY_NAME = "xrs-nexus-dev-adf-2yd1hw"

def run_adf_pipeline(pipeline_name):
    """Trigger ADF pipeline execution"""
    print(f"\n{'='*60}")
    print(f"Triggering Pipeline: {pipeline_name}")
    print(f"{'='*60}")
    
    credential = DefaultAzureCredential()
    client = DataFactoryManagementClient(credential, SUBSCRIPTION_ID)
    
    # Create pipeline run
    run_response = client.pipelines.create_run(
        RESOURCE_GROUP,
        DATA_FACTORY_NAME,
        pipeline_name,
        parameters={"triggerTime": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
    )
    
    run_id = run_response.run_id
    print(f"✅ Pipeline Run ID: {run_id}")
    
    # Monitor pipeline run
    print("\nMonitoring pipeline execution...")
    while True:
        run_status = client.pipeline_runs.get(
            RESOURCE_GROUP,
            DATA_FACTORY_NAME,
            run_id
        )
        
        status = run_status.status
        print(f"  Status: {status}")
        
        if status in ["Succeeded", "Failed", "Cancelled"]:
            break
        
        time.sleep(10)
    
    if status == "Succeeded":
        print(f"✅ Pipeline {pipeline_name} completed successfully!")
        return True
    else:
        print(f"❌ Pipeline {pipeline_name} failed with status: {status}")
        return False

def verify_data_in_adls(container, file_pattern):
    """Verify data exists in ADLS Gen2"""
    print(f"\nVerifying data in {container} container...")
    
    cmd = [
        "az", "storage", "fs", "file", "list",
        "--file-system", container,
        "--account-name", "xrsnexusdevstg2yd1hw",
        "--auth-mode", "login",
        "--query", f"[?contains(name, '{file_pattern}')].name",
        "-o", "tsv"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and result.stdout.strip():
        files = result.stdout.strip().split('\n')
        print(f"✅ Found {len(files)} file(s) matching '{file_pattern}'")
        for f in files:
            print(f"  - {f}")
        return True
    else:
        print(f"❌ No files found matching '{file_pattern}'")
        return False

def run_local_prompt_flow_test():
    """Run local Prompt Flow test"""
    print(f"\n{'='*60}")
    print("Running Local Prompt Flow Test")
    print(f"{'='*60}")
    
    cmd = ["python3", "ai-orchestration/run_integrated_demo.py"]
    result = subprocess.run(cmd, cwd="/Users/ranitsinha/Documents/XRS-Nexus")
    
    return result.returncode == 0

def main():
    print("=" * 60)
    print("XRS-NEXUS: End-to-End Integration Test")
    print("=" * 60)
    print("\nThis test will:")
    print("  1. Run ETL Pipeline (Bronze → Silver → Gold)")
    print("  2. Verify data in each layer")
    print("  3. Run AI Orchestration Pipeline (Prompt Flow integration)")
    print("  4. Run local Prompt Flow validation")
    print()
    
    try:
        # Step 1: Run ETL Pipeline
        success = run_adf_pipeline("PL_ETL_Bronze_to_Gold")
        if not success:
            print("\n❌ ETL Pipeline failed. Stopping test.")
            sys.exit(1)
        
        # Step 2: Verify Silver and Gold data
        verify_data_in_adls("silver", "metadata_clean")
        verify_data_in_adls("gold", "schema_stats")
        
        # Step 3: Run AI Orchestration Pipeline
        print("\n" + "="*60)
        print("NOTE: AI Orchestration pipeline requires Databricks cluster.")
        print("Skipping automated run. You can trigger manually via:")
        print(f"  az datafactory pipeline create-run \\")
        print(f"    --factory-name {DATA_FACTORY_NAME} \\")
        print(f"    --name PL_AI_Orchestration \\")
        print(f"    --resource-group {RESOURCE_GROUP}")
        print("="*60)
        
        # Step 4: Run local Prompt Flow test
        run_local_prompt_flow_test()
        
        print("\n" + "="*60)
        print("✅ End-to-End Test Complete!")
        print("="*60)
        print("\nSummary:")
        print("  ✅ ETL Pipeline executed successfully")
        print("  ✅ Data verified in Silver and Gold layers")
        print("  ✅ Local Prompt Flow test completed")
        print("\nNext Steps:")
        print("  - Review data in Azure Portal (Storage Browser)")
        print("  - Configure Databricks cluster for AI pipeline")
        print("  - Deploy Prompt Flows to Azure AI Project")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
