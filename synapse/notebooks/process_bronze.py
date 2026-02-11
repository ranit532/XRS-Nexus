# Databricks Notebook: process_bronze.py
# Synapse Spark version - Bronze to Silver transformation

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, upper, trim

# Get parameters from ADF
input_path = dbutils.widgets.get("input_path")
output_path = dbutils.widgets.get("output_path")

# Initialize Spark session
spark = SparkSession.builder.appName("Bronze_to_Silver").getOrCreate()

# Read JSON from Bronze
bronze_df = spark.read.json(f"{input_path}/metadata_samples.json")

# Explode data_quality_rules array to field-level records
silver_df = bronze_df.select(
    upper(trim(col("system_type"))).alias("system_normalized"),
    col("object_name").alias("table_name"),
    explode(col("data_quality_rules")).alias("rule_detail")
).select(
    col("system_normalized"),
    col("table_name"),
    col("rule_detail.field").alias("source_field"),
    col("rule_detail.rule").alias("dq_rule")
)

# Write to Silver as Parquet
silver_df.write.mode("overwrite").parquet(f"{output_path}/metadata_clean.parquet")

# Return count for ADF
record_count = silver_df.count()
print(f"Processed {record_count} field-level records")
dbutils.notebook.exit(record_count)
