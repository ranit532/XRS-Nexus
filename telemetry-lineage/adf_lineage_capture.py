#!/usr/bin/env python3
"""
ADF Lineage Capture
Captures data lineage metadata from Azure Data Factory pipeline executions
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.storage.filedatalake import DataLakeServiceClient
from dotenv import load_dotenv

load_dotenv()

class ADFLineageCapture:
    """Captures and stores ADF pipeline lineage metadata"""
    
    def __init__(self, subscription_id: str, resource_group: str, factory_name: str):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.factory_name = factory_name
        
        self.credential = DefaultAzureCredential()
        self.adf_client = DataFactoryManagementClient(
            credential=self.credential,
            subscription_id=subscription_id
        )
        
        # Storage for lineage data
        storage_account = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self.storage_client = DataLakeServiceClient(
            account_url=f"https://{storage_account}.dfs.core.windows.net",
            credential=self.credential
        )
    
    def get_pipeline_run(self, run_id: str) -> Dict[str, Any]:
        """Retrieve pipeline run details from ADF"""
        try:
            pipeline_run = self.adf_client.pipeline_runs.get(
                resource_group_name=self.resource_group,
                factory_name=self.factory_name,
                run_id=run_id
            )
            
            return {
                "run_id": pipeline_run.run_id,
                "pipeline_name": pipeline_run.pipeline_name,
                "status": pipeline_run.status,
                "run_start": pipeline_run.run_start.isoformat() if pipeline_run.run_start else None,
                "run_end": pipeline_run.run_end.isoformat() if pipeline_run.run_end else None,
                "duration_seconds": pipeline_run.duration_in_ms / 1000 if pipeline_run.duration_in_ms else 0,
                "parameters": pipeline_run.parameters or {}
            }
        except Exception as e:
            print(f"Error retrieving pipeline run: {e}")
            return {}
    
    def get_activity_runs(self, run_id: str) -> List[Dict[str, Any]]:
        """Retrieve activity-level details for a pipeline run"""
        try:
            from datetime import timedelta
            
            # Get pipeline run first to get time range
            pipeline_run = self.adf_client.pipeline_runs.get(
                resource_group_name=self.resource_group,
                factory_name=self.factory_name,
                run_id=run_id
            )
            
            # Query activity runs
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
                activity_data = {
                    "activity_name": activity.activity_name,
                    "activity_type": activity.activity_type,
                    "status": activity.status,
                    "activity_run_start": activity.activity_run_start.isoformat() if activity.activity_run_start else None,
                    "activity_run_end": activity.activity_run_end.isoformat() if activity.activity_run_end else None,
                    "duration_seconds": activity.duration_in_ms / 1000 if activity.duration_in_ms else 0,
                    "input": activity.input,
                    "output": activity.output
                }
                
                # Extract lineage information from input/output
                if activity.activity_type == "Copy":
                    activity_data["lineage"] = self._extract_copy_lineage(activity.input, activity.output)
                elif activity.activity_type == "ExecuteDataFlow":
                    activity_data["lineage"] = self._extract_dataflow_lineage(activity.input, activity.output)
                
                activities.append(activity_data)
            
            return activities
            
        except Exception as e:
            print(f"Error retrieving activity runs: {e}")
            return []
    
    def _extract_copy_lineage(self, input_data: Dict, output_data: Dict) -> Dict:
        """Extract lineage from Copy activity"""
        lineage = {
            "type": "copy",
            "sources": [],
            "sinks": [],
            "transformations": []
        }
        
        # Extract source information
        if input_data and "source" in input_data:
            source = input_data["source"]
            lineage["sources"].append({
                "type": source.get("type"),
                "dataset": input_data.get("datasetName")
            })
        
        # Extract sink information
        if output_data and "dataWritten" in output_data:
            lineage["sinks"].append({
                "rows_written": output_data.get("rowsCopied", 0),
                "dataset": input_data.get("datasetName")
            })
        
        return lineage
    
    def _extract_dataflow_lineage(self, input_data: Dict, output_data: Dict) -> Dict:
        """Extract lineage from Data Flow activity"""
        lineage = {
            "type": "dataflow",
            "sources": [],
            "sinks": [],
            "transformations": []
        }
        
        # Data flow lineage is more complex - would need to parse data flow definition
        if input_data and "dataFlow" in input_data:
            lineage["dataflow_name"] = input_data["dataFlow"].get("referenceName")
        
        return lineage
    
    def capture_lineage(self, run_id: str) -> Dict[str, Any]:
        """Capture complete lineage for a pipeline run"""
        print(f"\n📊 Capturing lineage for pipeline run: {run_id}")
        
        # Get pipeline run details
        pipeline_run = self.get_pipeline_run(run_id)
        if not pipeline_run:
            return {"error": "Pipeline run not found"}
        
        # Get activity runs
        activities = self.get_activity_runs(run_id)
        
        # Build lineage graph
        lineage_data = {
            "metadata": {
                "captured_at": datetime.now().isoformat(),
                "run_id": run_id,
                "pipeline_name": pipeline_run.get("pipeline_name"),
                "status": pipeline_run.get("status")
            },
            "pipeline_run": pipeline_run,
            "activities": activities,
            "lineage_graph": self._build_lineage_graph(activities)
        }
        
        return lineage_data
    
    def _build_lineage_graph(self, activities: List[Dict]) -> Dict:
        """Build a graph representation of data lineage"""
        graph = {
            "nodes": [],
            "edges": []
        }
        
        for activity in activities:
            # Add activity as node
            graph["nodes"].append({
                "id": activity["activity_name"],
                "type": activity["activity_type"],
                "status": activity["status"]
            })
            
            # Add edges based on lineage
            if "lineage" in activity:
                lineage = activity["lineage"]
                
                # Add source nodes and edges
                for source in lineage.get("sources", []):
                    source_id = source.get("dataset", "unknown_source")
                    if source_id not in [n["id"] for n in graph["nodes"]]:
                        graph["nodes"].append({
                            "id": source_id,
                            "type": "dataset",
                            "layer": "source"
                        })
                    graph["edges"].append({
                        "from": source_id,
                        "to": activity["activity_name"],
                        "type": "reads"
                    })
                
                # Add sink nodes and edges
                for sink in lineage.get("sinks", []):
                    sink_id = sink.get("dataset", "unknown_sink")
                    if sink_id not in [n["id"] for n in graph["nodes"]]:
                        graph["nodes"].append({
                            "id": sink_id,
                            "type": "dataset",
                            "layer": "sink"
                        })
                    graph["edges"].append({
                        "from": activity["activity_name"],
                        "to": sink_id,
                        "type": "writes"
                    })
        
        return graph
    
    def store_lineage(self, lineage_data: Dict):
        """Store lineage data to ADLS Gen2"""
        try:
            run_id = lineage_data["metadata"]["run_id"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lineage_{run_id}_{timestamp}.json"
            
            file_system_client = self.storage_client.get_file_system_client("lineage")
            directory_client = file_system_client.get_directory_client("adf_runs")
            file_client = directory_client.get_file_client(filename)
            
            lineage_json = json.dumps(lineage_data, indent=2)
            file_client.upload_data(lineage_json, overwrite=True)
            
            print(f"✅ Lineage data stored: lineage/adf_runs/{filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error storing lineage: {e}")
            return None

def main():
    """Main entry point for lineage capture"""
    if len(sys.argv) < 2:
        print("Usage: python adf_lineage_capture.py <run_id>")
        print("\nOr set environment variables:")
        print("  SUBSCRIPTION_ID")
        print("  RESOURCE_GROUP")
        print("  FACTORY_NAME")
        print("  RUN_ID")
        sys.exit(1)
    
    run_id = sys.argv[1] if len(sys.argv) > 1 else os.getenv("RUN_ID")
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = os.getenv("RESOURCE_GROUP", "xrs-nexus-dev-rg")
    factory_name = os.getenv("FACTORY_NAME")
    
    if not all([subscription_id, resource_group, factory_name, run_id]):
        print("❌ Missing required configuration")
        sys.exit(1)
    
    # Capture lineage
    capturer = ADFLineageCapture(subscription_id, resource_group, factory_name)
    lineage_data = capturer.capture_lineage(run_id)
    
    # Store lineage locally first
    if lineage_data and "error" not in lineage_data:
        # Save locally
        local_dir = Path("lineage/adf_runs")
        local_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        local_filename = local_dir / f"lineage_{run_id}_{timestamp}.json"
        
        with open(local_filename, 'w') as f:
            json.dump(lineage_data, f, indent=2)
        
        print(f"✅ Lineage data stored locally: {local_filename}")
        
        # Also try to store in cloud
        try:
            capturer.store_lineage(lineage_data)
        except Exception as e:
            print(f"⚠️  Could not store in cloud (local copy saved): {e}")
        
        print("\n✅ Lineage capture complete")
    else:
        print("\n❌ Lineage capture failed")


if __name__ == "__main__":
    main()
