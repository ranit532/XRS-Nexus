import sqlite3
import pandas as pd
import json
import os
from langchain.tools import tool
from graph.lineage_graph import LineageGraph

# Initialize Graph
graph_db = LineageGraph()

@tool
def inspect_excel_structure(filepath: str):
    """Inspects the sheets and columns of an Excel file to understand its structure."""
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"
    try:
        xl = pd.ExcelFile(filepath)
        structure = {}
        for sheet in xl.sheet_names:
            df = xl.parse(sheet, nrows=5)
            structure[sheet] = list(df.columns)
        return json.dumps(structure, indent=2)
    except Exception as e:
        return f"Error reading Excel: {str(e)}"

@tool
def inspect_database_schema(db_path: str):
    """Inspects the tables and columns of a SQLite database."""
    if not os.path.exists(db_path):
        return f"Database not found: {db_path}"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        schema = {}
        for (table_name,) in tables:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [info[1] for info in cursor.fetchall()]
            schema[table_name] = columns
        conn.close()
        return json.dumps(schema, indent=2)
    except Exception as e:
        return f"Error reading DB: {str(e)}"

@tool
def get_etl_lineage_logs(log_path: str = "data/simulation/etl_lineage_log.json"):
    """Reads the ETL execution logs to discover data lineage."""
    if not os.path.exists(log_path):
        return "No ETL logs found."
    try:
        with open(log_path, 'r') as f:
            logs = json.load(f)
        
        # summary for the LLM
        summary = []
        for entry in logs:
            status_note = ""
            if entry.get("status") == "PENDING_APPROVAL":
                status_note = " [⚠️ ACTION REQUIRED: PENDING_APPROVAL]"
            
            # Clean up source/target for better visuals
            source = entry['source'].replace("file://data/simulation/", "").replace("sqlite://data/simulation/", "DB: ").replace("/sheet/", " (Sheet: ").replace("/table/", " (Table: ").strip(")") + ")"
            if source.endswith("))"): source = source[:-1]
            
            target = entry['target'].replace("file://data/simulation/", "").replace("sqlite://data/simulation/", "DB: ").replace("/sheet/", " (Sheet: ").replace("/table/", " (Table: ").strip(")") + ")"
            if target.endswith("))"): target = target[:-1]

            summary.append(f"{entry['timestamp']}: {source} -> {target} ({entry['transformation']}){status_note}")
            
        return "\n".join(summary)
    except Exception as e:
        return f"Error reading logs: {str(e)}"

@tool
def approve_correction(correction_id: str, approved: bool):
    """
    Simulates approving or rejecting a data correction.
    In a real system, this would trigger a callback or update a DB state.
    """
    if approved:
        return f"Correction {correction_id} APPROVED. The ETL pipeline will apply the fix in the next run."
    else:
        return f"Correction {correction_id} REJECTED. The data will remain as is."

@tool
def push_lineage_to_graph(source: str, target: str, transformation: str):
    """Pushes a lineage relationship to the Neo4j graph."""
    if not graph_db.driver:
        return "Graph database not connected."
    
    # Create nodes
    graph_db.add_node("DataEntity", source)
    graph_db.add_node("DataEntity", target)
    
    # Create edge
    graph_db.add_relationship(source, target, "TRANSFORMS_TO", {"method": transformation})
    return f"Added lineage: {source} -> {target}"

@tool
def check_data_quality(db_path: str, table_name: str):
    """Checks for data quality issues like null values or stale dates in a table."""
    if not os.path.exists(db_path):
        return f"Database not found: {db_path}"
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        
        report = {
            "total_rows": len(df),
            "null_counts": df.isnull().sum().to_dict(),
            "sample_rows": df.head(5).to_dict(orient='records')
        }
        return json.dumps(report, indent=2)
    except Exception as e:
        return f"Error checking quality: {str(e)}"

@tool
def push_lineage_to_graph(source: str, target: str, transformation: str):
    """Pushes a lineage relationship to the Neo4j graph."""
    if not graph_db.driver:
        return "Graph database not connected."
    
    # Create nodes
    graph_db.add_node("DataEntity", source)
    graph_db.add_node("DataEntity", target)
    
    # Create edge
    graph_db.add_relationship(source, target, "TRANSFORMS_TO", {"method": transformation})
    return f"Added lineage: {source} -> {target}"
