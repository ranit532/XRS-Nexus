# Databricks notebook source
# MAGIC %md
# MAGIC # AI Orchestration with Prompt Flow
# MAGIC Integrate Databricks with Azure AI Prompt Flow for intelligent processing

# COMMAND ----------

# Get parameters from ADF
dbutils.widgets.text("storage_account", "", "Storage Account Name")
dbutils.widgets.text("bronze_path", "", "Bronze Path")

storage_account = dbutils.widgets.get("storage_account")
bronze_path = dbutils.widgets.get("bronze_path")

print(f"Storage Account: {storage_account}")
print(f"Bronze Path: {bronze_path}")

# COMMAND ----------

# Install Prompt Flow SDK
# %pip install promptflow promptflow-tools azure-identity
# Note: Uncomment above line when running in Databricks

# COMMAND ----------

# Read metadata from Bronze
df_metadata = spark.read.json(f"{bronze_path}metadata_samples.json")
sample_records = df_metadata.limit(5).toPandas()

print(f"Loaded {len(sample_records)} sample records for AI processing")

# COMMAND ----------

# Initialize Prompt Flow client
from promptflow import PFClient
from azure.identity import DefaultAzureCredential

pf = PFClient()

# COMMAND ----------

# Process each record through Prompt Flow
import json

results = []

for idx, row in sample_records.iterrows():
    # Extract field info
    if 'data_quality_rules' in row and row['data_quality_rules']:
        for rule in row['data_quality_rules']:
            field_name = rule.get('field', 'UNKNOWN')
            
            # Use Case 1: Schema Mapping
            print(f"\n[{idx}] Mapping field: {field_name}")
            try:
                mapping_result = pf.test(
                    flow="/Users/ranitsinha/Documents/XRS-Nexus/ai-orchestration/flows/advanced_schema_mapping",
                    inputs={
                        "source_field": field_name,
                        "source_system": row.get('system_type', 'UNKNOWN')
                    }
                )
                
                results.append({
                    "source_field": field_name,
                    "source_system": row.get('system_type'),
                    "target_field": mapping_result.get('target_field', 'UNMAPPED'),
                    "confidence": mapping_result.get('confidence_score', 0.0)
                })
                
                print(f"  ✅ Mapped to: {mapping_result.get('target_field')}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                results.append({
                    "source_field": field_name,
                    "error": str(e)
                })

# COMMAND ----------

# Convert results to DataFrame and save to Silver
from pyspark.sql import Row

results_df = spark.createDataFrame([Row(**r) for r in results])
output_path = f"abfss://silver@{storage_account}.dfs.core.windows.net/ai_mappings.parquet"

results_df.write.mode("overwrite").parquet(output_path)

print(f"\n✅ AI Processing Complete!")
print(f"Processed {len(results)} fields")
print(f"Results saved to: {output_path}")

# COMMAND ----------

# Return results to ADF
dbutils.notebook.exit({
    "status": "success",
    "fields_processed": len(results),
    "output_path": output_path
})
