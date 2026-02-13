#!/bin/bash
# ==============================================================================
# ADF Pipeline Deployment Script
# Deploys complete ADF-based data pipeline with AI orchestration and lineage
# ==============================================================================

set -e  # Exit on error

echo "============================================================"
echo "🚀 ADF Pipeline Deployment"
echo "============================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Provision Infrastructure
echo -e "${BLUE}Step 1: Provisioning ADF Infrastructure${NC}"
echo "-----------------------------------------------------------"
cd infra
terraform init
terraform plan -out adf.tfplan
terraform apply adf.tfplan

# Get outputs
STORAGE_ACCOUNT=$(terraform output -raw storage_account_name 2>/dev/null || echo "")
ADF_NAME=$(terraform output -raw adf_name 2>/dev/null || echo "")
RESOURCE_GROUP=$(terraform output -raw resource_group_name 2>/dev/null || echo "")

if [ -z "$STORAGE_ACCOUNT" ]; then
    echo -e "${YELLOW}⚠️  Could not get storage account from Terraform, attempting to find it...${NC}"
    STORAGE_ACCOUNT=$(az storage account list --query "[?contains(name, 'stg')].name | [0]" -o tsv)
fi

if [ -z "$ADF_NAME" ]; then
    echo -e "${YELLOW}⚠️  Could not get ADF name from Terraform, attempting to find it...${NC}"
    ADF_NAME=$(az datafactory list -g "$RESOURCE_GROUP" --query "[0].name" -o tsv 2>/dev/null || echo "")
fi

echo -e "${GREEN}✓ Infrastructure provisioned${NC}"
echo "  Storage Account: $STORAGE_ACCOUNT"
echo "  ADF Name: $ADF_NAME"
echo "  Resource Group: $RESOURCE_GROUP"
echo ""

cd ..

# Step 2: Generate Synthetic Data
echo -e "${BLUE}Step 2: Generating Synthetic Datasets${NC}"
echo "-----------------------------------------------------------"
python3 synthetic-dataset/generate_adf_datasets.py
echo -e "${GREEN}✓ Synthetic data generated${NC}"
echo ""

# Step 3: Upload Data to ADLS Gen2
echo -e "${BLUE}Step 3: Uploading Data to ADLS Gen2${NC}"
echo "-----------------------------------------------------------"
export AZURE_STORAGE_ACCOUNT_NAME="$STORAGE_ACCOUNT"
python3 scripts/upload_to_adls.py
echo -e "${GREEN}✓ Data uploaded to bronze layer${NC}"
echo ""

# Step 4: Deploy Azure Function (if enabled)
echo -e "${BLUE}Step 4: Deploying Azure Function${NC}"
echo "-----------------------------------------------------------"
FUNCTION_APP=$(az functionapp list -g "$RESOURCE_GROUP" --query "[0].name" -o tsv 2>/dev/null || echo "")

if [ -n "$FUNCTION_APP" ]; then
    echo "  Function App: $FUNCTION_APP"
    cd api-layer
    
    # Install dependencies
    pip3 install -r requirements.txt -t .python_packages/lib/site-packages --quiet
    
    # Deploy function
    func azure functionapp publish "$FUNCTION_APP" --python
    
    echo -e "${GREEN}✓ Azure Function deployed${NC}"
    cd ..
else
    echo -e "${YELLOW}⚠️  No Function App found, skipping deployment${NC}"
fi
echo ""

# Step 5: Verify Deployment
echo -e "${BLUE}Step 5: Verifying Deployment${NC}"
echo "-----------------------------------------------------------"

# Check ADF pipelines
echo "Checking ADF pipelines..."
PIPELINE_COUNT=$(az datafactory pipeline list -g "$RESOURCE_GROUP" --factory-name "$ADF_NAME" --query "length(@)" -o tsv 2>/dev/null || echo "0")
echo "  Pipelines found: $PIPELINE_COUNT"

# Check ADLS containers
echo "Checking ADLS Gen2 containers..."
CONTAINER_COUNT=$(az storage fs list --account-name "$STORAGE_ACCOUNT" --auth-mode login --query "length(@)" -o tsv 2>/dev/null || echo "0")
echo "  Containers found: $CONTAINER_COUNT"

# Check uploaded files
echo "Checking uploaded datasets..."
FILE_COUNT=$(az storage fs file list -f bronze --account-name "$STORAGE_ACCOUNT" --auth-mode login --query "length(@)" -o tsv 2>/dev/null || echo "0")
echo "  Files in bronze layer: $FILE_COUNT"

echo ""
echo -e "${GREEN}✓ Deployment verification complete${NC}"
echo ""

# Step 6: Display Next Steps
echo "============================================================"
echo "✅ Deployment Complete!"
echo "============================================================"
echo ""
echo "Next Steps:"
echo "  1. Test ADF pipeline execution:"
echo "     python3 scripts/test_adf_pipeline.py --pipeline ingest_synthetic_data"
echo ""
echo "  2. View data in Azure Portal:"
echo "     https://portal.azure.com/#@/resource/subscriptions/.../resourceGroups/$RESOURCE_GROUP/providers/Microsoft.DataFactory/factories/$ADF_NAME"
echo ""
echo "  3. Capture and visualize lineage:"
echo "     python3 telemetry-lineage/adf_lineage_capture.py <run_id>"
echo "     python3 telemetry-lineage/visualize_lineage.py lineage/adf_runs/<lineage_file>.json"
echo ""
echo "  4. Test AI validation endpoint:"
echo "     curl -X POST https://$FUNCTION_APP.azurewebsites.net/api/validate-data \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"datasets\": [\"customers\"], \"layer\": \"silver\", \"validation_rules\": [\"check_nulls\"]}'"
echo ""
echo "============================================================"
