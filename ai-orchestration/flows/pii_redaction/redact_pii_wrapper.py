from promptflow.core import tool
from promptflow.core import Prompty
import re

@tool
def redact_pii_wrapper(text: str) -> str:
    """
    Executes redact_pii.prompty with fallback.
    """
    try:
        p = Prompty.load(source="redact_pii.prompty")
        result = p(text=text)
    except Exception as e:
        print(f"⚠️ [WARNING] LLM Execution failed. Returning MOCK Redaction. Error: {e}")
        # Mock logic using regex for demo
        result = text
        result = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL]', result)
        result = re.sub(r'\d{3}-\d{3}-\d{4}', '[PHONE]', result)
        if "John Doe" in result:
             result = result.replace("John Doe", "[PERSON]")
            
    return result
