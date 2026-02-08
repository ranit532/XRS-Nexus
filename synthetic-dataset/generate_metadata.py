import json
import random
import uuid
from datetime import datetime, timedelta

def generate_sap_metadata(count=400):
    tables = ["EKKO", "VBAK", "MARA", "KNA1", "LFA1", "BKPF", "BSEG", "MATDOC", "CDHDR", "CDPOS"]
    modules = ["MM", "SD", "FI", "CO", "PP", "QM", "PM"]
    data = []
    
    for _ in range(count):
        table = random.choice(tables)
        module = random.choice(modules)
        obj_name = f"{table}_{uuid.uuid4().hex[:4].upper()}"
        
        record = {
            "id": str(uuid.uuid4()),
            "system_id": "SAP_ECC_PROD",
            "system_type": "SAP",
            "connection_type": "SAP_NATIVE",
            "object_name": obj_name,
            "description": f"SAP {module} Table {table} - {random.choice(['Master Data', 'Transactional Data', 'Configuration'])}",
            "domain": "SupplyChain" if module in ["MM", "SD"] else "Finance",
            "schema_drift_enabled": True,
            "cdc_enabled": random.choice([True, False]),
            "sla_minutes": random.choice([15, 30, 60, 120, 1440]),
            "data_quality_rules": [
                {"field": "MANDT", "rule": "not_null"},
                {"field": "CREATED_AT", "rule": "timestamp"}
            ],
            "tags": ["critical" if random.random() > 0.8 else "standard", "sap", module],
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
        }
        data.append(record)
    return data

def generate_salesforce_metadata(count=300):
    objects = ["Account", "Contact", "Lead", "Opportunity", "Case", "Campaign", "User", "Order"]
    data = []
    
    for _ in range(count):
        obj = random.choice(objects)
        record = {
            "id": str(uuid.uuid4()),
            "system_id": "SFDC_GLOBAL",
            "system_type": "Salesforce",
            "connection_type": "SALESFORCE_ADAPTER",
            "object_name": obj,
            "description": f"Salesforce Standard Object: {obj}",
            "domain": "CRM",
            "schema_drift_enabled": False,
            "cdc_enabled": True,
            "sla_minutes": random.choice([15, 60, 240]),
            "data_quality_rules": [
                {"field": "Id", "rule": "unique"},
                {"field": "Email", "rule": "email_format"}
            ],
            "tags": ["crm", "customer-facing", "cloud"],
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
        }
        data.append(record)
    return data

def generate_api_metadata(count=300):
    apis = ["Weather", "Stock", "Currency", "Payment", "Logistics", "HR"]
    data = []
    
    for _ in range(count):
        api = random.choice(apis)
        endpoint = f"/v1/{api.lower()}/{uuid.uuid4().hex[:8]}"
        record = {
            "id": str(uuid.uuid4()),
            "system_id": f"{api.upper()}_API_GW",
            "system_type": "REST_API",
            "connection_type": "HTTP_GENERIC",
            "object_name": endpoint,
            "description": f"External {api} Provider API Endpoint",
            "domain": "External",
            "schema_drift_enabled": True,
            "cdc_enabled": False,
            "sla_minutes": 60,
            "data_quality_rules": [
                {"field": "response_code", "rule": "equals_200"}
            ],
            "tags": ["external", "api", "json"],
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
        }
        data.append(record)
    return data

if __name__ == "__main__":
    print("Generating synthetic metadata...")
    all_metadata = []
    all_metadata.extend(generate_sap_metadata(450))
    all_metadata.extend(generate_salesforce_metadata(350))
    all_metadata.extend(generate_api_metadata(300))
    
    output_file = "data/metadata_samples.json"
    with open(output_file, "w") as f:
        json.dump(all_metadata, f, indent=2)
    
    print(f"Successfully generated {len(all_metadata)} records in {output_file}")
