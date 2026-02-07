import json
import random
import os
from datetime import datetime, timedelta

# Configuration
OUTPUT_DIR = "data"
SYSTEMS = ["SAP_ECC", "SAP_S4HANA", "Salesforce_CRM", "Workday_HR", "ServiceNow_ITSM"]
DATA_DOMAINS = ["Finance", "SupplyChain", "Sales", "HR", "Customer"]

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def generate_sap_metadata(system_id):
    tables = [
        {"name": "KNA1", "desc": "Customer Master", "domain": "Customer"},
        {"name": "VBAK", "desc": "Sales Document: Header Data", "domain": "Sales"},
        {"name": "VBAP", "desc": "Sales Document: Item Data", "domain": "Sales"},
        {"name": "EKKO", "desc": "Purchasing Document Header", "domain": "SupplyChain"},
        {"name": "BKPF", "desc": "Accounting Document Header", "domain": "Finance"},
    ]
    
    metadata = []
    for table in tables:
        has_cdc = random.choice([True, False])
        entry = {
            "system_id": system_id,
            "object_type": "Table",
            "object_name": table["name"],
            "description": table["desc"],
            "domain": table["domain"],
            "cdc_enabled": has_cdc,
            "load_strategy": "INCREMENTAL" if has_cdc else "FULL",
            "sla_minutes": random.choice([15, 60, 240, 1440]),
            "owner": f"team_{table['domain'].lower()}@xpsgroup.co.uk",
            "data_quality_rules": [
                {"field": "MANDT", "rule": "NOT_NULL"},
                {"field": "CREATED_AT", "rule": "DATE_FORMAT_ISO"}
            ] if random.random() > 0.3 else [],
            "dependencies": []
        }
        metadata.append(entry)
    
    # Generate IDocs
    idocs = ["DEBMAS", "MATMAS", "ORDERS", "CREMAS"]
    for idoc in idocs:
        entry = {
            "system_id": system_id,
            "object_type": "IDoc",
            "object_name": idoc,
            "description": f"{idoc} IDoc Interface",
            "domain": "Integration",
            "cdc_enabled": True,
            "load_strategy": "STREAMING",
            "sla_minutes": 5,
            "owner": "integration_center@xpsgroup.co.uk",
            "data_quality_rules": [],
            "dependencies": []
        }
        metadata.append(entry)
        
    return metadata

def generate_salesforce_metadata(system_id):
    objects = ["Account", "Contact", "Opportunity", "Lead", "Case"]
    metadata = []
    
    for obj in objects:
        entry = {
            "system_id": system_id,
            "object_type": "Object",
            "object_name": obj,
            "description": f"Salesforce {obj} Object",
            "domain": "Sales" if obj in ["Opportunity", "Lead"] else "Customer",
            "cdc_enabled": True,
            "load_strategy": "INCREMENTAL",
            "sla_minutes": 30,
            "owner": "crm_team@xpsgroup.co.uk",
            "data_quality_rules": [{"field": "Id", "rule": "UNIQUE"}],
            "dependencies": [{"system": "SAP_ECC", "object": "KNA1"}] if obj == "Account" else []
        }
        metadata.append(entry)
    return metadata

def generate_rest_api_metadata():
    apis = [
        {"name": "WeatherAPI", "endpoint": "/current", "domain": "Operations"},
        {"name": "CurrencyConverter", "endpoint": "/rates", "domain": "Finance"},
    ]
    metadata = []
    
    for api in apis:
        entry = {
            "system_id": "External_API",
            "object_type": "API_Endpoint",
            "object_name": f"{api['name']}_{api['endpoint']}",
            "description": f"External API: {api['name']}",
            "domain": api["domain"],
            "cdc_enabled": False,
            "load_strategy": "API_POLLING",
            "sla_minutes": 60,
            "owner": "digital_team@xpsgroup.co.uk",
            "connection_details": {
                "auth_type": "OAuth2",
                "base_url": f"https://api.{api['name'].lower()}.com/v1"
            },
            "dependencies": []
        }
        metadata.append(entry)
    return metadata

def main():
    ensure_output_dir()
    
    all_metadata = []
    
    # Generate SAP
    all_metadata.extend(generate_sap_metadata("SAP_ECC_PROD"))
    all_metadata.extend(generate_sap_metadata("SAP_S4HANA_TRIAL"))
    
    # Generate Salesforce
    all_metadata.extend(generate_salesforce_metadata("Salesforce_Global"))
    
    # Generate REST APIs
    all_metadata.extend(generate_rest_api_metadata())
    
    # Write to file
    output_file = os.path.join(OUTPUT_DIR, "enterprise_metadata.json")
    with open(output_file, "w") as f:
        json.dump(all_metadata, f, indent=4)
        
    print(f"Generated {len(all_metadata)} metadata entries in {output_file}")

if __name__ == "__main__":
    main()
