from pyspark.sql import SparkSession
import pyspark.functions as F

spark = SparkSession.builder.appName("XRS_Nexus_ETL").getOrCreate()

# Load raw transactions from Excel/CSV
raw_df = spark.read.format("csv").option("header", "true").load("vendor_contracts.csv")

# Transformation logic
# Joining with customer master data from SQLite
cleaned_df = raw_df.filter(F.col("vendor_id").isNotNull())

# Write to target Gold Layer
cleaned_df.write.mode("overwrite").parquet("gold_v1/vendor_master")
