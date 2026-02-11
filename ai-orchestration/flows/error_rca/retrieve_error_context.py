from promptflow.core import tool

@tool
def retrieve_error_context(error_message: str) -> str:
    """
    Simulates retrieval from a Known Error Database (KEDB) or Stack Overflow.
    """
    kedb = {
        "OutOfMemoryError": "Solution: Increase executor memory in Spark configuration. Check for data skew.",
        "TimeoutException": "Solution: Increase network timeout settings. Check firewall rules.",
        "Py4JJavError": "Solution: Check if the Spark Context is active. Verify UDF serialization."
    }
    
    # Simple keyword matching for simulation
    context = []
    for key, value in kedb.items():
        if key.lower() in error_message.lower():
            context.append(f"Known Issue: {key}\n{value}")
            
    if not context:
        return "No known issues found in KEDB."
        
    return "\n".join(context)
