import pandas as pd
import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker()

class DataSimulator:
    def __init__(self, output_dir="data/simulation"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.db_path = os.path.join(output_dir, "structured_data.db")
        self.excel_path = os.path.join(output_dir, "unstructured_data.xlsx")

    def generate_random_date(self, start_date="-2y", end_date="now"):
        return fake.date_between(start_date=start_date, end_date=end_date)

    def generate_stale_date(self):
        # Generate a date that is significantly old (e.g., > 5 years)
        return fake.date_between(start_date="-10y", end_date="-5y")

    def generate_customer_data(self, num_records=100, chaos_rate=0.1):
        data = []
        for _ in range(num_records):
            is_chaos = random.random() < chaos_rate
            
            if is_chaos:
                # Introduce chaos: Stale dates, missing names, or null emails
                chaos_type = random.choice(['stale_date', 'missing_email', 'null_name'])
                if chaos_type == 'stale_date':
                    record = {
                        "customer_id": fake.uuid4(),
                        "name": fake.name(),
                        "email": fake.email(),
                        "signup_date": self.generate_stale_date(),
                        "status": "Active"
                    }
                elif chaos_type == 'missing_email':
                    record = {
                        "customer_id": fake.uuid4(),
                        "name": fake.name(),
                        "email": None,
                        "signup_date": self.generate_random_date(),
                        "status": "Active"
                    }
                else: # null_name
                    record = {
                        "customer_id": fake.uuid4(),
                        "name": None,
                        "email": fake.email(),
                        "signup_date": self.generate_random_date(),
                        "status": "Active"
                    }
            else:
                record = {
                    "customer_id": fake.uuid4(),
                    "name": fake.name(),
                    "email": fake.email(),
                    "signup_date": self.generate_random_date(),
                    "status": "Active"
                }
            data.append(record)
        return pd.DataFrame(data)

    def generate_transaction_data(self, customer_ids, num_records=500):
        data = []
        for _ in range(num_records):
            record = {
                "transaction_id": fake.uuid4(),
                "customer_id": random.choice(customer_ids),
                "amount": round(random.uniform(10.0, 1000.0), 2),
                "transaction_date": self.generate_random_date(),
                "product": fake.word()
            }
            data.append(record)
        return pd.DataFrame(data)

    def generate_csv_data(self, num_records=200):
        print("Generating structured vendor data (CSV)...")
        data = []
        for _ in range(num_records):
            record = {
                "vendor_id": fake.company_suffix() + "-" + str(random.randint(100, 999)),
                "vendor_name": fake.company(),
                "category": random.choice(["Cloud Services", "Hardware", "Consulting", "Office Supplies"]),
                "last_contract_review": self.generate_random_date()
            }
            data.append(record)
        df = pd.DataFrame(data)
        csv_path = os.path.join(self.output_dir, "vendor_contracts.csv")
        df.to_csv(csv_path, index=False)
        print(f"Saved CSV to {csv_path}")

    def generate_logs(self, num_entries=50):
        print("Generating system logs (LOG)...")
        log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        log_path = os.path.join(self.output_dir, "system_runtime.log")
        with open(log_path, "w") as f:
            for _ in range(num_entries):
                timestamp = datetime.now() - timedelta(minutes=random.randint(0, 10000))
                level = random.choice(log_levels)
                msg = fake.sentence()
                f.write(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {level}: {msg}\n")
        print(f"Saved logs to {log_path}")

    def generate_txt_notes(self):
        print("Generating business notes (TXT)...")
        notes_path = os.path.join(self.output_dir, "discovery_notes.txt")
        content = f"""
        Discovery Session: XRS Nexus Project
        Date: {datetime.now().strftime('%Y-%m-%d')}
        
        Key Findings:
        - Legacy transaction data is stored in Excel sheets named 'Raw_Transactions'.
        - Customer master data resides in the 'customers' table of the centralized SQLite DB.
        - Vendor contracts are currently maintained in CSV format for bulk processing.
        - Important: The lineage from Excel to SQL must be validated by a human.
        """
        with open(notes_path, "w") as f:
            f.write(content)
        print(f"Saved notes to {notes_path}")

    def generate_pyspark_mock(self):
        print("Generating ETL scripts (PySpark)...")
        pyspark_path = os.path.join(self.output_dir, "etl_pipeline_v1.py")
        content = """from pyspark.sql import SparkSession
import pyspark.functions as F

spark = SparkSession.builder.appName("XRS_Nexus_ETL").getOrCreate()

# Load raw transactions from Excel/CSV
raw_df = spark.read.format("csv").option("header", "true").load("vendor_contracts.csv")

# Transformation logic
# Joining with customer master data from SQLite
cleaned_df = raw_df.filter(F.col("vendor_id").isNotNull())

# Write to target Gold Layer
cleaned_df.write.mode("overwrite").parquet("gold_v1/vendor_master")
"""
        with open(pyspark_path, "w") as f:
            f.write(content)
        print(f"Saved PySpark mock to {pyspark_path}")

    def run_simulation(self):
        print(f"Starting expanded discovery simulation in {self.output_dir}...")
        
        # 1. Generate Structured Data (Customers)
        print("Generating structured customer data (SQLite)...")
        df_customers = self.generate_customer_data(num_records=200, chaos_rate=0.15)
        
        conn = sqlite3.connect(self.db_path)
        df_customers.to_sql("customers", conn, if_exists="replace", index=False)
        conn.close()
        print(f"Saved customers to {self.db_path}")

        # 2. Generate Unstructured Data (Transactions in Excel)
        print("Generating unstructured transaction data (Excel)...")
        customer_ids = df_customers['customer_id'].tolist()
        df_transactions = self.generate_transaction_data(customer_ids, num_records=1000)
        
        with pd.ExcelWriter(self.excel_path, engine='openpyxl') as writer:
            df_transactions.to_excel(writer, sheet_name='Raw_Transactions', index=False)
            metadata = pd.DataFrame([
                {"Column": "transaction_id", "Description": "Unique ID"},
                {"Column": "customer_id", "Description": "Link to Customer DB"},
                {"Column": "amount", "Description": "Transaction Value"},
                {"Column": "product", "Description": "Product Name"}
            ])
            metadata.to_excel(writer, sheet_name='_Metadata', index=False)
        print(f"Saved transactions to {self.excel_path}")

        # 3. New Data discovery Formats
        self.generate_csv_data()
        self.generate_logs()
        self.generate_txt_notes()
        self.generate_pyspark_mock()

        print("Discovery Simulation complete.")

if __name__ == "__main__":
    sim = DataSimulator()
    sim.run_simulation()
