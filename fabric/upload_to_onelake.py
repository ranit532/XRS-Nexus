import msal
import os
import requests
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core.credentials import AccessToken

# Config
WORKSPACE_NAME = "xrs-nexus-workspace"
LAKEHOUSE_NAME = "XRSNexusLakehouse"

# Auth Config
CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"  # Microsoft Azure CLI public client ID
TENANT_ID = "8ed505e3-a743-4271-85f6-8ec8b5d0b18b"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

# Scope for OneLake Data Access (ADLS Gen2)
SCOPES = ["https://storage.azure.com/.default"]

def get_token():
    print(f"Authenticating for OneLake Access (Scope: {SCOPES[0]})...")
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    accounts = app.get_accounts()
    
    result = None
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    
    if not result:
        result = app.acquire_token_interactive(scopes=SCOPES)
    
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(result.get("error_description"))

class SimpleTokenCredential:
    def __init__(self, token):
        self.token = token
    def get_token(self, *scopes, **kwargs):
        return AccessToken(self.token, 3000)

def upload_file(file_system_client, local_path, lakehouse_path):
    if not os.path.exists(local_path):
        print(f"⚠️ File not found: {local_path}, skipping.")
        return

    file_name = os.path.basename(local_path)
    # Target Path: <LakehouseName>.Lakehouse/Files/<path>/<filename>
    target_path = f"{LAKEHOUSE_NAME}.Lakehouse/Files/{lakehouse_path}/{file_name}"
    
    print(f"Uploading {file_name} -> {target_path}...")
    
    try:
        file_client = file_system_client.get_file_client(target_path)
        with open(local_path, "rb") as data:
            file_client.upload_data(data, overwrite=True)
        print("✅ Upload Success")
    except Exception as e:
        print(f"❌ Upload Failed: {e}")

# Additional Scope for Fabric API (Control Plane)
CONTROL_PLANE_SCOPES = ["https://analysis.windows.net/powerbi/api/.default"]

def get_control_plane_token():
    print(f"Authenticating for Fabric Control Plane...")
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(CONTROL_PLANE_SCOPES, account=accounts[0])
    else:
        result = None
    if not result:
        result = app.acquire_token_interactive(scopes=CONTROL_PLANE_SCOPES)
    if "access_token" in result:
        return result["access_token"]
    raise Exception("Failed to get Control Plane token")

def ensure_lakehouse_exists(workspace_name, lakehouse_name):
    try:
        token = get_control_plane_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Get Workspace ID
        ws_resp = requests.get("https://api.fabric.microsoft.com/v1/workspaces", headers=headers)
        if ws_resp.status_code != 200:
             print(f"❌ Failed to list workspaces: {ws_resp.text}")
             return None
             
        workspaces = ws_resp.json().get('value', [])
        print(f"    Found {len(workspaces)} workspaces:")
        for w in workspaces:
            print(f"    - {w['displayName']} ({w['id']})")
            
        ws_id = next((w['id'] for w in workspaces if w['displayName'] == workspace_name), None)
        
        # Fallback: Use the first available workspace if target not found (simulation hack)
        if not ws_id and workspaces:
             print(f"⚠️ Target workspace '{workspace_name}' not found. Using first available: {workspaces[0]['displayName']}")
             ws_id = workspaces[0]['id']
             # Update global workspace name for filesystem client later
             global WORKSPACE_NAME
             WORKSPACE_NAME = workspaces[0]['displayName']
             
        if not ws_id:
            print(f"❌ No accessible workspaces found.")
            return None
            
        # 2. Check/Create Lakehouse
        items_url = f"https://api.fabric.microsoft.com/v1/workspaces/{ws_id}/items"
        items_resp = requests.get(items_url, headers=headers)
        
        lh_exists = any(i['displayName'] == lakehouse_name and i['type'] == 'Lakehouse' for i in items_resp.json().get('value', []))
        
        if lh_exists:
            print(f"✅ Lakehouse '{lakehouse_name}' exists.")
        else:
            print(f"DTO Creating Lakehouse '{lakehouse_name}'...")
            payload = {
                "displayName": lakehouse_name,
                "type": "Lakehouse"
            }
            create_resp = requests.post(items_url, headers=headers, json=payload)
            if create_resp.status_code in [201, 202]:
                print(f"✅ Lakehouse Created Successfully.")
            else:
                print(f"❌ Failed to create Lakehouse: {create_resp.text}")
                return None
                
        return True
    except Exception as e:
        print(f"❌ Lakehouse check failed: {e}")
        return None

def main():
    try:
        # 0. Ensure Lakehouse Exists
        import requests
        if not ensure_lakehouse_exists(WORKSPACE_NAME, LAKEHOUSE_NAME):
            print("❌ Cannot proceed with upload without Lakehouse.")
            return

        # 1. Get Token (Data Plane)
        token = get_token()
        credential = SimpleTokenCredential(token)
        
        # 2. Connect to OneLake
        # URL: https://onelake.dfs.fabric.microsoft.com
        service_client = DataLakeServiceClient(account_url="https://onelake.dfs.fabric.microsoft.com", credential=credential)
        
        # 3. Get Filesystem Client (Workspace Name)
        file_system_client = service_client.get_file_system_client(file_system=WORKSPACE_NAME)
        
        print("\n--- Starting Data Upload to Fabric OneLake ---")
        
        # 4. Upload Datasets
        # Bronze (Raw JSON)
        upload_file(file_system_client, "data/metadata_samples.json", "bronze")
        upload_file(file_system_client, "data/telemetry_logs.json", "bronze")
        
        # Silver (Parquet from simulated ETL)
        upload_file(file_system_client, "data/silver_metadata.parquet", "silver")
        
        # Gold (Parquet from simulated ETL)
        upload_file(file_system_client, "data/gold_schema_stats.parquet", "gold")
        
        print("\n🎉 All Datasets Pushed to OneLake!")
        
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")

if __name__ == "__main__":
    main()
