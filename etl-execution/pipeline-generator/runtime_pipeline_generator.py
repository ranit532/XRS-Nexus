"""
Runtime Pipeline Generator
- Converts logical flow JSON into Azure Data Factory (ADF) or Microsoft Fabric pipeline definitions
- Supports batch and CDC
- Supports retries, parallelism, and checkpoints
"""
import json
from typing import Dict, Any

class RuntimePipelineGenerator:
    def logical_to_adf(self, logical_flow: Dict[str, Any], mode: str = "batch") -> Dict[str, Any]:
        """Generate ADF pipeline JSON from logical flow."""
        activities = []
        # Extraction
        extract_activity = {
            "name": "Extract",
            "type": "Copy",
            "dependsOn": [],
            "policy": {"retry": 3, "timeout": "01:00:00"},
            "userProperties": [{"key": "step", "value": "extract"}],
            "inputs": ["SourceDataset"],
            "outputs": ["StagingDataset"]
        }
        activities.append(extract_activity)
        # Transformation (dummy mapping)
        transform_activity = {
            "name": "Transform",
            "type": "DataFlow",
            "dependsOn": [ {"activity": "Extract", "dependencyConditions": ["Succeeded"]} ],
            "policy": {"retry": 2},
            "userProperties": [{"key": "step", "value": "transform"}],
            "inputs": ["StagingDataset"],
            "outputs": ["TransformedDataset"]
        }
        activities.append(transform_activity)
        # Load
        load_activity = {
            "name": "Load",
            "type": "Copy",
            "dependsOn": [ {"activity": "Transform", "dependencyConditions": ["Succeeded"]} ],
            "policy": {"retry": 2},
            "userProperties": [{"key": "step", "value": "load"}],
            "inputs": ["TransformedDataset"],
            "outputs": ["LakehouseDataset"]
        }
        activities.append(load_activity)
        # CDC support
        if mode == "cdc":
            extract_activity["typeProperties"] = {"source": {"type": "CDCSource"}}
            load_activity["typeProperties"] = {"sink": {"type": "IncrementalSink"}}
        # Parallelism and checkpoints (dummy example)
        pipeline = {
            "name": "GeneratedPipeline",
            "properties": {
                "activities": activities,
                "annotations": ["generated", mode],
                "concurrency": 4,
                "runConcurrently": True,
                "checkpoint": True
            }
        }
        return pipeline

    def logical_to_fabric(self, logical_flow: Dict[str, Any], mode: str = "batch") -> Dict[str, Any]:
        """Generate Microsoft Fabric pipeline (or Spark job) from logical flow."""
        steps = []
        # Extraction
        steps.append({
            "step": "extract",
            "source": logical_flow['nodes'][0]['label'],
            "mode": mode
        })
        # Transformation
        steps.append({
            "step": "transform",
            "description": "Apply canonical mapping"
        })
        # Load
        steps.append({
            "step": "load",
            "target": logical_flow['nodes'][-1]['label'],
            "mode": mode
        })
        # Parallelism and checkpoints
        pipeline = {
            "pipelineName": "GeneratedFabricPipeline",
            "steps": steps,
            "parallelism": 4,
            "checkpoint": True,
            "annotations": ["generated", mode]
        }
        return pipeline

    def generate(self, logical_flow: Dict[str, Any], target: str = "adf", mode: str = "batch") -> Dict[str, Any]:
        if target == "adf":
            return self.logical_to_adf(logical_flow, mode)
        elif target == "fabric":
            return self.logical_to_fabric(logical_flow, mode)
        else:
            raise ValueError("Unknown target platform")

# Example usage
if __name__ == "__main__":
    with open("../../ai-orchestration/src/agents/example_sap_logical_flow.json") as f:
        sap_logical_flow = json.load(f)
    gen = RuntimePipelineGenerator()
    adf_pipeline = gen.generate(sap_logical_flow, target="adf", mode="cdc")
    fabric_pipeline = gen.generate(sap_logical_flow, target="fabric", mode="cdc")
    print("ADF Pipeline Example:\n", json.dumps(adf_pipeline, indent=2))
    print("Fabric Pipeline Example:\n", json.dumps(fabric_pipeline, indent=2))
