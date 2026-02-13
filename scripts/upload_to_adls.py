#!/usr/bin/env python3
"""
Enhanced Upload Script for ADLS Gen2
Uploads synthetic datasets to Azure Data Lake Storage for ADF pipeline demo
"""

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
        
        # 3. Upload to 'bronze' container with folder structure
        filesystem_name = "bronze"
        file_system_client = service_client.get_file_system_client(file_system=filesystem_name)
        
        # Original metadata files
        files_to_upload = [
            ("data/metadata_samples.json", "metadata/metadata_samples.json"),
            ("data/telemetry_logs.json", "metadata/telemetry_logs.json"),
        ]
        
        # New synthetic datasets for ADF pipeline
        datasets = ["customers", "orders", "products", "transactions", "events"]
        for dataset in datasets:
            files_to_upload.append((f"data/{dataset}.csv", f"{dataset}/{dataset}.csv"))
            files_to_upload.append((f"data/{dataset}.json", f"{dataset}/{dataset}.json"))
        
        # Add summary file
        files_to_upload.append(("data/dataset_summary.json", "metadata/dataset_summary.json"))
        
        upload_count = 0
        for local_path, remote_path in files_to_upload:
            if os.path.exists(local_path):
                print(f"Uploading {local_path} to {filesystem_name}/{remote_path}...")
                
                # Create directory path if needed
                directory_path = os.path.dirname(remote_path)
                if directory_path:
                    directory_client = file_system_client.get_directory_client(directory_path)
                    file_client = directory_client.get_file_client(os.path.basename(remote_path))
                else:
                    file_client = file_system_client.get_file_client(remote_path)
                
                with open(local_path, "rb") as data:
                    file_client.upload_data(data, overwrite=True)
                print("✅ Upload Success")
                upload_count += 1
            else:
                print(f"⚠️ File not found: {local_path}")
                
        print(f"\n🎉 Data Upload to ADLS Gen2 Complete! ({upload_count} files uploaded)")
        
    except Exception as e:
        print(f"❌ Upload Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    upload_to_adls()
