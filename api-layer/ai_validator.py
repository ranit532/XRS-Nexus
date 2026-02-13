"""
AI Validator using existing Prompt Flow
Calls the PII Detection flow deployed in Azure AI Project
"""
import json
import os
import logging
from azure.identity import DefaultAzureCredential
from promptflow.azure import PFClient

class PromptFlowValidator:
    """Validates data using deployed Prompt Flows"""
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = "xrs-nexus-dev-rg"
        self.workspace_name = "xrs-nexus-dev-ai-project"
        
        # Initialize Prompt Flow client
        self.pf_client = PFClient(
            credential=self.credential,
            subscription_id=self.subscription_id,
            resource_group_name=self.resource_group,
            workspace_name=self.workspace_name
        )
    
    def validate_pii(self, dataset_sample: list) -> dict:
        """
        Use PII Detection Prompt Flow for intelligent PII detection
        
        Args:
            dataset_sample: List of dictionaries representing sample data
            
        Returns:
            PII validation results
        """
        try:
            # Prepare payload for PII detection flow
            payload_sample = json.dumps(dataset_sample[0] if dataset_sample else {})
            
            # Invoke the PII detection flow
            print(f"Attempting to invoke Prompt Flow 'pii_detection'...")
            # Note: This assumes the flow is deployed in Azure AI Project.
            # If running locally, it requires 'pf' CLI and local flow files.
            result = self.pf_client.flows.invoke(
                flow="pii_detection",  # deployment_name or flow directory
                inputs={"payload_sample": payload_sample}
            )
            
            print(f"Prompt Flow invocation successful. Result: {result}")

            # Parse result
            if isinstance(result, str):
                pii_report = json.loads(result)
            else:
                pii_report = result
            
            return {
                "has_pii": pii_report.get("has_pii", False),
                "pii_fields": pii_report.get("pii_fields", []),
                "classification": pii_report.get("classification", "Public"),
                "status": "warning" if pii_report.get("has_pii") else "passed",
                "recommendations": ["Apply data masking", "Encrypt sensitive fields"] if pii_report.get("has_pii") else [],
                "ai_powered": True  # Explicitly flag as AI powered
            }
            
        except Exception as e:
            logging.error(f"PII validation via Prompt Flow failed: {e}")
            print(f"⚠️ AI Validation failed. Error: {e}")
            print("Falling back to enhanced pattern matching...")
            # Fallback to simple keyword matching
            return self._fallback_pii_detection(dataset_sample)
    
    def _fallback_pii_detection(self, dataset_sample: list) -> dict:
        """Fallback PII detection using keywords"""
        pii_keywords = ['email', 'phone', 'ssn', 'credit_card', 'address', 'name']
        pii_fields = []
        
        if dataset_sample:
            for field in dataset_sample[0].keys():
                if any(keyword in field.lower() for keyword in pii_keywords):
                    pii_fields.append(field)
        
        return {
            "has_pii": len(pii_fields) > 0,
            "pii_fields": pii_fields,
            "classification": "Confidential" if pii_fields else "Public",
            "status": "warning" if pii_fields else "passed",
            "recommendations": ["Apply data masking"] if pii_fields else []
        }
    
    def validate_data_quality(self, dataset_sample: list, field_names: list) -> dict:
        """
        Comprehensive data quality validation
        
        Args:
            dataset_sample: Sample data rows
            field_names: List of field names
            
        Returns:
            Validation results
        """
        results = {
            "pii_validation": self.validate_pii(dataset_sample),
            "quality_checks": self._basic_quality_checks(dataset_sample),
            "timestamp": json.dumps({"timestamp": "now"})  # Placeholder
        }
        
        # Determine overall status
        if results["pii_validation"]["status"] == "warning":
            results["status"] = "warning"
        elif any(c.get("status") == "failed" for c in results["quality_checks"]):
            results["status"] = "failed"
        else:
            results["status"] = "passed"
        
        return results
    
    def _basic_quality_checks(self, dataset_sample: list) -> list:
        """Basic quality checks (nulls, duplicates)"""
        checks = []
        
        if not dataset_sample:
            return checks
        
        # Null check
        null_counts = {}
        for row in dataset_sample:
            for key, value in row.items():
                if value is None or value == '' or str(value).lower() == 'null':
                    null_counts[key] = null_counts.get(key, 0) + 1
        
        null_percentage = max(null_counts.values()) / len(dataset_sample) * 100 if null_counts else 0
        
        checks.append({
            "check_name": "null_value_check",
            "status": "failed" if null_percentage > 5 else "passed",
            "details": {"null_percentage": null_percentage},
            "recommendation": "Review data quality" if null_percentage > 5 else "No action needed"
        })
        
        # Duplicate check
        key_field = list(dataset_sample[0].keys())[0]
        keys = [row.get(key_field) for row in dataset_sample]
        duplicate_count = len(keys) - len(set(keys))
        
        checks.append({
            "check_name": "duplicate_check",
            "status": "passed" if duplicate_count == 0 else "warning",
            "details": {"duplicate_count": duplicate_count},
            "recommendation": "No duplicates" if duplicate_count == 0 else "Implement deduplication"
        })
        
        return checks
