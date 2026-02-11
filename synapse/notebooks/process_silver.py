# Databricks Notebook: process_silver.py
# Synapse Spark version - Silver to Gold transformation

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, collect_set

# Get parameters from ADF
input_path = dbutils.widgets.get("input_path")
output_path = dbutils.widgets.get("output_path")

# Initialize Spark session
spark = SparkSession.builder.appName("Silver_to_Gold").getOrCreate()

# Read Parquet from Silver
silver_df = spark.read.parquet(f"{input_path}/metadata_clean.parquet")

# Aggregate by system and table
gold_df = silver_df.groupBy("system_normalized", "table_name").agg(
    count("source_field").alias("field_count"),
    collect_set("dq_rule").alias("applied_rules")
)

# Write to Gold as Parquet
gold_df.write.mode("overwrite").parquet(f"{output_path}/schema_stats.parquet")

# Return count for ADF
table_count = gold_df.count()
print(f"Aggregated {table_count} table-level records")
dbutils.notebook.exit(table_count)
