#!/usr/bin/env python3
"""
ADF Pipeline Testing Script
Tests end-to-end ADF pipeline execution and validates results
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime
from typing import Dict, Any
from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import CreateRunResponse
from dotenv import load_dotenv

load_dotenv()

class ADFPipelineTester:
    """Tests ADF pipeline execution"""
    
    def __init__(self, subscription_id: str, resource_group: str, factory_name: str):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.factory_name = factory_name
        
        self.credential = DefaultAzureCredential()
        self.adf_client = DataFactoryManagementClient(
            credential=self.credential,
            subscription_id=subscription_id
        )
    
    def trigger_pipeline(self, pipeline_name: str, parameters: Dict = None) -> str:
        """Trigger a pipeline run and return run ID"""
        print(f"\n🚀 Triggering pipeline: {pipeline_name}")
        
        try:
            response: CreateRunResponse = self.adf_client.pipelines.create_run(
                resource_group_name=self.resource_group,
                factory_name=self.factory_name,
                pipeline_name=pipeline_name,
                parameters=parameters or {}
            )
            
            run_id = response.run_id
            print(f"✓ Pipeline triggered successfully")
            print(f"  Run ID: {run_id}")
            return run_id
            
        except Exception as e:
            print(f"❌ Failed to trigger pipeline: {e}")
            return None
    
    def monitor_pipeline(self, run_id: str, timeout_seconds: int = 300) -> Dict[str, Any]:
        """Monitor pipeline execution until completion or timeout"""
        print(f"\n⏳ Monitoring pipeline execution...")
        print(f"  Run ID: {run_id}")
        print(f"  Timeout: {timeout_seconds}s")
        
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < timeout_seconds:
            try:
                pipeline_run = self.adf_client.pipeline_runs.get(
                    resource_group_name=self.resource_group,
                    factory_name=self.factory_name,
                    run_id=run_id
                )
                
                status = pipeline_run.status
                
                if status != last_status:
                    elapsed = time.time() - start_time
                    print(f"  [{elapsed:.1f}s] Status: {status}")
                    last_status = status
                
                if status in ["Succeeded", "Failed", "Cancelled"]:
                    print(f"\n{'✅' if status == 'Succeeded' else '❌'} Pipeline {status.lower()}")
                    
                    return {
                        "run_id": run_id,
                        "status": status,
                        "pipeline_name": pipeline_run.pipeline_name,
                        "run_start": pipeline_run.run_start.isoformat() if pipeline_run.run_start else None,
                        "run_end": pipeline_run.run_end.isoformat() if pipeline_run.run_end else None,
                        "duration_seconds": pipeline_run.duration_in_ms / 1000 if pipeline_run.duration_in_ms else 0,
                        "message": pipeline_run.message
                    }
                
                time.sleep(5)  # Poll every 5 seconds
                
            except Exception as e:
                print(f"  ⚠️  Error checking status: {e}")
                time.sleep(5)
        
        print(f"\n⏱️  Timeout reached after {timeout_seconds}s")
        return {"run_id": run_id, "status": "Timeout", "message": "Monitoring timeout"}
    
    def get_activity_runs(self, run_id: str) -> list:
        """Get activity-level details for a pipeline run"""
        try:
            from datetime import timedelta
            
            pipeline_run = self.adf_client.pipeline_runs.get(
                resource_group_name=self.resource_group,
                factory_name=self.factory_name,
                run_id=run_id
            )
            
            filter_params = {
                "last_updated_after": pipeline_run.run_start - timedelta(minutes=5),
                "last_updated_before": (pipeline_run.run_end or datetime.now()) + timedelta(minutes=5)
            }
            
            activity_runs = self.adf_client.activity_runs.query_by_pipeline_run(
                resource_group_name=self.resource_group,
                factory_name=self.factory_name,
                run_id=run_id,
                filter_parameters=filter_params
            )
            
            activities = []
            for activity in activity_runs.value:
                activities.append({
                    "name": activity.activity_name,
                    "type": activity.activity_type,
                    "status": activity.status,
                    "duration_seconds": activity.duration_in_ms / 1000 if activity.duration_in_ms else 0
                })
            
            return activities
            
        except Exception as e:
            print(f"⚠️  Could not retrieve activity runs: {e}")
            return []
    
    def print_summary(self, result: Dict, activities: list = None):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 Pipeline Execution Summary")
        print("="*60)
        print(f"Pipeline: {result.get('pipeline_name', 'N/A')}")
        print(f"Run ID: {result.get('run_id', 'N/A')}")
        print(f"Status: {result.get('status', 'N/A')}")
        print(f"Duration: {result.get('duration_seconds', 0):.2f}s")
        
        if result.get('run_start'):
            print(f"Started: {result['run_start']}")
        if result.get('run_end'):
            print(f"Ended: {result['run_end']}")
        
        if activities:
            print(f"\nActivities ({len(activities)}):")
            for activity in activities:
                status_icon = "✓" if activity["status"] == "Succeeded" else "✗"
                print(f"  {status_icon} {activity['name']} ({activity['type']}) - {activity['duration_seconds']:.2f}s")
        
        if result.get('message'):
            print(f"\nMessage: {result['message']}")
        
        print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Test ADF pipeline execution")
    parser.add_argument("--pipeline", required=True, help="Pipeline name to test")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds (default: 300)")
    parser.add_argument("--parameters", type=str, help="Pipeline parameters as JSON string")
    
    args = parser.parse_args()
    
    # Get configuration from environment
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = os.getenv("RESOURCE_GROUP", "xrs-nexus-dev-rg")
    factory_name = os.getenv("FACTORY_NAME")
    
    if not factory_name:
        # Try to find ADF factory
        print("⚠️  FACTORY_NAME not set, attempting to discover...")
        import subprocess
        result = subprocess.run(
            ["az", "datafactory", "list", "-g", resource_group, "--query", "[0].name", "-o", "tsv"],
            capture_output=True, text=True
        )
        factory_name = result.stdout.strip()
    
    if not all([subscription_id, resource_group, factory_name]):
        print("❌ Missing required configuration:")
        print("  AZURE_SUBSCRIPTION_ID")
        print("  RESOURCE_GROUP (or set default)")
        print("  FACTORY_NAME")
        sys.exit(1)
    
    # Parse parameters if provided
    parameters = None
    if args.parameters:
        try:
            parameters = json.loads(args.parameters)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in parameters: {args.parameters}")
            sys.exit(1)
    
    # Run test
    tester = ADFPipelineTester(subscription_id, resource_group, factory_name)
    
    # Trigger pipeline
    run_id = tester.trigger_pipeline(args.pipeline, parameters)
    if not run_id:
        sys.exit(1)
    
    # Monitor execution
    result = tester.monitor_pipeline(run_id, args.timeout)
    
    # Get activity details
    activities = tester.get_activity_runs(run_id)
    
    # Print summary
    tester.print_summary(result, activities)
    
    # Exit with appropriate code
    sys.exit(0 if result.get("status") == "Succeeded" else 1)

if __name__ == "__main__":
    main()
