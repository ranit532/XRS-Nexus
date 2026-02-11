from promptflow.core import tool
from promptflow.core import Prompty

@tool
def rule_translator_wrapper(rule: str) -> str:
    """
    Executes rule_translator.prompty with fallback.
    """
    try:
        p = Prompty.load(source="rule_translator.prompty")
        result = p(rule=rule)
    except Exception as e:
        print(f"⚠️ [WARNING] LLM Execution failed. Returning MOCK Code. Error: {e}")
        # Mock logic
        rule_lower = rule.lower()
        if "revenue" in rule_lower and "positive" in rule_lower:
             result = 'df.expect_column_values_to_be_between("revenue", min_value=0, strictly=True)'
        elif "email" in rule_lower:
             result = 'df.expect_column_values_to_match_regex("email", r"[^@]+@[^@]+\.[^@]+")'
        elif "null" in rule_lower:
             # extract field name if possible, simplified
             result = 'df.expect_column_values_to_not_be_null(column="<inferred_field>")'
        else:
             result = '# Rule could not be translated automatically (Mock limitation)'
    
    return result
