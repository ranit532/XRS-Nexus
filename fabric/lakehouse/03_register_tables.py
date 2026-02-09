# ==============================================================================
# Fabric Lakehouse - Table Registration Utility
# Description: Registers path-based Delta tables into the Metastore
#              to ensure Visibility in SQL Endpoint.
# ==============================================================================

from pyspark.sql import SparkSession

def register_tables(spark: SparkSession, lakehouse_name: str):
    """
    Scans the files directory and registers found Delta tables 
    to the metastore if they are missing.
    """
    print(f"Scanning Lakehouse: {lakehouse_name}...")
    
    # List of expected tables and their paths
    tables_to_register = [
        {"name": "silver_customer", "path": "Files/Silver/silver_customer"},
        {"name": "silver_sales", "path": "Files/Silver/silver_sales"},
        {"name": "dim_customer", "path": "Files/Gold/dim_customer"},
        {"name": "fact_sales", "path": "Files/Gold/fact_sales"}
    ]

    for table in tables_to_register:
        table_name = table["name"]
        table_path = f"abfss://{lakehouse_name}.dfs.fabric.microsoft.com/{table['path']}"
        
        try:
            # Check if table exists using Spark Catalog
            if not spark.catalog.tableExists(table_name):
                print(f"Registering table: {table_name} from {table_path}")
                spark.sql(f"""
                    CREATE TABLE IF NOT EXISTS {table_name}
                    USING DELTA
                    LOCATION '{table_path}'
                """)
                print(f"Successfully registered {table_name}.")
            else:
                print(f"Table {table_name} already exists. Skipping.")
                
        except Exception as e:
            print(f"Error registering {table_name}: {str(e)}")

if __name__ == "__main__":
    spark = SparkSession.builder.appName("FabricTableRegistration").getOrCreate()
    
    # In Fabric, the default lakehouse is usually attached.
    # Adjust this name based on environment
    LAKEHOUSE_NAME = "XRS_Nexus_Lakehouse" 
    
    register_tables(spark, LAKEHOUSE_NAME)
