import json
import random
import sys
import os

# Ensure we can import from local modules if needed, but we use pf.test
from promptflow.client import PFClient

def load_data(path):
    with open(path, 'r') as f:
        return json.load(f)

def run_integrated_demo():
    print("----------------------------------------------------------------")
    print("🚀 XRS NEXUS: Integrated AI & Data Demo")
    print("----------------------------------------------------------------")
    
    pf = PFClient()
    
    # 1. Load Metadata
    print("\n[1] Ingesting Metadata from Bronze Lakehouse...")
    try:
        metadata = load_data("data/metadata_samples.json")
        record = random.choice(metadata)
        print(f"    Selected Table: {record['object_name']} ({record['system_type']})")
        
        # Pick a field for Schema Mapping
        if 'data_quality_rules' in record and record['data_quality_rules']:
            field_info = record['data_quality_rules'][0]
            source_field = field_info['field']
            print(f"    Selected Field: {source_field}")
            
            # RUN USE CASE 1
            print("\n    Refining Schema with AI (Use Case 1)...")
            inputs = {"source_field": source_field, "source_system": record['system_type']}
            result = pf.test(flow="ai-orchestration/flows/advanced_schema_mapping", inputs=inputs)
            print(f"    ✅ Mapped {source_field} -> {result.get('target_field', 'UNKNOWN')}")
            
            # RUN USE CASE 5 (DQ Rule)
            rule_type = field_info['rule']
            # Convert simple metadata rule to Natural Language
            nl_rule = f"{source_field} must be {rule_type}"
            if rule_type == 'not_null':
                nl_rule = f"{source_field} cannot be null"
                
            print(f"\n    Generating DQ Logic (Use Case 5)...")
            print(f"    Rule: '{nl_rule}'")
            inputs = {"rule": nl_rule}
            result = pf.test(flow="ai-orchestration/flows/dq_rules", inputs=inputs)
            print(f"    ✅ Python Assertion: {result.get('python_code', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Metadata step failed: {e}")

    # 2. Analyze Telemetry
    print("\n[2] Monitoring Pipeline Telemetry...")
    try:
        # Simulate an error detection
        print("    Fetching recent logs from Application Insights...")
        error_sample = "spark.executor.memory overhead exceeded. Container killed by YARN."
        print(f"    ⚠️ CRITICAL ERROR DETECTED: {error_sample}")
        
        # RUN USE CASE 4
        print("\n    Diagnosing Root Cause (Use Case 4)...")
        inputs = {"error_log": error_sample}
        result = pf.test(flow="ai-orchestration/flows/error_rca", inputs=inputs)
        print(f"    ✅ Root Cause: {result.get('analysis', {}).get('root_cause', 'Unknown')}")
        print(f"    🛠  Suggested Fix: {result.get('analysis', {}).get('fix', 'Check logs')}")
        
    except Exception as e:
        print(f"❌ Telemetry step failed: {e}")

    print("\n----------------------------------------------------------------")
    print("🎉 Demo Complete. The Nexus is operational.")
    print("----------------------------------------------------------------")

if __name__ == "__main__":
    run_integrated_demo()
