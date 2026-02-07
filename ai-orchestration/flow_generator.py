import json
import logging
from typing import Dict, Any, List

# Configure logging
logger = logging.getLogger(__name__)

class LogicalFlowGeneratorAgent:
    """
    Agent responsible for generating technology-agnostic logical integration flows.
    Determines the sequence of operations (Extract, Transform, Load, Quality Check)
    based on metadata attributes like CDC, SLA, and System Type.
    """
    def __init__(self):
        pass

    def generate_flow(self, normalized_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a logical flow definition.
        
        Args:
            normalized_metadata: Metadata dict processed by MetadataIntelligenceAgent.
            
        Returns:
            Dictionary representing the logical flow steps.
        """
        integration_id = normalized_metadata.get("integration_id")
        system_type = normalized_metadata.get("system_type")
        load_strategy = normalized_metadata.get("load_strategy", "FULL")
        object_name = normalized_metadata.get("object_name")
        
        logger.info(f"Generating logical flow for {integration_id} ({load_strategy})")
        
        flow_steps = []
        
        # Step 1: Ingest/Extract
        ingest_step = {
            "step_id": "10",
            "step_name": f"Extract_{object_name}",
            "step_type": "EXTRACT",
            "config": {
                "source_system": normalized_metadata.get("system_id"),
                "source_object": object_name,
                "connection": normalized_metadata.get("connection_type")
            }
        }
        
        if load_strategy == "INCREMENTAL" or normalized_metadata.get("cdc_enabled"):
            ingest_step["config"]["mode"] = "CDC_STREAM" if normalized_metadata.get("system_type") == "SAP" else "WATERMARK"
        else:
            ingest_step["config"]["mode"] = "FULL_SNAPSHOT"
            
        flow_steps.append(ingest_step)
        
        # Step 2: Data Quality & Validation
        rules = normalized_metadata.get("data_quality_rules", [])
        if rules:
            dq_step = {
                "step_id": "20",
                "step_name": "Data_Quality_Check",
                "step_type": "VALIDATION",
                "config": {
                    "rules": rules,
                    "action_on_failure": "QUARANTINE" if normalized_metadata.get("criticality") == "HIGH" else "LOG_WARNING"
                }
            }
            flow_steps.append(dq_step)
            
        # Step 3: Transformation (Bronze to Silver)
        transform_step = {
            "step_id": "30",
            "step_name": "Standardize_to_Silver",
            "step_type": "TRANSFORM",
            "config": {
                "transformations": [
                    "snake_case_columns",
                    "cast_types",
                    "add_metadata_columns"
                ],
                "target_layer": "Silver"
            }
        }
        flow_steps.append(transform_step)
        
        # Step 4: Load (Silver to Gold/dw) - Optional based on domain, but we'll assume standard flow
        load_step = {
            "step_id": "40",
            "step_name": f"Load_{object_name}_Gold",
            "step_type": "LOAD",
            "config": {
                "target_layer": "Gold",
                "partition_by": "date_key" if "date" in str(rules) else None,
                "write_mode": "MERGE" if load_strategy == "INCREMENTAL" else "OVERWRITE"
            }
        }
        flow_steps.append(load_step)
        
        logical_flow = {
            "flow_id": f"FLOW_{integration_id}",
            "metadata_ref": normalized_metadata.get("integration_id"),
            "generated_at": normalized_metadata.get("analyzed_at"),
            "steps": flow_steps,
            "sla_config": {
                "expected_duration_minutes": 30, # Predicted
                "max_retries": 3,
                "alert_email": normalized_metadata.get("owner")
            }
        }
        
        return logical_flow

# @tool
def generate_flow_tool(normalized_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper for Prompt Flow"""
    agent = LogicalFlowGeneratorAgent()
    return agent.generate_flow(normalized_metadata)

if __name__ == "__main__":
    # Test stub
    sample = {
        "integration_id": "SAP_KNA1_CUSTOMER",
        "system_type": "SAP",
        "system_id": "SAP_ECC",
        "object_name": "KNA1",
        "load_strategy": "INCREMENTAL",
        "cdc_enabled": True,
        "criticality": "HIGH",
        "owner": "test@xpsgroup.com"
    }
    print(json.dumps(generate_flow_tool(sample), indent=2))
