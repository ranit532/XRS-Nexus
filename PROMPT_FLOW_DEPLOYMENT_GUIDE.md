# Deploy GPT Model and Prompt Flow - Step by Step Guide

## 🎯 What We've Created

✅ **Prompt Flow Created**: `ai-orchestration/flows/adf_data_validation`  
✅ **Components**:
- `flow.dag.yaml` - Flow definition
- `pii_validation.jinja2` - Intelligent PII detection prompt
- `quality_validation.jinja2` - Data quality validation prompt
- `aggregate.py` - Results aggregation logic

---

## 📋 Step 1: Deploy GPT Model in Azure AI Studio

**Time**: 5 minutes

### Instructions

1. **Open Azure AI Studio**  
   Go to: https://ai.azure.com

2. **Navigate to Deployments**
   - Click "Deployments" in the left menu
   - Or go directly to your OpenAI resource

3. **Create New Deployment**
   - Click "+ Create deployment" or "+ Deploy model"
   - Select model: **gpt-4o** (recommended) or **gpt-4o-mini** (cheaper)
   - Deployment name: **`gpt-4o`** (must match the name in flow.dag.yaml)
   - Tokens per minute: **10K** (or whatever your quota allows)
   - Click "Deploy"

4. **Wait for Deployment**
   - Should take 1-2 minutes
   - Status will change to "Succeeded"

5. **Verify Deployment**
   ```bash
   az cognitiveservices account deployment list \
     -g xrs-nexus-dev-rg \
     -n xrs-nexus-dev-openai \
     -o table
   ```

**Expected Output**:
```
Name      Model    Status
--------  -------  ---------
gpt-4o    gpt-4o   Succeeded
```

---

## 📋 Step 2: Test Prompt Flow Locally (Optional)

**Time**: 2 minutes

### Install Prompt Flow SDK

```bash
pip install promptflow promptflow-tools
```

### Test the Flow

```bash
cd ai-orchestration/flows/adf_data_validation

# Test with sample data
pf flow test \
  --flow . \
  --inputs dataset_sample='[{"email":"test@example.com","age":25}]' \
          field_names='["email","age"]' \
          validation_type="comprehensive"
```

**Expected Output**: JSON with PII detection and quality validation results

---

## 📋 Step 3: Deploy Prompt Flow to Azure

**Time**: 5 minutes

### Option A: Deploy via CLI (Recommended)

```bash
# Navigate to project root
cd /Users/ranitsinha/Documents/XRS-Nexus

# Deploy the flow
pf flow deploy \
  --flow ai-orchestration/flows/adf_data_validation \
  --name adf-data-validator \
  --workspace xrs-nexus-dev-ai-project \
  --resource-group xrs-nexus-dev-rg
```

### Option B: Deploy via Azure AI Studio

1. Go to https://ai.azure.com
2. Navigate to "Flows"
3. Click "Upload" or "Create"
4. Select folder: `ai-orchestration/flows/adf_data_validation`
5. Click "Deploy"
6. Deployment name: `adf-data-validator`
7. Click "Deploy"

---

## 📋 Step 4: Get Endpoint URL

After deployment, get the endpoint URL:

```bash
# Get endpoint details
az ml online-endpoint show \
  --name adf-data-validator \
  --workspace-name xrs-nexus-dev-ai-project \
  -g xrs-nexus-dev-rg \
  --query "{url:scoring_uri, auth:auth_mode}" \
  -o json
```

**Save this URL** - you'll need it for the Azure Function!

---

## 📋 Step 5: Update Azure Function

Update the Azure Function to call the Prompt Flow endpoint.

### Update `api-layer/ai_validator.py`

```python
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import json
import os
import requests

class PromptFlowValidator:
    """Validates data using Prompt Flow + GPT-4o"""
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.ml_client = MLClient(
            credential=self.credential,
            subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
            resource_group_name="xrs-nexus-dev-rg",
            workspace_name="xrs-nexus-dev-ai-project"
        )
        self.endpoint_name = "adf-data-validator"
    
    def validate(self, dataset_sample: list, field_names: list, validation_type: str = "comprehensive"):
        """Call Prompt Flow for AI validation"""
        
        # Get endpoint URL
        endpoint = self.ml_client.online_endpoints.get(self.endpoint_name)
        scoring_uri = endpoint.scoring_uri
        
        # Get auth token
        token = self.credential.get_token("https://ml.azure.com/.default").token
        
        # Prepare request
        request_data = {
            "dataset_sample": json.dumps(dataset_sample[:10]),
            "field_names": json.dumps(field_names),
            "validation_type": validation_type
        }
        
        # Call endpoint
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.post(scoring_uri, json=request_data, headers=headers)
        response.raise_for_status()
        
        return response.json()
```

### Update `api-layer/function_app.py`

```python
from ai_validator import PromptFlowValidator

@app.route(route="validate-data", methods=["POST"])
def validate_data(req: func.HttpRequest) -> func.HttpResponse:
    """AI-powered data quality validation using Prompt Flow"""
    
    try:
        req_body = req.get_json()
        datasets = req_body.get("datasets", [])
        layer = req_body.get("layer", "silver")
        
        # Initialize AI validator
        ai_validator = PromptFlowValidator()
        
        validation_results = []
        for dataset in datasets:
            # Get sample data from ADLS
            sample_data = get_data_sample(layer, dataset)
            
            if not sample_data:
                continue
            
            # Call Prompt Flow for AI validation
            ai_result = ai_validator.validate(
                dataset_sample=sample_data,
                field_names=list(sample_data[0].keys()),
                validation_type="comprehensive"
            )
            
            validation_results.append({
                "dataset": f"{layer}/{dataset}",
                "ai_validation": json.loads(ai_result),
                "timestamp": datetime.now().isoformat()
            })
        
        # Determine overall status
        overall_status = "passed"
        for result in validation_results:
            status = result["ai_validation"].get("status", "passed")
            if status == "failed":
                overall_status = "failed"
                break
            elif status == "warning":
                overall_status = "warning"
        
        return func.HttpResponse(
            json.dumps({
                "status": overall_status,
                "validation_results": validation_results,
                "ai_powered": True,
                "model": "gpt-4o"
            }),
            mimetype="application/json"
        )
    
    except Exception as e:
        logging.error(f"Validation error: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500
        )
```

---

## 📋 Step 6: Deploy Updated Function

```bash
cd api-layer

# Add new dependency
echo "azure-ai-ml>=1.12.0" >> requirements.txt

# Deploy
zip -r function.zip . -x "*.pyc" -x "__pycache__/*" -x ".venv/*"
az functionapp deployment source config-zip \
  -g xrs-nexus-dev-rg \
  -n xrs-nexus-ai-func-c53471 \
  --src function.zip
rm function.zip
```

---

## 📋 Step 7: Test End-to-End

### Test Azure Function

```bash
curl -X POST https://xrs-nexus-ai-func-c53471.azurewebsites.net/api/validate-data \
  -H "Content-Type: application/json" \
  -d '{
    "datasets": ["customers"],
    "layer": "silver",
    "validation_rules": ["check_pii", "check_quality"]
  }'
```

### Test ADF Pipeline

```bash
az datafactory pipeline create-run \
  -g xrs-nexus-dev-rg \
  --factory-name xrs-nexus-dev-adf-2yd1hw \
  --name ingest_with_ai_validation
```

---

## ✅ Success Criteria

- [ ] GPT-4o model deployed in Azure OpenAI
- [ ] Prompt Flow deployed as endpoint
- [ ] Endpoint returns validation results
- [ ] Azure Function calls Prompt Flow
- [ ] ADF pipeline executes with AI validation
- [ ] AI detects PII intelligently (not just keywords)
- [ ] AI identifies unrealistic values
- [ ] Response time < 10 seconds

---

## 🎯 What to Do Next

**Right now**: Deploy the GPT-4o model in Azure AI Studio (Step 1)

**Then let me know** and I'll help you with the remaining steps!

---

## 📊 Expected Results

### Before (Rule-Based):
```json
{
  "pii_fields_detected": ["email"],  // Only keyword matching
  "status": "warning"
}
```

### After (AI-Powered):
```json
{
  "pii_validation": {
    "has_pii": true,
    "pii_fields": [{
      "field": "user_contact",  // Detected without "email" keyword!
      "type": "email_address",
      "confidence": 0.95,
      "reasoning": "Contains email addresses based on value format"
    }]
  },
  "quality_validation": {
    "issues": [{
      "field": "age",
      "issue_type": "unrealistic_value",
      "description": "Age 250 is unrealistic for a human"
    }]
  },
  "status": "warning"
}
```

---

**Ready to proceed?** Deploy the GPT model (Step 1) and let me know!
