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
        data = json.load(f)
    
    print(f"Extracted {len(data)} table records.")
    
    # Flatten/Explode to get Field Level Data if possible
    flat_data = []
    for row in data:
        system = row.get('system_type', 'UNKNOWN')
        # Use data_quality_rules as proxy for fields if available
        rules = row.get('data_quality_rules', [])
        if rules:
            for r in rules:
                flat_data.append({
                    "system_normalized": system.upper().strip(),
                    "source_field": r.get('field', 'UNKNOWN'),
                    "source_type": "INFERRED", # Rule doesn't give type directly, just assume inferred
                    "rule": r.get('rule', '')
                })
        else:
             # Fallback if no rules/fields
             flat_data.append({
                    "system_normalized": system.upper().strip(),
                    "source_field": "UNKNOWN_FIELD",
                    "source_type": "UNKNOWN",
                    "rule": "N/A"
             })

    df = pd.DataFrame(flat_data)
    print(f"Transformed to {len(df)} field-level records.")
    
    # Transformation: Infer Data Types (Mock logic)
    df['inferred_type'] = df.apply(lambda row: 'STRING' if 'CHAR' in row.get('rule', '').upper() else 'UNKNOWN', axis=1)
    
    # Write to Silver (Parquet)
    print(f"Writing to Silver Lakehouse: {SILVER_DATA}")
    df.to_parquet(SILVER_DATA, index=False)
    print("✅ Bronze Processing Complete.")

if __name__ == "__main__":
    process_bronze()
