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

    def run_simulation(self):
        print(f"Starting simulation in {self.output_dir}...")
        
        # 1. Generate Structured Data (Customers)
        print("Generating structured customer data (SQLite)...")
        df_customers = self.generate_customer_data(num_records=200, chaos_rate=0.15)
        
        conn = sqlite3.connect(self.db_path)
        df_customers.to_sql("customers", conn, if_exists="replace", index=False)
        conn.close()
        print(f"Saved customers to {self.db_path}")

        # 2. Generate Unstructured Data (Transactions in Excel)
        # In a real scenario, this might be a raw dump from a legacy system
        print("Generating unstructured transaction data (Excel)...")
        # We use customer IDs from the structured data to create a link
        customer_ids = df_customers['customer_id'].tolist()
        df_transactions = self.generate_transaction_data(customer_ids, num_records=1000)
        
        # Add some macro-like structure or metadata sheet to simulate complexity
        with pd.ExcelWriter(self.excel_path, engine='openpyxl') as writer:
            df_transactions.to_excel(writer, sheet_name='Raw_Transactions', index=False)
            
            # Metadata sheet explaining the "schema" loosely
            metadata = pd.DataFrame([
                {"Column": "transaction_id", "Description": "Unique ID"},
                {"Column": "customer_id", "Description": "Link to Customer DB"},
                {"Column": "amount", "Description": "Transaction Value"},
                {"Column": "product", "Description": "Product Name"}
            ])
            metadata.to_excel(writer, sheet_name='_Metadata', index=False)
            
        print(f"Saved transactions to {self.excel_path}")
        print("Simulation complete.")

if __name__ == "__main__":
    sim = DataSimulator()
    sim.run_simulation()
