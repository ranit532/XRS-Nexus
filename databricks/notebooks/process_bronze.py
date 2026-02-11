# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze to Silver ETL
# MAGIC Process raw metadata from Bronze layer to cleaned Silver layer

# COMMAND ----------

# Get parameters from ADF
dbutils.widgets.text("input_path", "", "Input Path (Bronze)")
dbutils.widgets.text("output_path", "", "Output Path (Silver)")

input_path = dbutils.widgets.get("input_path")
output_path = dbutils.widgets.get("output_path")

print(f"Input: {input_path}")
print(f"Output: {output_path}")

# COMMAND ----------

# Read JSON data from Bronze
df_raw = spark.read.json(f"{input_path}metadata_samples.json")

print(f"Loaded {df_raw.count()} records from Bronze")
df_raw.printSchema()

# COMMAND ----------

# Transform: Normalize and clean data
from pyspark.sql.functions import col, upper, explode, trim

# Explode data_quality_rules to get field-level records
df_exploded = df_raw.select(
    col("system_type").alias("source_system"),
    col("object_name").alias("table_name"),
    explode(col("data_quality_rules")).alias("rule")
)

df_clean = df_exploded.select(
    upper(trim(col("source_system"))).alias("system_normalized"),
    col("table_name"),
    col("rule.field").alias("source_field"),
    col("rule.rule").alias("dq_rule")
)

print(f"Transformed to {df_clean.count()} field-level records")
df_clean.show(5)

# COMMAND ----------

# Write to Silver as Parquet
df_clean.write.mode("overwrite").parquet(f"{output_path}metadata_clean.parquet")

print(f"✅ Written to Silver: {output_path}metadata_clean.parquet")

# COMMAND ----------

# Return success status to ADF
dbutils.notebook.exit({"status": "success", "records_processed": df_clean.count()})
