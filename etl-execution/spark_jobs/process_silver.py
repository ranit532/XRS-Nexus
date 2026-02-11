import pandas as pd
import os

# Paths
SILVER_DATA = "data/silver_metadata.parquet"
GOLD_DATA = "data/gold_schema_stats.parquet"

def process_silver():
    print("--- Simulating Spark Job: Silver -> Gold ---")
    
    if not os.path.exists(SILVER_DATA):
        print("❌ Silver data not found. Run process_bronze.py first.")
        return

    # Simulating reading from Silver Delta Table
    print(f"Reading from Silver: {SILVER_DATA}")
    df = pd.read_parquet(SILVER_DATA)
    
    # Aggregation: Count fields per system
    print("Aggregating Data...")
    gold_df = df.groupby('system_normalized').agg(
        total_fields=('source_field', 'count'),
        unique_types=('source_type', 'nunique')
    ).reset_index()
    
    # Write to Gold
    print(f"Writing to Gold Lakehouse: {GOLD_DATA}")
    gold_df.to_parquet(GOLD_DATA, index=False)
    
    print("✅ Gold Processing Complete.")
    print("\n--- Gold Layer Stats ---")
    print(gold_df)

if __name__ == "__main__":
    process_silver()
