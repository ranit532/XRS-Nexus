import json
import logging
from typing import Dict, Any, List
# In a real Prompt Flow, you would import @tool
# from promptflow import tool

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MetadataIntelligenceAgent:
    """
    Agent responsible for ingesting raw metadata and normalizing it into a canonical format.
    Simulates AI-driven classification and enrichment.
    """
    def __init__(self):
        self.logger = logger

    def analyze_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes raw metadata to correct data types, detect PII, and normalize schema.
        
        Args:
            raw_metadata: Dictionary containing raw metadata from source.
            
        Returns:
            Normalized and enriched metadata dictionary.
        """
        object_name = raw_metadata.get('object_name', 'Unknown')
        self.logger.info(f"Analyzing metadata for object: {object_name}")
        
        normalized_metadata = raw_metadata.copy()
        
        # 1. Normalize System Type & Source Category
        system_id = raw_metadata.get("system_id", "").upper()
        if "SAP" in system_id:
            normalized_metadata["system_type"] = "SAP"
            normalized_metadata["connection_type"] = "SAP_NATIVE"
        elif "SALESFORCE" in system_id:
            normalized_metadata["system_type"] = "Salesforce"
            normalized_metadata["connection_type"] = "SALESFORCE_ADAPTER"
        else:
            normalized_metadata["system_type"] = "REST_API"
            normalized_metadata["connection_type"] = "HTTP_GENERIC"

        # 2. Detect Load Strategy & CDC
        # Rule-based fallback if not explicitly set
        if "cdc_enabled" not in normalized_metadata:
             # Simulation: Tables with createdAt/updatedAt usually support incremental
             normalized_metadata["cdc_enabled"] = False
             normalized_metadata["load_strategy"] = "FULL_LOAD"
        
        # 3. Assign Business Criticality based on SLA
        sla = raw_metadata.get("sla_minutes", 1440) # Default 24h
        if sla <= 60:
            normalized_metadata["criticality"] = "HIGH"
            normalized_metadata["priority_tier"] = "Tier-1"
        elif sla <= 240:
            normalized_metadata["criticality"] = "MEDIUM"
            normalized_metadata["priority_tier"] = "Tier-2"
        else:
            normalized_metadata["criticality"] = "LOW"
            normalized_metadata["priority_tier"] = "Tier-3"

        # 4. Enrich Description (Simulated GenAI)
        if not normalized_metadata.get("description"):
            normalized_metadata["description"] = f"[AI-Generated] Standard integration object for {object_name} from {system_id}."
            
        # 5. Data Governance & PII Detection (Simulated)
        # In production, this would call Azure PII detection
        sensitive_terms = ["email", "salary", "ssn", "dob", "credit_card", "phone"]
        pii_fields = []
        
        # Check explicit data quality rules first
        rules = normalized_metadata.get("data_quality_rules", [])
        for rule in rules:
             field_name = rule.get("field", "").lower()
             if any(term in field_name for term in sensitive_terms):
                 pii_fields.append(field_name)
        
        normalized_metadata["has_pii"] = len(pii_fields) > 0
        normalized_metadata["pii_fields"] = pii_fields

        # Add unique integration ID
        normalized_metadata["integration_id"] = f"{normalized_metadata['system_type']}_{object_name}_{normalized_metadata['domain']}".upper()
        
        self.logger.info(f"Metadata analysis complete for {object_name}. Criticality: {normalized_metadata['criticality']}")
        return normalized_metadata

    def run_batch(self, metadata_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.analyze_metadata(m) for m in metadata_list]

# @tool
def analyze_metadata_tool(raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function for Prompt Flow"""
    agent = MetadataIntelligenceAgent()
    return agent.analyze_metadata(raw_metadata)

if __name__ == "__main__":
    # Test stub
    sample = {
        "system_id": "SAP_ECC", 
        "object_name": "KNA1", 
        "sla_minutes": 30,
        "data_quality_rules": [{"field": "email_address", "rule": "email"}]
    }
    print(json.dumps(analyze_metadata_tool(sample), indent=2))
