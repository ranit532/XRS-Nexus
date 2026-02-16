
import sys
import os
import sqlite3

# Ensure we can import from api-layer
sys.path.append(os.path.join(os.getcwd(), 'api-layer'))

from complex_query_engine import ComplexQueryEngine

print("--- STARTING DEBUG ---")
try:
    engine = ComplexQueryEngine()
    print("\n--- INJECTED SCHEMA SUMMARY ---")
    print(engine.schema_summary)
    print("-------------------------------")
    
    expected_tables = ["departments", "projects", "products", "vendors"]
    print("\n--- TABLE VERIFICATION ---")
    for t in expected_tables:
        if f"- {t}:" in engine.schema_summary:
            print(f"✅ Table '{t}' FOUND in schema summary.")
        else:
            print(f"❌ Table '{t}' MISSING from schema summary.")

except Exception as e:
    print(f"❌ ERROR: {e}")
print("--- END DEBUG ---")
