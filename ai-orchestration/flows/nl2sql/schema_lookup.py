from promptflow import tool

@tool
def schema_lookup(table_name: str):
    # Mock schema registry lookup
    schemas = {
        "sales_bronze": "CREATE TABLE sales_bronze (region STRING, amount DOUBLE, date DATE)",
        "customers_silver": "CREATE TABLE customers_silver (id STRING, name STRING, country STRING)"
    }
    return schemas.get(table_name, "Schema not found.")
