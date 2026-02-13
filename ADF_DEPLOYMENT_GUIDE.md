# ADF Pipeline Deployment Guide

## Quick Start

This guide provides step-by-step instructions to deploy and test the ADF-based data pipeline with AI orchestration and lineage tracking.

---

## Prerequisites

- Azure subscription with appropriate permissions
- Azure CLI installed and authenticated (`az login`)
- Terraform installed (v1.0+)
- Python 3.8+ with pip
- Git

---

## Step 1: Deploy Infrastructure

### 1.1 Navigate to Infrastructure Directory
```bash
cd /Users/ranitsinha/Documents/XRS-Nexus/infra
```

### 1.2 Review Terraform Plan
```bash
terraform plan -out=adf.tfplan
```

**Expected Output**: Plan shows creation of:
- 2 ADLS Gen2 containers (`synthetic-data`, `lineage`)
- 3 ADF linked services (bronze, silver, gold layers)
- 5 ADF datasets (customers, orders in CSV and Parquet formats)
- 1 Key Vault access policy for ADF

### 1.3 Apply Infrastructure
```bash
terraform apply adf.tfplan
```

**Duration**: ~3-5 minutes

### 1.4 Capture Outputs
```bash
export STORAGE_ACCOUNT=$(terraform output -raw storage_account_name)
export ADF_NAME=$(terraform output -raw adf_name)
export RESOURCE_GROUP=$(terraform output -raw resource_group_name)
export AZURE_SUBSCRIPTION_ID=$(az account show --query id -o tsv)

echo "Storage Account: $STORAGE_ACCOUNT"
echo "ADF Name: $ADF_NAME"
echo "Resource Group: $RESOURCE_GROUP"
```

---

## Step 2: Upload Synthetic Data

### 2.1 Set Environment Variables
```bash
export AZURE_STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT
```

### 2.2 Upload Data to ADLS Gen2
```bash
cd /Users/ranitsinha/Documents/XRS-Nexus
python3 scripts/upload_to_adls.py
```

**Expected Output**:
```
--- Starting Data Upload to ADLS Gen2 ---
Target Storage Account: xrsnexusdevstg2yd1hw
Uploading data/customers.csv to bronze/customers/customers.csv...
✅ Upload Success
...
🎉 Data Upload to ADLS Gen2 Complete! (12 files uploaded)
```

### 2.3 Verify Upload
```bash
az storage fs file list -f bronze --account-name $STORAGE_ACCOUNT --auth-mode login -o table
```

---

## Step 3: Deploy Azure Function (Optional)

### 3.1 Check if Function App Exists
```bash
FUNCTION_APP=$(az functionapp list -g $RESOURCE_GROUP --query "[0].name" -o tsv)
echo "Function App: $FUNCTION_APP"
```

### 3.2 Deploy Function Code
```bash
cd api-layer
pip3 install -r requirements.txt
func azure functionapp publish $FUNCTION_APP --python
```

### 3.3 Test Validation Endpoint
```bash
curl -X POST https://$FUNCTION_APP.azurewebsites.net/api/validate-data \
  -H "Content-Type: application/json" \
  -d '{
    "datasets": ["customers"],
    "layer": "silver",
    "validation_rules": ["check_nulls", "check_pii"]
  }'
```

**Expected Response**:
```json
{
  "status": "warning",
  "validation_results": [...]
}
```

---

## Step 4: Test ADF Pipeline

### 4.1 Set Environment Variables for Testing
```bash
export FACTORY_NAME=$ADF_NAME
```

### 4.2 Trigger Ingestion Pipeline
```bash
cd /Users/ranitsinha/Documents/XRS-Nexus
python3 scripts/test_adf_pipeline.py --pipeline ingest_synthetic_data --timeout 300
```

**Expected Output**:
```
🚀 Triggering pipeline: ingest_synthetic_data
✓ Pipeline triggered successfully
  Run ID: abc123-def456-...

⏳ Monitoring pipeline execution...
  [5.2s] Status: InProgress
  [45.8s] Status: Succeeded

✅ Pipeline succeeded
📊 Pipeline Execution Summary
Pipeline: ingest_synthetic_data
Run ID: abc123-def456-...
Status: Succeeded
Duration: 45.82s

Activities (4):
  ✓ CopyCustomersToSilver (Copy) - 12.34s
  ✓ CopyOrdersToSilver (Copy) - 15.67s
  ✓ AIDataQualityValidation (AzureFunctionActivity) - 8.91s
  ✓ LogValidationResults (SetVariable) - 0.12s
```

### 4.3 Verify Data in Silver Layer
```bash
az storage fs file list -f silver --account-name $STORAGE_ACCOUNT --auth-mode login -o table
```

---

## Step 5: Capture and Visualize Lineage

### 5.1 Capture Lineage from Pipeline Run
```bash
# Use the Run ID from Step 4.2
RUN_ID="<your-run-id-from-previous-step>"

python3 telemetry-lineage/adf_lineage_capture.py $RUN_ID
```

**Expected Output**:
```
📊 Capturing lineage for pipeline run: abc123-def456-...
✅ Lineage data stored: lineage/adf_runs/lineage_abc123_20260213_113045.json
✅ Lineage capture complete
```

### 5.2 Generate Visualization
```bash
LINEAGE_FILE=$(ls -t lineage/adf_runs/lineage_*.json | head -n 1)
python3 telemetry-lineage/visualize_lineage.py $LINEAGE_FILE
```

**Expected Output**:
```
✅ Generated lineage visualization: lineage/adf_runs/lineage_abc123_20260213_113045.html
🎉 Lineage visualization complete!
📂 Open in browser: file:///Users/ranitsinha/Documents/XRS-Nexus/lineage/adf_runs/lineage_abc123_20260213_113045.html
```

### 5.3 Open Visualization in Browser
```bash
open lineage/adf_runs/lineage_*.html
```

**What You'll See**:
- Interactive Mermaid flowchart showing data flow
- Metadata panel with pipeline details (name, run ID, status, duration)
- Color-coded nodes:
  - 🔵 Blue: Source datasets
  - 🟣 Purple: Sink datasets
  - 🟠 Orange: Copy activities
  - 🟢 Green: Transform activities

---

## Step 6: View Results in Azure Portal

### 6.1 Open ADF Studio
```bash
echo "https://adf.azure.com/en/authoring?factory=/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.DataFactory/factories/$ADF_NAME"
```

### 6.2 Navigate to Monitor Tab
- Click **Monitor** in left sidebar
- View **Pipeline runs**
- Click on your run to see activity details

### 6.3 Browse Data in Storage Explorer
```bash
echo "https://portal.azure.com/#@/resource/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT/storageexplorer"
```

Navigate to:
- `bronze/` - Raw CSV files
- `silver/` - Cleaned Parquet files
- `gold/` - Analytics-ready aggregated data
- `lineage/` - Lineage metadata JSON files

---

## Troubleshooting

### Issue: Terraform Apply Fails
**Solution**: Check for duplicate resources
```bash
cd infra
terraform validate
terraform fmt
```

### Issue: Data Upload Fails
**Solution**: Verify authentication and permissions
```bash
az login
az account show
az storage account show -n $STORAGE_ACCOUNT -g $RESOURCE_GROUP
```

### Issue: Pipeline Fails with "Dataset Not Found"
**Solution**: Ensure data was uploaded correctly
```bash
az storage fs file list -f bronze --account-name $STORAGE_ACCOUNT --auth-mode login
```

### Issue: AI Validation Endpoint Returns 404
**Solution**: Verify Function App deployment
```bash
az functionapp list -g $RESOURCE_GROUP -o table
az functionapp function list -g $RESOURCE_GROUP -n $FUNCTION_APP -o table
```

---

## Next Steps

1. **Add More Datasets**: Modify `generate_adf_datasets.py` to create additional datasets
2. **Customize Pipelines**: Edit ADF pipeline JSON files in `adf/pipelines/`
3. **Enhance AI Validation**: Update `ai-orchestration/adf_integration.py` with custom rules
4. **Schedule Pipelines**: Add triggers in ADF Studio for automated execution
5. **Monitor Costs**: Set up Azure Cost Management alerts

---

## Cost Estimation

| Resource | Estimated Monthly Cost |
|----------|----------------------|
| ADLS Gen2 Storage (10 GB) | $0.20 |
| ADF Pipeline Executions (100 runs) | $1.00 |
| Azure Function (Consumption) | $0.40 |
| Key Vault Operations | $0.03 |
| **Total** | **~$1.63/month** |

*Note: Costs may vary based on usage. This estimate assumes minimal testing workloads.*

---

## Support

For issues or questions:
1. Check the [walkthrough.md](file:///Users/ranitsinha/.gemini/antigravity/brain/2e618bc4-4cb3-4538-976b-c80bc0c991bd/walkthrough.md) for detailed implementation details
2. Review [implementation_plan.md](file:///Users/ranitsinha/.gemini/antigravity/brain/2e618bc4-4cb3-4538-976b-c80bc0c991bd/implementation_plan.md) for architecture overview
3. Consult Azure documentation for service-specific issues
