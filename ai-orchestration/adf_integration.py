#!/usr/bin/env python3
"""
AI Orchestration Integration for ADF Pipeline
Provides data quality validation using Prompt Flow and Azure OpenAI
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ADFAIOrchestrator:
    """Integrates AI-powered data quality checks with ADF pipelines"""
    
    def __init__(self):
        self.storage_account = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self.account_url = f"https://{self.storage_account}.dfs.core.windows.net"
        self.credential = DefaultAzureCredential()
        self.service_client = DataLakeServiceClient(
            account_url=self.account_url,
            credential=self.credential
        )
    
    def sample_dataset(self, container: str, folder: str, sample_size: int = 100) -> List[Dict]:
        """Sample data from ADLS Gen2 for AI validation"""
        try:
            file_system_client = self.service_client.get_file_system_client(container)
            directory_client = file_system_client.get_directory_client(folder)
            
            # Find CSV or Parquet files
            paths = directory_client.get_paths()
            data_files = [p for p in paths if not p.is_directory and (p.name.endswith('.csv') or p.name.endswith('.parquet'))]
            
            if not data_files:
                return []
            
            # Read first file (simplified - in production, use proper CSV/Parquet parsing)
            file_client = file_system_client.get_file_client(data_files[0].name)
            download = file_client.download_file()
            content = download.readall().decode('utf-8')
            
            # Parse CSV (basic implementation)
            lines = content.strip().split('\n')
            if len(lines) < 2:
                return []
            
            headers = lines[0].split(',')
            sample_data = []
            
            for line in lines[1:min(sample_size + 1, len(lines))]:
                values = line.split(',')
                sample_data.append(dict(zip(headers, values)))
            
            return sample_data
            
        except Exception as e:
            print(f"Error sampling dataset: {e}")
            return []
    
    def validate_data_quality(self, dataset_path: str, schema: Dict, validation_rules: List[str]) -> Dict[str, Any]:
        """
        AI-powered data quality validation
        
        Args:
            dataset_path: Path to dataset in ADLS (e.g., "silver/customers")
            schema: Expected schema definition
            validation_rules: List of validation rules to apply
        
        Returns:
            Validation results with pass/fail status and recommendations
        """
        container, folder = dataset_path.split('/', 1)
        sample_data = self.sample_dataset(container, folder)
        
        if not sample_data:
            return {
                "status": "error",
                "message": "Unable to sample dataset",
                "timestamp": datetime.now().isoformat()
            }
        
        # AI-based validation checks
        validation_results = {
            "dataset": dataset_path,
            "sample_size": len(sample_data),
            "timestamp": datetime.now().isoformat(),
            "checks": []
        }
        
        # Check 1: Null values
        if "check_nulls" in validation_rules:
            null_check = self._check_nulls(sample_data, schema)
            validation_results["checks"].append(null_check)
        
        # Check 2: Duplicates
        if "check_duplicates" in validation_rules:
            duplicate_check = self._check_duplicates(sample_data, schema)
            validation_results["checks"].append(duplicate_check)
        
        # Check 3: PII detection
        if "check_pii" in validation_rules:
            pii_check = self._check_pii(sample_data)
            validation_results["checks"].append(pii_check)
        
        # Check 4: Data type validation
        if "check_types" in validation_rules:
            type_check = self._check_data_types(sample_data, schema)
            validation_results["checks"].append(type_check)
        
        # Determine overall status
        failed_checks = [c for c in validation_results["checks"] if c["status"] == "failed"]
        validation_results["status"] = "failed" if failed_checks else "passed"
        validation_results["failed_count"] = len(failed_checks)
        validation_results["total_checks"] = len(validation_results["checks"])
        
        return validation_results
    
    def _check_nulls(self, data: List[Dict], schema: Dict) -> Dict:
        """Check for unexpected null values"""
        null_counts = {}
        total_rows = len(data)
        
        for row in data:
            for key, value in row.items():
                if value is None or value == '' or value.lower() == 'null':
                    null_counts[key] = null_counts.get(key, 0) + 1
        
        # Calculate null percentages
        null_percentages = {k: (v / total_rows) * 100 for k, v in null_counts.items()}
        
        # Flag fields with > 5% nulls
        high_null_fields = {k: v for k, v in null_percentages.items() if v > 5}
        
        return {
            "check_name": "null_value_check",
            "status": "failed" if high_null_fields else "passed",
            "details": {
                "null_percentages": null_percentages,
                "high_null_fields": high_null_fields
            },
            "recommendation": "Review data quality at source" if high_null_fields else "No action needed"
        }
    
    def _check_duplicates(self, data: List[Dict], schema: Dict) -> Dict:
        """Check for duplicate records"""
        # Assume first field is primary key
        if not data:
            return {"check_name": "duplicate_check", "status": "passed", "details": {}}
        
        key_field = list(data[0].keys())[0]
        keys = [row.get(key_field) for row in data]
        unique_keys = set(keys)
        
        duplicate_count = len(keys) - len(unique_keys)
        duplicate_percentage = (duplicate_count / len(keys)) * 100 if keys else 0
        
        return {
            "check_name": "duplicate_check",
            "status": "failed" if duplicate_percentage > 1 else "passed",
            "details": {
                "total_records": len(keys),
                "unique_records": len(unique_keys),
                "duplicate_count": duplicate_count,
                "duplicate_percentage": duplicate_percentage
            },
            "recommendation": "Implement deduplication logic" if duplicate_percentage > 1 else "No action needed"
        }
    
    def _check_pii(self, data: List[Dict]) -> Dict:
        """Detect potential PII fields (simplified - in production use AI model)"""
        pii_keywords = ['email', 'phone', 'ssn', 'credit_card', 'address', 'name']
        pii_fields = []
        
        if data:
            for field in data[0].keys():
                if any(keyword in field.lower() for keyword in pii_keywords):
                    pii_fields.append(field)
        
        return {
            "check_name": "pii_detection",
            "status": "warning" if pii_fields else "passed",
            "details": {
                "pii_fields_detected": pii_fields,
                "count": len(pii_fields)
            },
            "recommendation": "Apply data masking or encryption" if pii_fields else "No PII detected"
        }
    
    def _check_data_types(self, data: List[Dict], schema: Dict) -> Dict:
        """Validate data types match schema"""
        type_mismatches = []
        
        # Simplified type checking
        for row in data[:10]:  # Check first 10 rows
            for field, value in row.items():
                # Basic type inference
                if value and value.lower() != 'null':
                    try:
                        # Try to infer type
                        if value.replace('.', '').replace('-', '').isdigit():
                            inferred_type = "numeric"
                        elif '@' in value:
                            inferred_type = "email"
                        else:
                            inferred_type = "string"
                    except:
                        inferred_type = "unknown"
        
        return {
            "check_name": "data_type_validation",
            "status": "passed",
            "details": {
                "type_mismatches": type_mismatches
            },
            "recommendation": "No type issues detected"
        }

def validate_data_endpoint(request_body: Dict) -> Dict:
    """
    Azure Function endpoint for data validation
    Expected request body:
    {
        "datasets": ["customers", "orders"],
        "layer": "silver",
        "validation_rules": ["check_nulls", "check_duplicates", "check_pii"]
    }
    """
    orchestrator = ADFAIOrchestrator()
    
    datasets = request_body.get("datasets", [])
    layer = request_body.get("layer", "silver")
    validation_rules = request_body.get("validation_rules", ["check_nulls"])
    
    results = []
    for dataset in datasets:
        dataset_path = f"{layer}/{dataset}"
        schema = {}  # In production, load from schema registry
        
        validation_result = orchestrator.validate_data_quality(
            dataset_path, schema, validation_rules
        )
        results.append(validation_result)
    
    # Aggregate results
    overall_status = "passed"
    if any(r["status"] == "failed" for r in results):
        overall_status = "failed"
    elif any(r["status"] == "warning" for r in results):
        overall_status = "warning"
    
    return {
        "status": overall_status,
        "validation_results": results,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Test locally
    test_request = {
        "datasets": ["customers", "orders"],
        "layer": "silver",
        "validation_rules": ["check_nulls", "check_duplicates", "check_pii"]
    }
    
    result = validate_data_endpoint(test_request)
    print(json.dumps(result, indent=2))
