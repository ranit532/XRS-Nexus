import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PipelineBuilder:
    """
    Converts logical integration flows into physical execution definitions
    (Fabric Pipelines JSON or Spark Job Configurations).
    """
    def __init__(self):
        pass

    def build_pipeline(self, logical_flow: Dict[str, Any], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds the physical pipeline definition.
        
        Args:
            logical_flow: The technology-agnostic flow definition.
            strategy: The chosen execution strategy (e.g., Fabric_Spark).
            
        Returns:
            JSON definition of the pipeline/job.
        """
        engine = strategy.get("engine")
        flow_id = logical_flow.get("flow_id")
        logger.info(f"Building pipeline for {flow_id} on {engine}")
        
        if engine == "Fabric_Spark":
            return self._build_spark_job(logical_flow, strategy)
        elif engine == "Fabric_Pipeline" or engine == "Azure_Data_Factory":
            return self._build_adf_pipeline(logical_flow, strategy)
        else:
            raise ValueError(f"Unsupported engine: {engine}")

    def _build_spark_job(self, flow: Dict[str, Any], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a Spark Job definition."""
        steps = flow.get("steps", [])
        
        # Construct Spark arguments
        spark_conf = {
            "spark.app.name": f"XRS_{flow['flow_id']}",
            "spark.executor.cores": str(strategy.get("parallelism", 2)),
            "spark.executor.memory": "4g" if strategy.get("compute_size") == "Small" else "8g"
        }
        
        job_payload = {
            "job_type": "SparkBatch",
            "file": "abfss://.../main.py", # Placeholder
            "args": [
                "--flow_definition", json.dumps(flow), # Pass full flow logic to Spark
                "--target_layer", "Silver" # Default
            ],
            "conf": spark_conf,
            "tags": {
                "generated_by": "XPS_NEXUS_AI",
                "flow_id": flow["flow_id"]
            }
        }
        return job_payload

    def _build_adf_pipeline(self, flow: Dict[str, Any], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Generates an ADF/Fabric Pipeline JSON definition."""
        activities = []
        
        for step in flow.get("steps", []):
            if step["step_type"] == "EXTRACT":
                activities.append({
                    "name": step["step_name"],
                    "type": "Copy",
                    "inputs": [{"referenceName": step["config"]["source_object"], "type": "DatasetReference"}],
                    "outputs": [{"referenceName": "BronzeLakehouse", "type": "DatasetReference"}]
                })
            elif step["step_type"] == "TRANSFORM":
                 activities.append({
                    "name": step["step_name"],
                    "type": "SynapseNotebook", # Using Notebook for transform even in Pipeline
                    "notebook": {"referenceName": "BronzeToSilver"},
                    "parameters": {"tables": json.dumps(step["config"])}
                })

        pipeline_def = {
            "name": flow["flow_id"],
            "properties": {
                "activities": activities,
                "annotations": ["AI_Generated", "XPS_NEXUS"]
            }
        }
        return pipeline_def

if __name__ == "__main__":
    # Test
    flow = {
        "flow_id": "TEST_FLOW",
        "steps": [
            {"step_type": "EXTRACT", "step_name": "CopyData", "config": {"source_object": "KNA1"}},
            {"step_type": "TRANSFORM", "step_name": "Cleanse", "config": {}}
        ]
    }
    strategy = {"engine": "Fabric_Pipeline"}
    builder = PipelineBuilder()
    print(json.dumps(builder.build_pipeline(flow, strategy), indent=2))
