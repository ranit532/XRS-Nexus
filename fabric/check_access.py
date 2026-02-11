import requests
import msal

CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"  # Microsoft Azure CLI public client ID
TENANT_ID = "8ed505e3-a743-4271-85f6-8ec8b5d0b18b"

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://analysis.windows.net/powerbi/api/.default"]

def get_token():
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)

    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    else:
        result = None

    if not result:
        result = app.acquire_token_interactive(scopes=SCOPES)

    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(result.get("error_description"))

def check_fabric_access():
    print("Checking Fabric API Access...")
    try:
        token = get_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        url = "https://api.fabric.microsoft.com/v1/workspaces"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print("✅ Successfully authenticated with Fabric API!")
            workspaces = response.json().get('value', [])
            print(f"Workspaces found ({len(workspaces)}):")
            for ws in workspaces:
                print(f" - {ws['displayName']} (ID: {ws['id']})")

        elif response.status_code == 403:
            print("⚠️ Fabric not enabled. Activate trial at https://app.fabric.microsoft.com")

        else:
            print(response.status_code, response.text)

    except Exception as e:
        print("❌ Failed:", e)

if __name__ == "__main__":
    check_fabric_access()
