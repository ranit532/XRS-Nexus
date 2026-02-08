import json
import random
import uuid
from datetime import datetime, timedelta

def generate_telemetry(count=1200):
    statuses = ["SUCCESS", "FAILED", "WARNING", "RUNNING"]
    stages = ["EXTRACT", "TRANSFORM", "LOAD", "VALIDATE"]
    errors = [
        "ConnectionTimeout: SAP Gateway not reachable",
        "DataValidationError: Email format invalid",
        "SchemaMismatch: Field 'curr' not found",
        "AuthError: Token expired",
        "NullPointer: Value cannot be null"
    ]
    data = []
    
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(count):
        status = random.choices(statuses, weights=[0.7, 0.1, 0.15, 0.05])[0]
        run_duration = random.randint(10, 3600)
        
        record = {
            "run_id": str(uuid.uuid4()),
            "pipeline_id": f"pipe_{random.randint(1000, 9999)}",
            "timestamp": (base_time + timedelta(minutes=i*2)).isoformat(),
            "status": status,
            "stage": random.choice(stages),
            "rows_processed": random.randint(0, 1000000),
            "duration_ms": run_duration * 1000,
            "cost_usd": round(run_duration * 0.05, 4),
            "region": random.choice(["uksouth", "ukwest", "northeurope"]),
        }
        
        if status == "FAILED":
            record["error_details"] = {
                "code": "ERR_500" if random.random() > 0.5 else "ERR_400",
                "message": random.choice(errors),
                "stack_trace": f"File 'main.py', line {random.randint(10, 200)} in <module>..."
            }
        
        data.append(record)
    return data

if __name__ == "__main__":
    print("Generating synthetic telemetry logs...")
    logs = generate_telemetry(1200)
    
    output_file = "data/telemetry_logs.json"
    with open(output_file, "w") as f:
        json.dump(logs, f, indent=2)
    
    print(f"Successfully generated {len(logs)} records in {output_file}")
