from promptflow.core import tool
from promptflow.core import Prompty

@tool
def resolve_mapping(source_field: str, source_system: str, retrieved_context: str) -> str:
    """
    Executes the resolve_mapping.prompty file.
    """
    # Load the prompty file
    # Note: path is relative to flow directory
    p = Prompty.load(source="resolve_mapping.prompty")
    
    try:
        # Execute it
        # This requires AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in env
        result = p(
            source_field=source_field, 
            source_system=source_system, 
            retrieved_context=retrieved_context
        )
    except Exception as e:
        print(f"⚠️ [WARNING] LLM Execution failed (likely missing keys). Returning MOCK response. Error: {e}")
        # Mock Response for demo purposes
        result = {
            "target_field": "CustomerID",
            "confidence": 0.99,
            "rationale": "Simulated AI decision: KUNNR matches CustomerID based on SAP context."
        }
    
    return result
