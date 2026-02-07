import logging
import json
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ETLStrategyAgent:
    """
    Agent responsible for determining the optimal execution engine and strategy 
    for a given logical flow.
    Decides between Fabric Spark, Fabric Pipelines, or Azure Data Factory.
    """
    def __init__(self):
        pass

    def determine_strategy(self, logical_flow: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determines the physical execution strategy.
        
        Args:
            logical_flow: The logical flow definition from LogicalFlowGeneratorAgent.
            metadata: Normalized metadata.
            
        Returns:
            Strategy configuration including engine, cluster size, and parallelism.
        """
        flow_id = logical_flow.get("flow_id")
        steps = logical_flow.get("steps", [])
        
        # Heuristic Analysis
        has_complex_transform = any(s.get("step_type") == "TRANSFORM" for s in steps)
        has_cdc = any("CDC" in str(s.get("config", {})) for s in steps)
        criticality = metadata.get("criticality", "LOW")
        
        # Default strategy
        strategy = {
            "flow_ref": flow_id,
            "engine": "Fabric_Pipeline",
            "compute_size": "Small",
            "parallelism": 1
        }
        
        # Decision Logic
        if has_complex_transform or has_cdc:
            strategy["engine"] = "Fabric_Spark"
            strategy["reason"] = "Deep transformation or CDC merge required."
            
            if criticality == "HIGH":
                strategy["compute_size"] = "Medium_High_Concurrency"
                strategy["parallelism"] = 4
            else:
                 strategy["compute_size"] = "Small_Job_Cluster"
        
        elif metadata.get("system_type") == "SAP":
            # SAP usually requires specific connectors best handled by ADF or Fabric Pipeline Copy
            strategy["engine"] = "Fabric_Pipeline" # Uses Copy Activity
            strategy["reason"] = "Native SAP Connector required for efficient extraction."
            
        elif metadata.get("system_type") == "REST_API":
            strategy["engine"] = "Azure_Functions" # Or Fabric Notebook
            strategy["reason"] = "Lightweight API polling suitable for Serverless Function."
            
        # Add resilience config
        strategy["resilience"] = {
            "retry_count": 3 if criticality == "HIGH" else 1,
            "retry_interval_seconds": 300,
            "dead_letter_queue": True
        }
        
        logger.info(f"Strategy determined for {flow_id}: {strategy['engine']}")
        return strategy

# @tool
def etl_strategy_tool(logical_flow: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    agent = ETLStrategyAgent()
    return agent.determine_strategy(logical_flow, metadata)
