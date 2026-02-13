# How to Check AI Validation in Azure Portal

This guide shows you exactly where to find and verify the AI validation results in the Azure Portal.

---

## 🎯 Quick Navigation

1. [View Pipeline Runs](#step-1-navigate-to-adf-studio)
2. [Check AI Validation Activities](#step-2-view-pipeline-run-details)
3. [Inspect Validation Results](#step-3-check-validation-activity-output)
4. [Monitor Azure Function](#step-4-monitor-azure-function)
5. [View Application Insights](#step-5-application-insights-optional)

---

## Step 1: Navigate to ADF Studio

### Option A: Direct Link
Open your browser and go to:
```
https://adf.azure.com
```

### Option B: From Azure Portal
1. Go to [Azure Portal](https://portal.azure.com)
2. Search for **"Data factories"** in the top search bar
3. Click on **xrs-nexus-dev-adf-2yd1hw**
4. Click **"Launch Studio"** button

![Launch ADF Studio](https://docs.microsoft.com/en-us/azure/data-factory/media/quickstart-create-data-factory-portal/data-factory-home-page.png)

---

## Step 2: View Pipeline Run Details

### 2.1 Open Monitoring Tab

1. In ADF Studio, click the **Monitor** icon (📊) on the left sidebar
2. Click **"Pipeline runs"** (should be selected by default)
3. You'll see a list of recent pipeline runs

### 2.2 Find Your Pipeline Run

Look for:
- **Pipeline name**: `ingest_with_ai_validation`
- **Run ID**: `256776cc-08a8-11f1-a56e-920e0d931155`
- **Status**: ✅ Succeeded
- **Start time**: 2026-02-13 06:49:30
- **Duration**: ~68 seconds

**What to look for**:
```
Pipeline Name              Status      Start Time           Duration
─────────────────────────────────────────────────────────────────────
ingest_with_ai_validation  Succeeded   2026-02-13 06:49:30  68.5s
```

### 2.3 Open Run Details

Click on the **pipeline name** or the **Run ID** to open the detailed view.

---

## Step 3: Check Validation Activity Output

### 3.1 View Activity Runs

You should now see a **visual diagram** of your pipeline with 4 activities:

```
┌─────────────────────────┐
│ CopyCustomersToSilver   │ ✅ Succeeded (15.5s)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ ValidateCustomersData   │ ⚠️ Succeeded (4.5s)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ CopyOrdersToSilver      │ ✅ Succeeded (25.4s)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ ValidateOrdersData      │ ✅ Succeeded (3.9s)
└─────────────────────────┘
```

### 3.2 Inspect Validation Activity

**For ValidateCustomersData**:

1. Click on the **"ValidateCustomersData"** activity box
2. A panel will slide out from the right
3. Click the **"Output"** tab
4. You'll see the JSON response from the AI validation

**Expected Output**:
```json
{
  "status": "warning",
  "validation_results": [
    {
      "dataset": "silver/customers",
      "checks": [
        {
          "check_name": "null_value_check",
          "status": "passed",
          "details": {"null_percentage": 2.5},
          "recommendation": "No action needed"
        },
        {
          "check_name": "duplicate_check",
          "status": "passed",
          "details": {"duplicate_count": 0},
          "recommendation": "No action needed"
        },
        {
          "check_name": "pii_detection",
          "status": "warning",
          "details": {
            "pii_fields_detected": ["email", "phone"],
            "count": 2
          },
          "recommendation": "Apply data masking or encryption"
        }
      ]
    }
  ]
}
```

### 3.3 Key Things to Check

✅ **HTTP Status Code**: Should be `200`
```json
"ADFHttpStatusCodeInResponse": "200"
```

✅ **Validation Status**: Should be `"warning"` or `"passed"`
```json
"status": "warning"
```

⚠️ **PII Detection**: Should show detected fields
```json
"pii_fields_detected": ["email", "phone"]
```

✅ **Recommendations**: Should provide actionable advice
```json
"recommendation": "Apply data masking or encryption"
```

---

## Step 4: Monitor Azure Function

### 4.1 Navigate to Function App

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for **"Function App"** in the top search bar
3. Click on **xrs-nexus-ai-func-c53471**

### 4.2 View Function Invocations

1. In the left menu, click **"Functions"**
2. Click on **"validate-data"** function
3. Click **"Monitor"** in the left submenu
4. You'll see a list of recent invocations

**What to look for**:
- **Invocation Time**: Should match your pipeline run time (06:50:04 and 06:50:36)
- **Status**: Should be ✅ Success
- **Duration**: Should be ~1-2 seconds

### 4.3 View Invocation Details

Click on any invocation to see:
- **Request Body**: The validation request from ADF
- **Response**: The validation results
- **Logs**: Console output from the function
- **Execution Time**: How long it took

**Example Request**:
```json
{
  "datasets": ["customers"],
  "layer": "silver",
  "validation_rules": ["check_nulls", "check_duplicates", "check_pii"]
}
```

**Example Response**:
```json
{
  "status": "warning",
  "validation_results": [...]
}
```

---

## Step 5: Application Insights (Optional)

### 5.1 View Telemetry

1. In the Function App, click **"Application Insights"** in the left menu
2. Click **"View Application Insights data"**
3. Click **"Logs"** in the left menu

### 5.2 Query Validation Logs

Run this query to see all validation requests:

```kusto
traces
| where timestamp > ago(1h)
| where message contains "validate-data"
| project timestamp, message, severityLevel
| order by timestamp desc
```

### 5.3 Query Performance Metrics

See how long validations take:

```kusto
requests
| where timestamp > ago(1h)
| where name == "validate-data"
| summarize 
    count=count(),
    avg_duration=avg(duration),
    max_duration=max(duration)
| project count, avg_duration_ms=avg_duration, max_duration_ms=max_duration
```

---

## 🎯 Quick Verification Checklist

Use this checklist to verify everything is working:

### In ADF Studio (Monitor Tab)

- [ ] Pipeline run shows **Succeeded** status
- [ ] **4 activities** visible in the diagram
- [ ] **ValidateCustomersData** activity succeeded
- [ ] **ValidateOrdersData** activity succeeded
- [ ] Click on validation activity → **Output tab** shows JSON
- [ ] Output contains `"status": "warning"` or `"passed"`
- [ ] Output contains `"validation_results"` array
- [ ] Output contains `"pii_fields_detected"` for customers

### In Azure Function App

- [ ] Function App is **Running**
- [ ] **validate-data** function exists
- [ ] Function shows **2 invocations** around 06:50
- [ ] Both invocations show **Success** status
- [ ] Click invocation → see request/response details

### In Application Insights (Optional)

- [ ] Logs show validation requests
- [ ] No errors in the logs
- [ ] Average duration is 1-5 seconds

---

## 🔍 Troubleshooting

### Issue: Can't see validation output

**Solution**:
1. Make sure you clicked on the **WebActivity** (ValidateCustomersData), not the Copy activity
2. Click the **"Output"** tab, not "Input" or "Details"
3. If output is empty, check if the activity actually ran (should show duration)

### Issue: Validation activity failed

**Solution**:
1. Click on the failed activity
2. Click **"Error"** tab to see error message
3. Common issues:
   - Function App not running → Start the Function App
   - Authentication failed → Check managed identity permissions
   - Timeout → Increase timeout in pipeline definition

### Issue: Can't find Function App

**Solution**:
1. Go to Azure Portal → Resource Groups
2. Click **xrs-nexus-dev-rg**
3. Look for resource type **"Function App"**
4. Name should be **xrs-nexus-ai-func-c53471**

---

## 📸 Visual Guide Summary

### Where to Click in ADF Studio

```
ADF Studio Homepage
├── Monitor (📊 icon on left)
│   ├── Pipeline runs
│   │   └── Click: "ingest_with_ai_validation"
│   │       └── Click: "ValidateCustomersData" activity
│   │           └── Click: "Output" tab
│   │               └── See: AI validation JSON
```

### Where to Click in Azure Portal

```
Azure Portal
├── Search: "xrs-nexus-ai-func-c53471"
│   ├── Functions
│   │   └── validate-data
│   │       ├── Monitor → See invocations
│   │       └── Code + Test → Test manually
│   └── Application Insights
│       └── Logs → Query telemetry
```

---

## 🎓 What to Look For

### ✅ Good Signs

- Pipeline status: **Succeeded** (green checkmark)
- Validation activities: **Succeeded** (even if status is "warning")
- HTTP status: **200**
- Response contains: `"validation_results"` array
- PII detected: `["email", "phone"]` for customers
- Recommendations provided: `"Apply data masking..."`

### ⚠️ Warning Signs (Expected)

- Validation status: **"warning"** (this is correct for PII detection)
- PII fields detected (this is expected for customer data)

### ❌ Bad Signs

- Pipeline status: **Failed** (red X)
- HTTP status: **400**, **401**, **500**
- Error message in activity output
- No validation results in response
- Function invocations show failures

---

## 🚀 Next Steps

After verifying in the portal:

1. **Review PII Findings**: Decide how to handle email/phone fields
2. **Set Up Alerts**: Configure alerts for failed validations
3. **Create Dashboard**: Pin key metrics to Azure Dashboard
4. **Schedule Pipeline**: Add triggers for automated runs
5. **Extend Validation**: Add custom validation rules

---

## 📚 Related Resources

- [ADF Monitoring Documentation](https://docs.microsoft.com/en-us/azure/data-factory/monitor-visually)
- [Azure Functions Monitoring](https://docs.microsoft.com/en-us/azure/azure-functions/functions-monitoring)
- [Application Insights Queries](https://docs.microsoft.com/en-us/azure/azure-monitor/logs/get-started-queries)

---

**Need Help?**

If you can't find something or see unexpected results, check:
1. [AI Validation Report](file:///Users/ranitsinha/Documents/XRS-Nexus/AI_VALIDATION_REPORT.md) - Detailed analysis
2. [AI Orchestration Explained](file:///Users/ranitsinha/Documents/XRS-Nexus/AI_ORCHESTRATION_EXPLAINED.md) - How it works
3. [Walkthrough](file:///Users/ranitsinha/.gemini/antigravity/brain/2e618bc4-4cb3-4538-976b-c80bc0c991bd/walkthrough.md) - Complete guide

---

**Last Updated**: 2026-02-13 12:41:32 IST
