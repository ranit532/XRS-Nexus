from promptflow.core import tool
from typing import List, Dict

@tool
def retrieve_schemas(source_field: str, source_system: str) -> str:
    """
    Simulates a RAG retrieval from multiple knowledge bases (SAP, Salesforce, Enterprise Data Dictionary).
    In a real scenario, this would query Azure AI Search indexes.
    """
    
    # Simulated Knowledge Base (Vector Store results)
    sap_dictionary = {
        "KUNNR": {"description": "Customer Number", "type": "VARCHAR(10)", "system": "SAP"},
        "MATNR": {"description": "Material Number", "type": "VARCHAR(18)", "system": "SAP"},
        "BUKRS": {"description": "Company Code", "type": "VARCHAR(4)", "system": "SAP"}
    }
    
    salesforce_dictionary = {
        "AccountNum": {"description": "Unique identifier for the account", "type": "String", "system": "Salesforce"},
        "ProductCode": {"description": "Code identifying the product", "type": "String", "system": "Salesforce"}
    }
    
    enterprise_canonical = {
        "CustomerID": {"description": "Global unique identifier for customers", "type": "String", "format": "UUID"},
        "MaterialID": {"description": "Global material identifier", "type": "String"},
        "LegalEntityID": {"description": "Legal entity or company code", "type": "String"}
    }

    # Simulate Retrieval Logic
    results = []
    
    # 1. Exact Match in Source System
    if source_system == "SAP" and source_field in sap_dictionary:
        results.append(f"Found in SAP Dictionary: {sap_dictionary[source_field]}")
    elif source_system == "Salesforce" and source_field in salesforce_dictionary:
        results.append(f"Found in Salesforce Dictionary: {salesforce_dictionary[source_field]}")
        
    # 2. Fuzzy/Semantic matches in Canonical (Simulated)
    # Ideally logic: "KUNNR" -> "Customer" -> "CustomerID"
    if source_field in ["KUNNR", "AccountNum"]:
        results.append(f"Potential Canonical Match: {enterprise_canonical['CustomerID']}")
    elif source_field in ["MATNR", "ProductCode"]:
        results.append(f"Potential Canonical Match: {enterprise_canonical['MaterialID']}")
    elif source_field in ["BUKRS"]:
        results.append(f"Potential Canonical Match: {enterprise_canonical['LegalEntityID']}")

    return "\n".join(results)
