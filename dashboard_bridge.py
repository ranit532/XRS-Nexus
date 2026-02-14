#!/usr/bin/env python3
import os
import json
import time
from flask import Flask, jsonify
from flask_cors import CORS
from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration from environment
RESOURCE_GROUP = "xrs-nexus-dev-rg"
FACTORY_NAME = "xrs-nexus-dev-adf-2yd1hw"
SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")

if not SUBSCRIPTION_ID:
    print("ERROR: AZURE_SUBSCRIPTION_ID environment variable is not set!")

credential = DefaultAzureCredential()
try:
    adf_client = DataFactoryManagementClient(credential, SUBSCRIPTION_ID) if SUBSCRIPTION_ID else None
except Exception as e:
    print(f"Failed to initialize ADF client: {e}")
    adf_client = None

# Global state
latest_triggered_run_id = None
unified_progress = {
    "SYNTHETIC": "Pending",
    "BRONZE": "Pending",
    "SILVER": "Pending",
    "AI_VALIDATION": "Pending",
    "GOLD": "Pending"
}

@app.route('/api/latest-run')
def get_latest_run():
    """Fetches the most recent pipeline run and its AI validation results"""
    global latest_triggered_run_id, unified_progress
    
    # GATING: If no journey has reached the ADF stage or manual AI stage, don't show historical junk
    if not latest_triggered_run_id and not unified_progress.get("ai_insights"):
        return jsonify({"status": "waiting", "message": "No active data journey in progress."})

    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching data journey details...")
        
        # If we have a triggered run, we only care about that one.
        # Otherwise, if we have manual insights, we might still want to show them.
        target_run_id = latest_triggered_run_id
        
        # 1. Get the specific run (if available)
        latest_run = None
        activity_details = []
        ai_thoughts = []

        if target_run_id:
            latest_run = adf_client.pipeline_runs.get(RESOURCE_GROUP, FACTORY_NAME, target_run_id)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Found session run: {latest_run.run_id} - Status: {latest_run.status}")
            
            # 2. Get activity runs for this pipeline
            activities = adf_client.activity_runs.query_by_pipeline_run(
                RESOURCE_GROUP,
                FACTORY_NAME,
                latest_run.run_id,
                {
                    "last_updated_after": (latest_run.run_start - timedelta(minutes=5)).isoformat(),
                    "last_updated_before": (datetime.now() + timedelta(minutes=5)).isoformat()
                }
            )
            
            for activity in sorted(activities.value, key=lambda x: x.activity_run_start if x.activity_run_start else datetime.min):
                activity_details.append({
                    "name": activity.activity_name,
                    "type": activity.activity_type,
                    "status": activity.status,
                    "duration": activity.duration_in_ms / 1000 if activity.duration_in_ms else 0
                })
                
                # Extract AI insights if it's the validation activity (from ADF)
                if "Validate" in activity.activity_name and activity.status == "Succeeded":
                    output = activity.output
                    if output and "validation_results" in output:
                        results = output["validation_results"]
                        for res in results:
                            if "pii_validation" in res:
                                pii = res["pii_validation"]
                                ai_thoughts.append({
                                    "id": f"adf-pii-{activity.activity_run_id}",
                                    "type": "warning" if pii.get("has_pii") else "success",
                                    "text": f"PII Analysis: {pii.get('classification', 'Clear')}"
                                })
                                if pii.get("pii_fields"):
                                    ai_thoughts.append({
                                        "id": f"adf-fields-{activity.activity_run_id}",
                                        "type": "process",
                                        "text": f"Flagged fields: {', '.join(pii['pii_fields'])}"
                                    })
                    
                    ai_thoughts.append({
                        "id": f"adf-complete-{activity.activity_run_id}",
                        "type": "success",
                        "text": f"Ollama Validation Complete (ai_powered: {output.get('ai_powered') if output else 'unknown'})"
                    })

        # OVERRIDE/ENHANCE with manual AI Validation results if they exist (Takes precedence)
        if unified_progress.get("ai_insights"):
            pii = unified_progress["ai_insights"]
            # Clear historical ADF thoughts if we have a fresh manual one
            ai_thoughts = []
            ai_thoughts.append({
                "id": "manual-pii-result",
                "type": "warning" if pii.get("has_pii") else "success",
                "text": f"PII Analysis: {pii.get('classification', 'Confidential')}"
            })
            if pii.get("pii_fields"):
                ai_thoughts.append({
                    "id": "manual-fields-result",
                    "type": "process",
                    "text": f"Flagged fields: {', '.join(pii['pii_fields'])}"
                })
            ai_thoughts.append({
                "id": "manual-complete-result",
                "type": "success",
                "text": "Ollama Validation Complete (Live Verification)"
            })

        # Calculate current status based on unified_progress if no active ADF run
        overall_status = "Succeeded"
        if latest_run:
            overall_status = latest_run.status
        elif unified_progress["AI_VALIDATION"] == "InProgress":
            overall_status = "InProgress"
        elif unified_progress["AI_VALIDATION"] == "Pending":
            overall_status = "Waiting"

        return jsonify({
            "run_id": latest_run.run_id if latest_run else None,
            "pipeline": latest_run.pipeline_name if latest_run else "Manual Validation",
            "status": overall_status,
            "activities": activity_details,
            "ai_thoughts": ai_thoughts,
            "unified_progress": unified_progress, # Pass this too to keep frontend in sync
            "lineage_metadata": {
                "source": "XRS-Nexus Real-time Flow",
                "compute": "Managed Azure IR",
                "storage_sink": "ADLS Gen2 Gold Layer"
            },
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/simulation')
def get_simulation():
    """Simulates a full end-to-end data flow with timestamps"""
    now = datetime.now()
    return jsonify({
        "status": "simulated",
        "current_step": 0, # Will be controlled by frontend
        "steps": [
            {
                "id": 0,
                "name": "Synthetic Data Generation",
                "status": "Succeeded",
                "details": "Generating 10,000 records of customer telemetry...",
                "logs": ["Initializing Faker...", "Generating PII fields...", "Dataset created: customer_telemetry_v1.csv"]
            },
            {
                "id": 1,
                "name": "ADLS Ingestion (Bronze)",
                "status": "Succeeded",
                "details": "Uploading to landingZone/bronze/customers...",
                "logs": ["Connecting to Storage Account...", "Uploading blob...", "Data landed in Bronze (Raw)"]
            },
            {
                "id": 2,
                "name": "ADF Transformation (Silver)",
                "status": "Succeeded",
                "details": "Converting CSV to Parquet and deduplicating...",
                "logs": ["ADF Pipeline Triggered", "Bronze -> Silver transformation started", "Parquet conversion complete"]
            },
            {
                "id": 3,
                "name": "AI Validation (Ollama)",
                "status": "InProgress",
                "details": "Running PHI-3 local inference for PII detection...",
                "logs": [
                    "Checking email fields...",
                    "PII Detected: customer_email (98% confidence)",
                    "Data classification: Restricted",
                    "Applying masking policy..."
                ]
            },
            {
                "id": 4,
                "name": "Gold Layer Integration",
                "status": "Pending",
                "details": "Moving validated & masked data to analytics-ready tables.",
                "logs": ["Waiting for AI clearance..."]
            }
        ],
        "timestamp": now.isoformat()
    })

import subprocess
import traceback

# State for manual actions and unified progress
action_status = {
    "is_running": False,
    "last_action": None,
    "logs": [],
    "error": None
}

unified_progress = {
    "SYNTHETIC": "Pending",
    "BRONZE": "Pending",
    "SILVER": "Pending",
    "AI_VALIDATION": "Pending",
    "GOLD": "Pending",
    "ai_insights": None
}

def run_script(command, action_name):
    global action_status, unified_progress, latest_triggered_run_id
    if action_status["is_running"]:
        return jsonify({"status": "busy", "message": "An action is already in progress"}), 409
    
    # RESET PROGRESS ENGINE ON NEW JOURNEY START
    if action_name == "Data Generation":
        unified_progress = {
            "SYNTHETIC": "InProgress",
            "BRONZE": "Pending",
            "SILVER": "Pending",
            "AI_VALIDATION": "Pending",
            "GOLD": "Pending",
            "ai_insights": None
        }
        latest_triggered_run_id = None
        action_status["logs"] = [] # Clear logs for fresh start
        print("--- SESSION RESET: Fresh Data Journey Started ---")
    
    action_status["is_running"] = True
    action_status["last_action"] = action_name
    action_status["logs"] = [f"🚀 Initializing {action_name}..."]
    action_status["error"] = None
    
    # Map action name to unified progress key
    progress_key = None
    if action_name == "Data Generation": progress_key = "SYNTHETIC"
    elif action_name == "ADLS Upload": progress_key = "BRONZE"
    elif action_name == "AI Validation": progress_key = "AI_VALIDATION"
    
    if progress_key:
        unified_progress[progress_key] = "InProgress"
    
    try:
        # Use PYTHONUNBUFFERED to ensure we get logs immediately
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        last_json_output = None
        for line in iter(process.stdout.readline, ''):
            clean_line = line.strip()
            if clean_line:
                # Add timestamp for the console
                ts = datetime.now().strftime('%H:%M:%S')
                log_entry = f"[{ts}] {clean_line}"
                print(f"[{action_name}] {clean_line}")
                action_status["logs"].append(log_entry)
                
                # Try to capture JSON output at the end
                if clean_line.startswith('{') and clean_line.endswith('}'):
                    try:
                        last_json_output = json.loads(clean_line)
                    except:
                        pass

                # Keep only last 100 logs to prevent memory issues
                if len(action_status["logs"]) > 100:
                    action_status["logs"].pop(0)
                
        process.wait()
        if process.returncode == 0:
            action_status["logs"].append(f"✅ {action_name} Completed Successfully.")
            if progress_key:
                unified_progress[progress_key] = "Succeeded"
                if last_json_output:
                    unified_progress["ai_insights"] = last_json_output.get("pii_validation")
                
                # SPECIAL CHAINING: AI Validation is done, but GOLD waits for manual approval.
                if action_name == "AI Validation":
                    print("AI Validation complete. Waiting for user approval to push to Gold.")
        else:
            action_status["error"] = f"Action failed with exit code {process.returncode}"
            action_status["logs"].append(f"❌ {action_name} Failed (Exit Code: {process.returncode})")
            if progress_key:
                unified_progress[progress_key] = "Failed"
            
    except Exception as e:
        action_status["error"] = str(e)
        action_status["logs"].append(f"🚨 ERROR: {str(e)}")
        if progress_key:
            unified_progress[progress_key] = "Failed"
    finally:
        action_status["is_running"] = False

@app.route('/api/pipeline/generate', methods=['POST'])
def trigger_generate():
    """Triggers the synthetic dataset generation script"""
    if action_status["is_running"]:
        return jsonify({"status": "busy", "message": "An action is already in progress"}), 409
    
    import threading
    thread = threading.Thread(target=run_script, args=(["python3", "synthetic-dataset/generate_adf_datasets.py"], "Data Generation"))
    thread.start()
    return jsonify({"status": "started", "action": "Data Generation"})

@app.route('/api/pipeline/upload', methods=['POST'])
def trigger_upload():
    """Triggers the ADLS upload script"""
    if action_status["is_running"]:
        return jsonify({"status": "busy", "message": "An action is already in progress"}), 409
    
    import threading
    thread = threading.Thread(target=run_script, args=(["python3", "scripts/upload_to_adls.py"], "ADLS Upload"))
    thread.start()
    return jsonify({"status": "started", "action": "ADLS Upload"})

@app.route('/api/pipeline/trigger', methods=['POST'])
def trigger_adf():
    """Triggers the ADF pipeline directly via Azure SDK"""
    global action_status, unified_progress, latest_triggered_run_id
    if action_status["is_running"]:
        return jsonify({"status": "busy", "message": "An action is already in progress"}), 409
    
    unified_progress["SILVER"] = "InProgress"
    action_status["is_running"] = True
    action_status["last_action"] = "ADF Pipeline Trigger"
    action_status["logs"] = ["--- Requesting ADF Pipeline Run ---"]
    
    try:
        pipeline_name = "ingest_with_ai_validation"
        print(f"Triggering ADF Pipeline: {pipeline_name}")
        run_response = adf_client.pipelines.create_run(RESOURCE_GROUP, FACTORY_NAME, pipeline_name)
        latest_triggered_run_id = run_response.run_id
        action_status["logs"].append(f"✓ Pipeline Triggered Successfully!")
        action_status["logs"].append(f"Run ID: {run_response.run_id}")
        return jsonify({"status": "success", "run_id": run_response.run_id})
    except Exception as e:
        action_status["error"] = str(e)
        action_status["logs"].append(f"❌ Failed to trigger pipeline: {str(e)}")
        unified_progress["SILVER"] = "Failed"
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        action_status["is_running"] = False

@app.route('/api/pipeline/validate', methods=['POST'])
def trigger_validate():
    """Triggers the actual AI validation script (Ollama/Azure)"""
    if action_status["is_running"]:
        return jsonify({"status": "busy", "message": "An action is already in progress"}), 409
    
    import threading
    thread = threading.Thread(target=run_script, args=(["python3", "api-layer/ai_validator.py"], "AI Validation"))
    thread.start()
    return jsonify({"status": "started", "action": "AI Validation"})

@app.route('/api/pipeline/approve', methods=['POST'])
def approve_gold_push():
    """Manually approves the data push to Gold layer"""
    global unified_progress
    
    if unified_progress["AI_VALIDATION"] != "Succeeded":
        return jsonify({"status": "error", "message": "Cannot push to Gold. AI Validation not complete."}), 400
        
    unified_progress["GOLD"] = "Succeeded"
    print("--- User Approved Data Push to Gold Layer ---")
    
    # Simulate file move -> REAL MOVEMENT
    action_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 👤 User Approved: Pushing validated data to Gold Storage...")
    
    try:
        from azure.storage.blob import BlobServiceClient
        import os
        import json
        
        # Azure Config
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container_name = "gold"
        
        if not connection_string:
            raise ValueError("Missing AZURE_STORAGE_CONNECTION_STRING in .env")
            
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        
        # Ensure container exists
        if not container_client.exists():
            container_client.create_container()

        # Retrieve MASKED DATA from AI output
        masked_data = unified_progress.get("ai_insights", {}).get("masked_data")
        
        if masked_data:
            # 1. Write masked data to a temporary file
            gold_file_name = "gold_customers.json"
            gold_file_path = f"data/gold/{gold_file_name}"
            
            # Ensure local gold dir exists
            os.makedirs("data/gold", exist_ok=True)
            
            with open(gold_file_path, "w") as f:
                json.dump(masked_data, f, indent=2)
                
            action_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 🔒 Generated {gold_file_name} with {len(masked_data)} masked records.")
            
            # 2. Upload MASKED file to Azure
            blob_name = f"analytics/ready/{gold_file_name}"
            with open(gold_file_path, "rb") as data:
                container_client.upload_blob(name=blob_name, data=data, overwrite=True)
            
            action_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] ☁️ Uploaded MASKED data to Azure gold/{blob_name}")
            action_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Data pushed to Azure container 'gold/analytics/ready'")
            
        else:
            action_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ No masked data found in AI insights. pushing nothing.")
            
    except Exception as e:
        print(f"Error moving files: {e}")
        action_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Azure upload failed: {e}")
    
    return jsonify({"status": "success", "action": "Gold Push"})

@app.route('/api/pipeline/status')
def get_action_status():
    """Returns the current status of manual actions and their logs"""
    global action_status, unified_progress, latest_triggered_run_id
    
    # Sync ADF status to unified progress ONLY if we have a triggered run in this session
    if latest_triggered_run_id:
        try:
            run = adf_client.pipeline_runs.get(RESOURCE_GROUP, FACTORY_NAME, latest_triggered_run_id)
            if run.status == "InProgress":
                unified_progress["SILVER"] = "InProgress"
                unified_progress["GOLD"] = "Pending"
            elif run.status == "Succeeded":
                unified_progress["SILVER"] = "Succeeded"
            elif run.status == "Failed":
                unified_progress["SILVER"] = "Failed"
                unified_progress["GOLD"] = "Failed"
        except:
            pass

    return jsonify({
        **action_status,
        "unified_progress": unified_progress
    })

if __name__ == '__main__':
    # Using 5001 to avoid common 5000 conflict with macOS AirPlay
    app.run(port=5001, debug=False)
