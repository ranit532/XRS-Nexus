# ==============================================================================
# Fabric OneLake - Spark Shortcut Access
# Description: Demonstrates reading from OneLake shortcuts using PySpark.
#              Shortcuts appear as local folders in the Lakehouse.
# ==============================================================================

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("OneLakeShortcutDemo").getOrCreate()

# ------------------------------------------------------------------------------
# 1. Read from ADLS Gen2 Shortcut
#    Path: Files/External/CorporateData (defined in shortcuts_config.yaml)
# ------------------------------------------------------------------------------
adls_shortcut_path = "Files/External/CorporateData/transactions.parquet"

try:
    df_adls = spark.read.parquet(adls_shortcut_path)
    print(f"Successfully read {df_adls.count()} rows from ADLS Shortcut.")
    df_adls.show(5)
except Exception as e:
    print(f"Error reading ADLS shortcut: {str(e)}")

# ------------------------------------------------------------------------------
# 2. Read from Cross-Workspace Lakehouse Shortcut
#    Path: Tables/Marketing (defined in shortcuts_config.yaml)
# ------------------------------------------------------------------------------
# Note: Tables shortcuts are registered in the Metastore, so we can use SQL or Table API
marketing_table_name = "marketing_campaign_performance" # Assuming shortcut name mapped to table

try:
    # Option A: Read via Spark SQL (if registered)
    df_marketing = spark.sql(f"SELECT * FROM {marketing_table_name} LIMIT 10")
    
    # Option B: Read via ABFSS path if it's a file shortcut
    # df_marketing = spark.read.format("delta").load("Tables/Marketing")
    
    print("Successfully read from Marketing Workspace Shortcut.")
    df_marketing.show()
except Exception as e:
    print(f"Error reading Marketing shortcut: {str(e)}")

# ------------------------------------------------------------------------------
# 3. Write processed data back to OneLake (Standard Lakehouse)
# ------------------------------------------------------------------------------
output_path = "Files/Processed/JoinedData"
df_adls.write.mode("overwrite").parquet(output_path)
print(f"Data written to {output_path}")
