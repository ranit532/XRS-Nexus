import os
import sys
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient

def upload_to_adls():
    try:
        print("--- Starting Data Upload to ADLS Gen2 ---")
        
        # 1. Authenticate
        credential = DefaultAzureCredential()
        
        # 2. Get Storage Account Name from Env or Hardcode (from Terraform output)
        # We'll try to find it dynamically or expect it passed as kwarg/env
        account_name = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
        if not account_name:
             # Fallback lookup via CLI (for convenience in this script)
             print("Fetching storage account name from Azure CLI...")
             import subprocess
             result = subprocess.run(
                 ["az", "storage", "account", "list", "--query", "[?contains(name, 'stg')].name | [0]", "-o", "tsv"],
                 capture_output=True, text=True
             )
             account_name = result.stdout.strip()
        
        if not account_name:
            print("❌ Could not determine Storage Account Name.")
            return

        print(f"Target Storage Account: {account_name}")
        account_url = f"https://{account_name}.dfs.core.windows.net"
        
        service_client = DataLakeServiceClient(account_url=account_url, credential=credential)
        
        # 3. Upload to 'bronze' container
        filesystem_name = "bronze"
        file_system_client = service_client.get_file_system_client(file_system=filesystem_name)
        
        files_to_upload = [
            "data/metadata_samples.json",
            "data/telemetry_logs.json"
        ]
        
        for local_path in files_to_upload:
            if os.path.exists(local_path):
                file_name = os.path.basename(local_path)
                print(f"Uploading {file_name} to {filesystem_name}...")
                file_client = file_system_client.get_file_client(file_name)
                
                with open(local_path, "rb") as data:
                    file_client.upload_data(data, overwrite=True)
                print("✅ Upload Success")
            else:
                print(f"⚠️ File not found: {local_path}")
                
        print("\n🎉 Data Upload to ADLS Gen2 Complete!")
        
    except Exception as e:
        print(f"❌ Upload Failed: {e}")

if __name__ == "__main__":
    upload_to_adls()
