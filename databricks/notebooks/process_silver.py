# Databricks notebook source
# MAGIC %md
# MAGIC # Silver to Gold ETL
# MAGIC Aggregate cleaned data from Silver to Gold layer

# COMMAND ----------

# Get parameters from ADF
dbutils.widgets.text("input_path", "", "Input Path (Silver)")
dbutils.widgets.text("output_path", "", "Output Path (Gold)")

input_path = dbutils.widgets.get("input_path")
output_path = dbutils.widgets.get("output_path")

print(f"Input: {input_path}")
print(f"Output: {output_path}")

# COMMAND ----------

# Read Parquet from Silver
df_silver = spark.read.parquet(f"{input_path}metadata_clean.parquet")

print(f"Loaded {df_silver.count()} records from Silver")
df_silver.printSchema()

# COMMAND ----------

# Aggregate: Create schema statistics
from pyspark.sql.functions import count, countDistinct, collect_set

df_gold = df_silver.groupBy("system_normalized", "table_name").agg(
    count("source_field").alias("field_count"),
    countDistinct("source_field").alias("unique_fields"),
    collect_set("dq_rule").alias("applied_rules")
)

print(f"Aggregated to {df_gold.count()} table-level records")
df_gold.show(5, truncate=False)

# COMMAND ----------

# Write to Gold as Parquet
df_gold.write.mode("overwrite").parquet(f"{output_path}schema_stats.parquet")

print(f"✅ Written to Gold: {output_path}schema_stats.parquet")

# COMMAND ----------

# Return success status to ADF
dbutils.notebook.exit({"status": "success", "tables_processed": df_gold.count()})
