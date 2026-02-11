from promptflow.core import tool
from promptflow.core import Prompty

@tool
def generate_sql_wrapper(question: str, schema: str) -> str:
    """
    Executes generate_sql.prompty with fallback.
    """
    try:
        p = Prompty.load(source="generate_sql.prompty")
        result = p(question=question, schema=schema)
    except Exception as e:
        print(f"⚠️ [WARNING] LLM Execution failed. Returning MOCK SQL. Error: {e}")
        # Mock logic based on input
        if "sales" in question.lower() and "region" in question.lower():
            result = "SELECT region, SUM(amount) as total_sales FROM sales_data GROUP BY region"
        else:
            result = "SELECT * FROM sales_data LIMIT 10"
            
    return result
