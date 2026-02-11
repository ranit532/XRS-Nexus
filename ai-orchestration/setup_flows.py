import os
from promptflow.client import PFClient
from promptflow.client import PFClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

def run_use_case_1():
    print("\n--- Running Use Case 1: Multi-Source Schema Mapping ---")
    pf = PFClient()
    
    flow_path = "ai-orchestration/flows/advanced_schema_mapping"
    inputs = {
        "source_field": "KUNNR",
        "source_system": "SAP"
    }
    
    print(f"Executing flow at: {flow_path}")
    print(f"Inputs: {inputs}")
    
    try:
        # Test the flow
        result = pf.test(flow=flow_path, inputs=inputs)
        print("\n✅ Flow Execution Successful!")
        print("Result:")
        print(result)
    except Exception as e:
        print("\n❌ Flow Execution Failed!")
        print(e)

def run_use_case_2():
    print("\n--- Running Use Case 2: Context-Aware NL2SQL ---")
    pf = PFClient()
    
    flow_path = "ai-orchestration/flows/context_aware_nl2sql"
    inputs = {
        "question": "Show total sales by region for last year",
        "table_name": "sales_data"
    }
    
    print(f"Executing flow at: {flow_path}")
    print(f"Inputs: {inputs}")
    
    try:
        # Test the flow
        result = pf.test(flow=flow_path, inputs=inputs)
        print("\n✅ Flow Execution Successful!")
        print("Result:")
        print(result)
    except Exception as e:
        print("\n❌ Flow Execution Failed!")
        print(e)
        
def run_use_case_3():
    print("\n--- Running Use Case 3: Intelligent PII Redaction ---")
    pf = PFClient()
    
    flow_path = "ai-orchestration/flows/pii_redaction"
    inputs = {
        "text": "Please contact John Doe (john.doe@enterprise.com) regarding project XRS-123."
    }
    
    print(f"Executing flow at: {flow_path}")
    print(f"Inputs: {inputs}")
    
    try:
        # Test the flow
        result = pf.test(flow=flow_path, inputs=inputs)
        print("\n✅ Flow Execution Successful!")
        print("Result:")
        print(result)
    except Exception as e:
        print("\n❌ Flow Execution Failed!")
        print(e)

def run_use_case_4():
    print("\n--- Running Use Case 4: Automated Error Root Cause Analysis ---")
    pf = PFClient()
    
    flow_path = "ai-orchestration/flows/error_rca"
    inputs = {
        "error_log": "java.lang.OutOfMemoryError: Java heap space at org.apache.spark.scheduler.TaskSetManager..."
    }
    
    print(f"Executing flow at: {flow_path}")
    print(f"Inputs: {inputs}")
    
    try:
        # Test the flow
        result = pf.test(flow=flow_path, inputs=inputs)
        print("\n✅ Flow Execution Successful!")
        print("Result:")
        print(result)
    except Exception as e:
        print("\n❌ Flow Execution Failed!")
        print(e)
        
def run_use_case_5():
    print("\n--- Running Use Case 5: Natural Language Data Quality Rules ---")
    pf = PFClient()
    
    flow_path = "ai-orchestration/flows/dq_rules"
    inputs = {
        "rule": "Revenue must be positive."
    }
    
    print(f"Executing flow at: {flow_path}")
    print(f"Inputs: {inputs}")
    
    try:
        # Test the flow
        result = pf.test(flow=flow_path, inputs=inputs)
        print("\n✅ Flow Execution Successful!")
        print("Result:")
        print(result)
    except Exception as e:
        print("\n❌ Flow Execution Failed!")
        print(e)

if __name__ == "__main__":
    run_use_case_1()
    run_use_case_2()
    run_use_case_3()
    run_use_case_4()
    run_use_case_5()
