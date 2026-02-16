
import sqlite3

DB_PATH = "data/complex_erp.db"

def fix_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("--- FIXING PRODUCTS TABLE ---")
        # Check if priority column exists
        try:
            cursor.execute("SELECT priority FROM products LIMIT 1")
            print("✅ Column 'priority' already exists in products.")
        except sqlite3.OperationalError:
            print("⚠️ Column 'priority' missing. Adding it...")
            cursor.execute("ALTER TABLE products ADD COLUMN priority TEXT")
            print("✅ Added 'priority' column.")

        # Check if budget_cap column exists (it seemed to exist in schema receipt but let's double check)
        try:
            cursor.execute("SELECT budget_cap FROM products LIMIT 1")
            print("✅ Column 'budget_cap' already exists in products.")
        except sqlite3.OperationalError:
            print("⚠️ Column 'budget_cap' missing. Adding it...")
            cursor.execute("ALTER TABLE products ADD COLUMN budget_cap REAL")
            print("✅ Added 'budget_cap' column.")

        print("\n--- FIXING PROJECTS TABLE ---")
        # Re-create projects to match the Agent's expected "simple" schema (No FKs)
        cursor.execute("DROP TABLE IF EXISTS projects")
        cursor.execute("""
            CREATE TABLE projects (
                project_id INTEGER PRIMARY KEY, 
                name TEXT, 
                status TEXT, 
                budget REAL
            )
        """)
        # Seed Data for 'Legacy_System_Notes.md'
        # File mentions "Customer API (v1)" is decommissioning.
        # We seed it as "Active" so the Agent effectively UPDATES it.
        cursor.execute("INSERT INTO projects (name, status, budget) VALUES (?, ?, ?)", 
                       ('Customer API (v1)', 'Active', 100000.0))
        cursor.execute("INSERT INTO projects (name, status, budget) VALUES (?, ?, ?)", 
                       ('Legacy CRM', 'Active', 120000.0))
        print("✅ Re-created 'projects' table and seeded 2 records.")

        print("\n--- FIXING VENDORS TABLE ---")
        # Re-create vendors
        cursor.execute("DROP TABLE IF EXISTS vendors")
        cursor.execute("""
            CREATE TABLE vendors (
                vendor_name TEXT PRIMARY KEY, 
                status TEXT
            )
        """)
        # Seed Data for 'Vendor_Legal_Notes.md'
        cursor.execute("INSERT INTO vendors (vendor_name, status) VALUES (?, ?)", 
                       ('Acme Corp', 'Active'))
        cursor.execute("INSERT INTO vendors (vendor_name, status) VALUES (?, ?)", 
                       ('TechGlobal', 'Active'))
        print("✅ Re-created 'vendors' table and seeded 2 records.")

        conn.commit()
        conn.close()
        print("\n🎉 Database Fixes Applied Successfully!")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    fix_database()
