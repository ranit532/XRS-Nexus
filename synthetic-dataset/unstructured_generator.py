import os
import random
import csv
import sqlite3
import faker

# Initialize Faker
fake = faker.Faker()
Faker_Seed = 42
fake.seed_instance(Faker_Seed)
random.seed(Faker_Seed)

DB_PATH = "data/complex_erp.db"
OUTPUT_DIR = "data/unstructured"

def create_unstructured_data():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Connect to DB to get valid IDs for references
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    dept_ids = [row[0] for row in cursor.execute("SELECT id FROM departments").fetchall()]
    sup_ids = [row[0] for row in cursor.execute("SELECT id FROM suppliers").fetchall()]
    prod_ids = [row[0] for row in cursor.execute("SELECT id FROM products").fetchall()]
    
    # 1. Budget_Review.md (Text referencing Departments)
    print("Generating Budget_Review.md...")
    with open(f"{OUTPUT_DIR}/Budget_Review.md", "w") as f:
        f.write("# Annual Budget Review 2025\n\n")
        f.write("The following departments have been reviewed for Q1 allocation:\n\n")
        
        for did in random.sample(dept_ids, 5):
            dept_name = cursor.execute("SELECT name FROM departments WHERE id=?", (did,)).fetchone()[0]
            budget = cursor.execute("SELECT budget FROM departments WHERE id=?", (did,)).fetchone()[0]
            
            f.write(f"## Department: {dept_name} (ID: {did})\n")
            f.write(f"Current allocation is ${budget:,.2f}. Performance has been {random.choice(['exceptional', 'steady', 'below expectations'])}.\n")
            f.write(f"Recommendation: {random.choice(['Increase by 10%', 'Maintain current level', 'Reduce by 5%'])}.\n\n")
            
        f.write("**Confidential**: This document contains sensitive financial projections.\n")

    # 2. Vendor_Contract.txt (Legal text referencing Suppliers)
    print("Generating Vendor_Contract.txt...")
    with open(f"{OUTPUT_DIR}/Vendor_Legal_Notes.txt", "w") as f:
        f.write("INTERNAL LEGAL NOTES - VENDOR DISPUTES & RENEWALS\n")
        f.write("=================================================\n\n")
        
        for sid in random.sample(sup_ids, 3):
            sup_name = cursor.execute("SELECT name FROM suppliers WHERE id=?", (sid,)).fetchone()[0]
            f.write(f"Supplier Ref: {sid} ({sup_name})\n")
            f.write(f"Status: {random.choice(['Under Review', 'Active Dispute', 'Renewal Pending'])}\n")
            f.write(f"Notes: Contract terms regarding liability clause 4.2 are being contested. Last shipment had {random.randint(1, 5)}% defect rate.\n")
            f.write("-------------------------------------------------\n")

    # 3. Strategy_Planning.csv (Simulating Excel with Macros/Logic)
    print("Generating Strategy_Planning.csv (Simulated Excel)...")
    # In a real scenario, this would be an .xlsm file. 
    # We simulate the "logic" by adding a 'Formula/Macro' column description.
    
    with open(f"{OUTPUT_DIR}/Product_Strategy_Macro.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["RowID", "Product_ID", "Product_Name", "Current_Price", "Proposed_Price", "Macro_Logic", "Strategy_Outcome"])
        
        for pid in random.sample(prod_ids, 10):
            p_data = cursor.execute("SELECT name, price FROM products WHERE id=?", (pid,)).fetchone()
            p_name = p_data[0]
            price = p_data[1]
            
            # Simulate a macro calculation
            macro = f"IF(Reference('competitor_pricing_api', ID={pid}) < {price}, 'LOWER_PRICE', 'HOLD')"
            outcome = random.choice(['REPRICE', 'HOLD', 'DISCONTINUE'])
            
            writer.writerow([
                fake.uuid4(),
                pid,
                p_name,
                f"{price:.2f}",
                f"{price * random.uniform(0.9, 1.1):.2f}",
                macro,
                outcome
            ])

    # 4. Orphaned_Notes.txt (References non-existent or legacy data)
    print("Generating Orphaned_Notes.txt...")
    with open(f"{OUTPUT_DIR}/Legacy_System_Notes.txt", "w") as f:
        f.write("MIGRATION LOGS - LEGACY SYSTEM\n")
        f.write("The following user IDs from the old system were flagged:\n\n")
        
        # Fetch some legacy user IDs
        legacy_users = [row[0] for row in cursor.execute("SELECT user_id FROM legacy_users").fetchall()]
        
        for uid in random.sample(legacy_users, 5):
            f.write(f"- User {uid}: Failed to map to new Active Directory. Data stored in 'legacy_users' table.\n")

    conn.close()
    print("Unstructured data generation complete.")

if __name__ == "__main__":
    create_unstructured_data()
