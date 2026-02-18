import pandas as pd
import sqlite3
import json
import os
from datetime import datetime

class HybridETLProcessor:
    def __init__(self, data_dir="data/simulation"):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "structured_data.db")
        self.excel_path = os.path.join(data_dir, "unstructured_data.xlsx")
        self.log_path = os.path.join(data_dir, "etl_lineage_log.json")

    def log_lineage(self, source, target, transformation, status="SUCCESS"):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "target": target,
            "transformation": transformation,
            "status": status
        }
        
        logs = []
        if os.path.exists(self.log_path):
            with open(self.log_path, "r") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        
        logs.append(log_entry)
        
        with open(self.log_path, "w") as f:
            json.dump(logs, f, indent=4)
        print(f"Logged lineage: {source} -> {target}")

    def run_etl(self):
        print("Starting Expanded Discovery & ETL Process...")
        
        # Discovery Phase Lineage
        self.log_lineage(
            source="file://data/simulation/vendor_contracts.csv",
            target="discovery_registry",
            transformation="Registry Scan: Vendor Data"
        )
        self.log_lineage(
            source="file://data/simulation/system_runtime.log",
            target="discovery_registry",
            transformation="Registry Scan: Runtime Logs"
        )
        self.log_lineage(
            source="file://data/simulation/discovery_notes.txt",
            target="discovery_registry",
            transformation="Registry Scan: Discovery Notes"
        )
        self.log_lineage(
            source="file://data/simulation/etl_pipeline_v1.py",
            target="discovery_registry",
            transformation="Registry Scan: PySpark Logic"
        )

        # 1. READ: Extract from Unstructured Source
        print(f"Reading from {self.excel_path}...")
        try:
            df_raw = pd.read_excel(self.excel_path, sheet_name='Raw_Transactions')
            self.log_lineage(
                source=f"file://{self.excel_path}/sheet/Raw_Transactions", 
                target="memory_dataframe", 
                transformation="pandas.read_excel"
            )
        except Exception as e:
            print(f"Error reading Excel: {e}")
            return

        # 2. TRANSFORM: Clean Data
        print("Transforming data...")
        total_rows = len(df_raw)
        
        # Mocking a suggested correction for the HITL flow
        self.log_lineage(
            source="memory_dataframe",
            target="memory_dataframe_clean",
            transformation="CLEANING_PENDING_APPROVAL: Found anomalous transaction amounts. Suggested Correction: Limit max amount to 10000.0",
            status="PENDING_APPROVAL"
        )
        
        # Fix Null Names (if any) by looking up in DB (simulated join/repair)
        # For this POC, we'll just fillna or drop
        df_clean = df_raw.copy()
        
        # Remove rows with null transaction_ids (Critical quality issue)
        df_clean = df_clean.dropna(subset=['transaction_id'])
        
        # Normalize amounts (e.g. ensure float)
        df_clean['amount'] = pd.to_numeric(df_clean['amount'], errors='coerce').fillna(0.0)
        
        cleaned_rows = len(df_clean)
        dropped_rows = total_rows - cleaned_rows
        
        self.log_lineage(
            source="memory_dataframe", 
            target="memory_dataframe_clean", 
            transformation=f"Data Cleaning: Dropped {dropped_rows} rows with missing IDs. Filled NaNs."
        )

        # 3. LOAD: Load into Structured DB
        print(f"Loading into {self.db_path}...")
        conn = sqlite3.connect(self.db_path)
        
        # Validate against existing customers (Referential Integrity Check)
        valid_customers = pd.read_sql("SELECT customer_id FROM customers", conn)['customer_id'].tolist()
        
        # Tag invalid customers
        df_clean['is_valid_customer'] = df_clean['customer_id'].isin(valid_customers)
        valid_transactions = df_clean[df_clean['is_valid_customer']].drop(columns=['is_valid_customer'])
        invalid_transactions = df_clean[~df_clean['is_valid_customer']].drop(columns=['is_valid_customer'])
        
        # Write valid to main table
        valid_transactions.to_sql("transactions_processed", conn, if_exists="replace", index=False)
        self.log_lineage(
            source="memory_dataframe_clean", 
            target=f"sqlite://{self.db_path}/table/transactions_processed", 
            transformation="Load valid transactions"
        )
        
        # Write invalid to error table
        if not invalid_transactions.empty:
            invalid_transactions.to_sql("transactions_error", conn, if_exists="replace", index=False)
            self.log_lineage(
                source="memory_dataframe_clean", 
                target=f"sqlite://{self.db_path}/table/transactions_error", 
                transformation="Filter & Load invalid transactions (orphaned)"
            )
            
        conn.close()
        print("ETL Process Complete.")

if __name__ == "__main__":
    etl = HybridETLProcessor()
    etl.run_etl()
