from azure.identity import DefaultAzureCredential
import requests

def check_fabric_access():
    print("Checking Fabric API Access...")
    try:
        cred = DefaultAzureCredential()
        token = cred.get_token("https://api.fabric.microsoft.com/.default")
        headers = {"Authorization": f"Bearer {token.token}"}
        
        url = "https://api.fabric.microsoft.com/v1/workspaces"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Successfully authenticated with Fabric API!")
            print(f"    Workspaces found: {len(response.json().get('value', []))}")
        elif response.status_code == 401:
            print("❌ Authentication Failed (401). Please re-login using 'az login'.")
        elif response.status_code == 403:
            print("⚠️ Access Denied (403). Only Fabric enabled users can access this API.")
            print("   Action: Go to https://app.fabric.microsoft.com and start a Free Trial.")
        else:
            print(f"❌ Unexpected Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Failed to connect: {e}")

if __name__ == "__main__":
    check_fabric_access()
