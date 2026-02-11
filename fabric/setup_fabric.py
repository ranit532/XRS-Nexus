import os
import requests
import json
from azure.identity import DefaultAzureCredential

# Config
WORKSPACE_NAME = "xrs-nexus-workspace"
LAKEHOUSE_NAME = "XRSNexusLakehouse"
CAPACITY_ID = "" # Optional: Set if you have a specific F2/Trial capacity ID to assign

# API Endpoints
FABRIC_API_BASE = "https://api.fabric.microsoft.com/v1"

def get_token():
    credential = DefaultAzureCredential()
    token = credential.get_token("https://api.fabric.microsoft.com/.default")
    return token.token

def create_workspace(headers):
    print(f"Creating Workspace: {WORKSPACE_NAME}...")
    url = f"{FABRIC_API_BASE}/workspaces"
    payload = {"displayName": WORKSPACE_NAME}
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        ws_id = response.json()['id']
        print(f"✅ Workspace Created: {ws_id}")
        return ws_id
    elif response.status_code == 400:
        print("⚠️ Workspace might already exist or invalid name.")
        # Try to find existing
        return get_workspace_id(headers)
    else:
        print(f"❌ Failed to create workspace: {response.text}")
        return None

def get_workspace_id(headers):
    # List workspaces and find by name
    url = f"{FABRIC_API_BASE}/workspaces"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        workspaces = response.json().get('value', [])
        for ws in workspaces:
            if ws['displayName'] == WORKSPACE_NAME:
                print(f"ℹ️ Found existing workspace: {ws['id']}")
                return ws['id']
    return None

def create_lakehouse(headers, workspace_id):
    print(f"Creating Lakehouse: {LAKEHOUSE_NAME}...")
    url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items"
    payload = {
        "displayName": LAKEHOUSE_NAME,
        "type": "Lakehouse"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        lh_id = response.json()['id']
        print(f"✅ Lakehouse Created: {lh_id}")
        return lh_id
    else:
        print(f"❌ Failed to create lakehouse: {response.text}")
        return None

def upload_file_to_onelake(credential, workspace_id, lakehouse_id, local_path, destination_path):
    # Use azure-storage-file-datalake for upload
    from azure.storage.filedatalake import DataLakeServiceClient
    
    print(f"Uploading {local_path} to OneLake...")
    
    # OneLake Endpoint
    account_url = "https://onelake.dfs.fabric.microsoft.com"
    
    # Filesystem name is the Workspace ID (sometimes Name, but ID is safer for API) - Actually OneLake uses Workspace Name in URI usually but let's try.
    # The standard is: https://onelake.dfs.fabric.microsoft.com/<workspace>/<item>.<type>/<path>
    # We can perform purely via REST or SDK.
    
    # Let's try constructing the full URL for the file
    # Note: Workspace name in URL might need escaping if it has spaces
    
    # To use SDK, we treat it as ADLS Gen2
    # FileSystem = Workspace Name
    # Directory = <LakehouseName>.Lakehouse/Files/<path>
    
    try:
        service_client = DataLakeServiceClient(account_url=account_url, credential=credential)
        file_system_client = service_client.get_file_system_client(file_system=WORKSPACE_NAME)
        
        # Ensure filesystem exists (it should via Fabric)
        # Directory path
        target_dir = f"{LAKEHOUSE_NAME}.Lakehouse/Files/{destination_path}"
        directory_client = file_system_client.get_directory_client(target_dir)
        
        if not directory_client.exists():
            directory_client.create_directory()
            
        file_name = os.path.basename(local_path)
        file_client = directory_client.get_file_client(file_name)
        
        with open(local_path, "rb") as data:
            file_client.upload_data(data, overwrite=True)
            
        print(f"✅ Uploaded {file_name}")
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")


if __name__ == "__main__":
    print("--- Starting Fabric Setup ---")
    
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Create/Get Workspace
        ws_id = create_workspace(headers)
        if not ws_id:
            exit(1)
            
        # 2. Create Lakehouse
        lh_id = create_lakehouse(headers, ws_id)
        
        # 3. Upload Data
        credential = DefaultAzureCredential()
        
        # Upload Metadata
        upload_file_to_onelake(credential, ws_id, lh_id, "data/metadata_samples.json", "metadata")
        
        # Upload Telemetry
        upload_file_to_onelake(credential, ws_id, lh_id, "data/telemetry_logs.json", "telemetry")
        
        print("\n🎉 Fabric Setup Complete!")
        
    except Exception as e:
        print(f"❌ Script failed: {e}")
