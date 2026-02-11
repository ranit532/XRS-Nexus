# Real-Time Pipeline Monitoring Guide

## 🔍 Where to Monitor Your Pipeline

### Option 1: Azure Data Factory Studio (RECOMMENDED)
**Direct URL**: https://adf.azure.com/en-us/monitoring/pipelineruns?factory=/subscriptions/ddfba1ba-a22b-4bb4-b981-033e62bde697/resourceGroups/xrs-nexus-dev-rg/providers/Microsoft.DataFactory/factories/xrs-nexus-dev-adf-2yd1hw

**Steps:**
1. Click the link above (opens ADF Studio)
2. You'll see all pipeline runs with real-time status
3. Click on your run ID: `9ad02a1a-073d-11f1-8c45-920e0d931154`
4. View detailed activity progress, including:
   - Databricks cluster creation status
   - Notebook execution logs
   - Error messages (if any)

### Option 2: Databricks Workspace
**Direct URL**: https://adb-7405606665021845.5.azuredatabricks.net

**Steps:**
1. Go to Databricks workspace
2. Click **Compute** (left sidebar)
3. Look for a cluster starting with `job-` (auto-created by ADF)
4. Click on the cluster to see:
   - Cluster creation progress
   - Spark UI
   - Driver/executor logs

### Option 3: Azure Portal
1. Go to: https://portal.azure.com
2. Search for: `xrs-nexus-dev-adf-2yd1hw`
3. Click **Monitor** → **Pipeline runs**
4. Find your run and click for details

---

## 🐛 Troubleshooting Long-Running Pipeline

### Check Current Status
```bash
# Get detailed pipeline info
az datafactory pipeline-run show \
  --factory-name xrs-nexus-dev-adf-2yd1hw \
  --resource-group xrs-nexus-dev-rg \
  --run-id 9ad02a1a-073d-11f1-8c45-920e0d931154
```

### Check Activity Details
```bash
# See what activities are running
az datafactory activity-run query-by-pipeline-run \
  --factory-name xrs-nexus-dev-adf-2yd1hw \
  --resource-group xrs-nexus-dev-rg \
  --run-id 9ad02a1a-073d-11f1-8c45-920e0d931154 \
  --last-updated-after "2026-02-11T11:00:00Z" \
  --last-updated-before "2026-02-11T13:00:00Z"
```

### Common Reasons for Delays

1. **Databricks Cluster Creation** (5-7 minutes)
   - First-time cluster creation
   - Installing libraries
   - Initializing Spark

2. **Notebook Execution** (2-5 minutes per notebook)
   - Reading data from ADLS Gen2
   - Spark transformations
   - Writing output

3. **Quota/Capacity Issues**
   - Azure region capacity limits
   - Databricks workspace limits

---

## ⚡ Quick Actions

### Cancel the Current Run
```bash
# If it's taking too long, cancel and retry
az datafactory pipeline-run cancel \
  --factory-name xrs-nexus-dev-adf-2yd1hw \
  --resource-group xrs-nexus-dev-rg \
  --run-id 9ad02a1a-073d-11f1-8c45-920e0d931154
```

### Use Existing Cluster (Faster)
Instead of creating a new cluster each time, you can:
1. Create a persistent cluster in Databricks
2. Update the linked service to use `existingClusterId` instead of `newCluster*` parameters

---

## 📊 Expected Timeline

| Phase | Duration | What's Happening |
|-------|----------|------------------|
| Queued | 0-30s | Waiting for resources |
| Cluster Creation | 5-7 min | Databricks provisioning VMs |
| Notebook 1 (Bronze→Silver) | 1-3 min | Data transformation |
| Notebook 2 (Silver→Gold) | 1-2 min | Aggregation |
| **Total** | **7-12 min** | First run (cluster creation) |
| **Subsequent Runs** | **2-5 min** | If cluster is reused |

---

## 🔗 Quick Links

- **ADF Studio**: https://adf.azure.com
- **Databricks**: https://adb-7405606665021845.5.azuredatabricks.net
- **Azure Portal**: https://portal.azure.com
- **Storage Explorer**: https://portal.azure.com/#view/Microsoft_Azure_Storage/ContainerMenuBlade/~/overview/storageAccountId/%2Fsubscriptions%2Fddfba1ba-a22b-4bb4-b981-033e62bde697%2FresourceGroups%2Fxrs-nexus-dev-rg%2Fproviders%2FMicrosoft.Storage%2FstorageAccounts%2Fxrsnexusdevstg2yd1hw/path/bronze
