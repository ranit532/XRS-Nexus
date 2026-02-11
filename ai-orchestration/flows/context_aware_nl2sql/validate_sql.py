from promptflow.core import tool

@tool
def validate_sql(sql_query: str) -> str:
    """
    Basic validation of SparkSQL syntax.
    """
    if not sql_query:
        return "INVALID: Empty query"
    
    forbidden_keywords = ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT"]
    upper_sql = sql_query.upper()
    
    for kw in forbidden_keywords:
        if kw in upper_sql:
            return f"INVALID: Query contains forbidden keyword '{kw}' (Read-only allowed)."
            
    if not upper_sql.startswith("SELECT") and not upper_sql.startswith("WITH"):
         return "INVALID: Query must start with SELECT or WITH."
         
    return "VALID"
