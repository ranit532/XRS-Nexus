
import sqlite3

DB_PATH = "data/complex_erp.db"

def reset_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("--- RESETTING DEPARTMENTS TABLE ---")
        # Drop and Recreate to be sure
        cursor.execute("DROP TABLE IF EXISTS departments")
        cursor.execute("""
            CREATE TABLE departments (
                id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT,
                budget REAL
            )
        """)
        
        # Insert Valid Data (matching Budget_Review.md start state)
        # Sales: 216,739.00
        # Engineering: 770,486.00
        # Support: 356,787.00
        # Marketing: 126,225.00
        # Legal: 246,316.00
        # HR, Finance, Product: Unknown/Null for now or dummy
        
        data = [
            (1, 'Engineering', 'North Judithbury', 770486.00),
            (2, 'Sales', 'East Jill', 216739.00),
            (3, 'Marketing', 'New Roberttown', 126225.00),
            (6, 'Support', 'Robinsonshire', 356787.00),
            (8, 'Legal', 'Lake Roberto', 246316.00),
            (4, 'HR', 'East Jessetown', 100000.00),
            (5, 'Finance', 'Lake Debra', 150000.00),
            (7, 'Product', 'Lisatown', 200000.00)
        ]
        
        cursor.executemany("INSERT INTO departments (id, name, location, budget) VALUES (?, ?, ?, ?)", data)
        conn.commit()
        
        print(f"✅ Reset complete. Inserted {cursor.rowcount} rows.")
        
        # Verify
        print("\n--- VERIFYING DATA ---")
        for row in cursor.execute("SELECT * FROM departments"):
            print(row)
            
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    reset_db()
