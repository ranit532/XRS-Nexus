from promptflow.core import tool
from promptflow.core import Prompty
import json

@tool
def analyze_error_wrapper(error_log: str, context: str) -> str:
    """
    Executes analyze_error.prompty with fallback.
    """
    try:
        p = Prompty.load(source="analyze_error.prompty")
        result = p(error_log=error_log, context=context)
    except Exception as e:
        print(f"⚠️ [WARNING] LLM Execution failed. Returning MOCK RCA. Error: {e}")
        # Mock logic
        if "OutOfMemory" in error_log:
             result = {
                 "root_cause": "Spark executor ran out of heap memory processing a large partition.",
                 "fix": "Increase 'spark.executor.memory' from 4g to 8g.",
                 "category": "Configuration"
             }
        else:
             result = {
                 "root_cause": "Unknown error pattern.",
                 "fix": "Check upstream dependencies.",
                 "category": "Unknown"
             }
    
    return result
