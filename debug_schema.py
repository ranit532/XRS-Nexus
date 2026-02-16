
import sys
import os
import sqlite3

# Ensure we can import from api-layer
sys.path.append(os.path.join(os.getcwd(), 'api-layer'))

from complex_query_engine import ComplexQueryEngine

print("--- STARTING DEBUG ---")
try:
    engine = ComplexQueryEngine()
    print("\n--- SCHEMA SUMMARY CONTENT ---")
    print(engine.schema_summary)
    print("------------------------------")
    
    if not engine.schema_summary:
        print("❌ SCHEMA SUMMARY IS EMPTY!")
    else:
        print("✅ GENERIC SCHEMA SUMMARY FOUND")
        
    if "departments" in engine.schema_summary:
        print("✅ 'departments' table found in schema")
    else:
        print("❌ 'departments' table NOT found in schema")

except Exception as e:
    print(f"❌ ERROR: {e}")
print("--- END DEBUG ---")
