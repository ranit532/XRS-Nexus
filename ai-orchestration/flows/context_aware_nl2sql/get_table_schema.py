from promptflow.core import tool

@tool
def get_table_schema(table_name: str) -> str:
    """
    Retrieves the schema for a given table name (Simulated).
    """
    schemas = {
        "sales_data": """
            CREATE TABLE sales_data (
                transaction_id STRING,
                customer_id STRING,
                product_id STRING,
                amount DOUBLE,
                transaction_date DATE,
                region STRING
            ) USING DELTA
        """,
        "customers": """
            CREATE TABLE customers (
                customer_id STRING,
                name STRING,
                email STRING,
                country STRING,
                segment STRING
            ) USING DELTA
        """
    }
    
    return schemas.get(table_name.lower(), "Schema not found.")
