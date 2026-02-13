#!/usr/bin/env python3
"""
Enhanced Synthetic Dataset Generator for ADF Pipeline Demo
Generates 5 distinct datasets with realistic schemas and intentional data quality issues
"""

import json
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class SyntheticDataGenerator:
    def __init__(self, output_dir: str = "data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Sample data pools
        self.first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa", 
                           "James", "Mary", "William", "Patricia", "Richard", "Jennifer", "Thomas"]
        self.last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", 
                          "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson"]
        self.cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", 
                      "San Antonio", "San Diego", "Dallas", "San Jose", "London", "Paris", "Berlin"]
        self.countries = ["USA", "UK", "Germany", "France", "Canada", "Australia", "Spain", "Italy"]
        self.product_names = ["Laptop", "Smartphone", "Tablet", "Headphones", "Monitor", "Keyboard", 
                             "Mouse", "Webcam", "Printer", "Router", "Speaker", "Charger"]
        self.categories = ["Electronics", "Computers", "Accessories", "Networking", "Audio", "Peripherals"]
        
    def generate_customers(self, num_records: int = 2000) -> List[Dict]:
        """Generate customer dataset with intentional quality issues"""
        customers = []
        for i in range(num_records):
            # Intentionally introduce nulls (5% of records)
            email = None if random.random() < 0.05 else f"{self.first_names[random.randint(0, len(self.first_names)-1)].lower()}.{self.last_names[random.randint(0, len(self.last_names)-1)].lower()}@example.com"
            
            # Intentionally introduce invalid ages (2% of records)
            age = random.randint(-5, 100) if random.random() < 0.02 else random.randint(18, 75)
            
            customer = {
                "customer_id": f"CUST{i+1:06d}",
                "first_name": random.choice(self.first_names),
                "last_name": random.choice(self.last_names),
                "email": email,
                "phone": f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "age": age,
                "city": random.choice(self.cities),
                "country": random.choice(self.countries),
                "registration_date": (datetime.now() - timedelta(days=random.randint(1, 1000))).strftime("%Y-%m-%d"),
                "is_active": random.choice([True, False]),
                "loyalty_tier": random.choice(["Bronze", "Silver", "Gold", "Platinum"])
            }
            customers.append(customer)
        
        return customers
    
    def generate_orders(self, num_records: int = 5000, num_customers: int = 2000) -> List[Dict]:
        """Generate orders dataset"""
        orders = []
        for i in range(num_records):
            # Intentionally introduce missing customer_id (3% of records)
            customer_id = None if random.random() < 0.03 else f"CUST{random.randint(1, num_customers):06d}"
            
            # Intentionally introduce negative amounts (1% of records)
            amount = random.uniform(-100, 0) if random.random() < 0.01 else random.uniform(10, 5000)
            
            order = {
                "order_id": f"ORD{i+1:08d}",
                "customer_id": customer_id,
                "order_date": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
                "order_amount": round(amount, 2),
                "order_status": random.choice(["Pending", "Shipped", "Delivered", "Cancelled", "Returned"]),
                "payment_method": random.choice(["Credit Card", "Debit Card", "PayPal", "Bank Transfer"]),
                "shipping_country": random.choice(self.countries),
                "discount_applied": random.choice([0, 5, 10, 15, 20, 25])
            }
            orders.append(order)
        
        return orders
    
    def generate_products(self, num_records: int = 500) -> List[Dict]:
        """Generate products dataset"""
        products = []
        for i in range(num_records):
            # Intentionally introduce null prices (2% of records)
            price = None if random.random() < 0.02 else round(random.uniform(10, 2000), 2)
            
            product = {
                "product_id": f"PROD{i+1:05d}",
                "product_name": f"{random.choice(self.product_names)} {random.choice(['Pro', 'Plus', 'Max', 'Ultra', 'Lite'])}",
                "category": random.choice(self.categories),
                "price": price,
                "stock_quantity": random.randint(0, 1000),
                "supplier": f"Supplier_{random.randint(1, 50)}",
                "weight_kg": round(random.uniform(0.1, 10), 2),
                "is_available": random.choice([True, False]),
                "rating": round(random.uniform(1, 5), 1)
            }
            products.append(product)
        
        return products
    
    def generate_transactions(self, num_records: int = 3000) -> List[Dict]:
        """Generate transaction dataset"""
        transactions = []
        for i in range(num_records):
            transaction = {
                "transaction_id": f"TXN{i+1:08d}",
                "order_id": f"ORD{random.randint(1, 5000):08d}",
                "transaction_date": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d %H:%M:%S"),
                "amount": round(random.uniform(10, 5000), 2),
                "currency": random.choice(["USD", "EUR", "GBP", "CAD"]),
                "transaction_type": random.choice(["Purchase", "Refund", "Chargeback"]),
                "status": random.choice(["Success", "Failed", "Pending"]),
                "gateway": random.choice(["Stripe", "PayPal", "Square", "Authorize.Net"])
            }
            transactions.append(transaction)
        
        return transactions
    
    def generate_events(self, num_records: int = 10000) -> List[Dict]:
        """Generate event logs dataset"""
        events = []
        event_types = ["page_view", "click", "add_to_cart", "checkout", "purchase", "login", "logout"]
        
        for i in range(num_records):
            event = {
                "event_id": f"EVT{i+1:010d}",
                "customer_id": f"CUST{random.randint(1, 2000):06d}",
                "event_type": random.choice(event_types),
                "event_timestamp": (datetime.now() - timedelta(seconds=random.randint(1, 86400*30))).strftime("%Y-%m-%d %H:%M:%S"),
                "page_url": f"/products/{random.randint(1, 500)}",
                "session_id": f"SESS{random.randint(1, 5000):08d}",
                "device_type": random.choice(["Desktop", "Mobile", "Tablet"]),
                "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"])
            }
            events.append(event)
        
        return events
    
    def save_to_csv(self, data: List[Dict], filename: str):
        """Save dataset to CSV format"""
        filepath = self.output_dir / filename
        if data:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print(f"✓ Generated {filepath} ({len(data)} records)")
    
    def save_to_json(self, data: List[Dict], filename: str):
        """Save dataset to JSON format"""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Generated {filepath} ({len(data)} records)")
    
    def generate_all(self):
        """Generate all datasets"""
        print("\n🔄 Generating synthetic datasets for ADF pipeline demo...\n")
        
        # Generate datasets
        customers = self.generate_customers(2000)
        orders = self.generate_orders(5000, 2000)
        products = self.generate_products(500)
        transactions = self.generate_transactions(3000)
        events = self.generate_events(10000)
        
        # Save to CSV (for ADF ingestion)
        self.save_to_csv(customers, "customers.csv")
        self.save_to_csv(orders, "orders.csv")
        self.save_to_csv(products, "products.csv")
        self.save_to_csv(transactions, "transactions.csv")
        self.save_to_csv(events, "events.csv")
        
        # Save to JSON (for reference/testing)
        self.save_to_json(customers, "customers.json")
        self.save_to_json(orders, "orders.json")
        self.save_to_json(products, "products.json")
        self.save_to_json(transactions, "transactions.json")
        self.save_to_json(events, "events.json")
        
        # Generate summary
        summary = {
            "generated_at": datetime.now().isoformat(),
            "datasets": {
                "customers": {"count": len(customers), "quality_issues": "5% null emails, 2% invalid ages"},
                "orders": {"count": len(orders), "quality_issues": "3% missing customer_id, 1% negative amounts"},
                "products": {"count": len(products), "quality_issues": "2% null prices"},
                "transactions": {"count": len(transactions), "quality_issues": "None (clean)"},
                "events": {"count": len(events), "quality_issues": "None (clean)"}
            },
            "total_records": len(customers) + len(orders) + len(products) + len(transactions) + len(events)
        }
        
        self.save_to_json(summary, "dataset_summary.json")
        
        print(f"\n✅ Successfully generated {summary['total_records']:,} total records across 5 datasets")
        print(f"📁 Output directory: {self.output_dir.absolute()}\n")

if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    generator.generate_all()
