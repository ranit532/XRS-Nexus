import pandas as pd
import json
import os

# Paths
BRONZE_DATA = "data/metadata_samples.json"
SILVER_DATA = "data/silver_metadata.parquet"

def process_bronze():
    print("--- Simulating Spark Job: Bronze -> Silver ---")
    
    # Simulating reading from OneLake Bronze
    print(f"Reading from Bronze: {BRONZE_DATA}")
    with open(BRONZE_DATA, 'r') as f:
        data = [json.loads(line) for line in f]
    
    df = pd.DataFrame(data)
    print(f"Extracted {len(df)} records.")
    
    # Transformation: Normalize System Names
    print("Applying Transformations...")
    df['system_normalized'] = df['source_system'].str.upper().str.strip()
    
    # Transformation: Infer Data Types (Simple mapping simulation)
    df['inferred_type'] = df.apply(lambda row: 'STRING' if 'CHAR' in row.get('source_type', '') else 'UNKNOWN', axis=1)
    
    # Write to Silver (Parquet)
    print(f"Writing to Silver Lakehouse: {SILVER_DATA}")
    df.to_parquet(SILVER_DATA, index=False)
    print("✅ Bronze Processing Complete.")

if __name__ == "__main__":
    process_bronze()
