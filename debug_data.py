
import sqlite3
import json

DB_PATH = "data/complex_erp.db"

def inspect_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Access columns by name
        cursor = conn.cursor()
        
        print("\n--- SCHEMA ---")
        schema = cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='departments'").fetchone()
        print(schema[0] if schema else "Table not found")
        
        print("\n--- DATA ---")
        rows = cursor.execute("SELECT * FROM departments").fetchall()
        for row in rows:
            print(dict(row))
            
        print("\n--- MANUAL UPDATE TEST (ID=2) ---")
        try:
            cursor.execute("UPDATE departments SET budget = budget * 0.7 WHERE id = 2")
            print(f"Rows affected by test update (id=2): {cursor.rowcount}")
        except Exception as e:
            print(f"Update Error: {e}")
            
        print("\n--- MANUAL UPDATE TEST (ID='2') ---")
        try:
            cursor.execute("UPDATE departments SET budget = budget * 0.7 WHERE id = '2'")
            print(f"Rows affected by test update (id='2'): {cursor.rowcount}")
        except Exception as e:
            print(f"Update Error: {e}")

        conn.rollback() # Don't actually change it
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    inspect_data()
