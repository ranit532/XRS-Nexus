#!/bin/bash
# Generate Databricks access token and update ADF linked service

echo "=== Databricks Access Token Setup ==="
echo ""
echo "IMPORTANT: You need to create a Databricks Personal Access Token manually."
echo ""
echo "Steps:"
echo "1. Go to Databricks workspace: https://adb-7405606665021845.5.azuredatabricks.net"
echo "2. Click on your username (top right) → Settings"
echo "3. Go to 'Developer' → 'Access tokens'"
echo "4. Click 'Generate new token'"
echo "5. Set comment: 'ADF Integration'"
echo "6. Set lifetime: 90 days"
echo "7. Click 'Generate'"
echo "8. Copy the token (you won't see it again!)"
echo ""
echo "Then run:"
echo "  az datafactory linked-service create \\"
echo "    --factory-name xrs-nexus-dev-adf-2yd1hw \\"
echo "    --resource-group xrs-nexus-dev-rg \\"
echo "    --name LS_Databricks \\"
echo "    --properties @databricks_linked_service.json"
echo ""
echo "Where databricks_linked_service.json contains:"
cat << 'EOF'
{
  "type": "AzureDatabricks",
  "typeProperties": {
    "domain": "https://adb-7405606665021845.5.azuredatabricks.net",
    "accessToken": {
      "type": "SecureString",
      "value": "YOUR_TOKEN_HERE"
    },
    "newClusterNodeType": "Standard_DS3_v2",
    "newClusterNumOfWorker": "1",
    "newClusterVersion": "13.3.x-scala2.12"
  }
}
EOF
