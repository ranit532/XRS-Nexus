# Step-by-Step: Create ADF Pipeline for Synapse Spark

## ✅ Prerequisites Complete
- Synapse workspace: `xrs-nexus-dev-synapse-2yd1hw`
- Spark pool: `sparkpool01`
- Notebooks published: `process_bronze_to_silver`, `process_silver_to_gold`
- ADF linked service: `LS_Synapse`

---

## 📝 Create the Pipeline (5 minutes)

### Step 1: Open Data Factory Studio
1. Go to: **https://adf.azure.com**
2. Select factory: **`xrs-nexus-dev-adf-2yd1hw`**

### Step 2: Create New Pipeline
1. Click **Author** (pencil icon on left sidebar)
2. Click **+** (plus icon) → **Pipeline** → **Pipeline**
3. In the Properties panel (right side):
   - Name: `PL_ETL_Synapse_Bronze_to_Gold`
   - Description: `ETL pipeline using Synapse Spark notebooks`

### Step 3: Add First Activity (Bronze → Silver)
1. In the **Activities** panel, expand **Synapse**
2. Drag **Synapse Notebook** activity onto the canvas
3. In the **General** tab (bottom):
   - Name: `Process_Bronze_to_Silver`
4. In the **Settings** tab (bottom):
   - **Synapse workspace**: Select `LS_Synapse`
   - **Notebook**: Select `process_bronze_to_silver`
   - **Spark pool**: Select `sparkpool01`

### Step 4: Add Second Activity (Silver → Gold)
1. Drag another **Synapse Notebook** activity onto the canvas
2. In the **General** tab:
   - Name: `Process_Silver_to_Gold`
3. In the **Settings** tab:
   - **Synapse workspace**: Select `LS_Synapse`
   - **Notebook**: Select `process_silver_to_gold`
   - **Spark pool**: Select `sparkpool01`

### Step 5: Connect Activities
1. Click on the **green box** on the right side of `Process_Bronze_to_Silver`
2. Drag the arrow to `Process_Silver_to_Gold`
3. This creates a dependency: Silver runs only after Bronze succeeds

### Step 6: Publish Pipeline
1. Click **Publish all** (top toolbar)
2. Review changes → Click **Publish**
3. Wait for "Publishing succeeded" message

---

## 🚀 Run the Pipeline

### Option 1: Via ADF Studio (Recommended)
1. Click **Add trigger** (top toolbar) → **Trigger now**
2. Click **OK** in the popup
3. Click **Monitor** (left sidebar) to watch execution
4. Pipeline should complete in **4-8 minutes**

### Option 2: Via Azure CLI
```bash
az datafactory pipeline create-run \
  --factory-name xrs-nexus-dev-adf-2yd1hw \
  --name PL_ETL_Synapse_Bronze_to_Gold \
  --resource-group xrs-nexus-dev-rg
```

---

## 📊 Monitor Execution

### In ADF Studio
1. Click **Monitor** (left sidebar)
2. Click **Pipeline runs**
3. Find `PL_ETL_Synapse_Bronze_to_Gold`
4. Click on the run to see activity details
5. Watch the progress:
   - **Queued** → **InProgress** → **Succeeded**

### Expected Timeline
| Phase | Duration | Status |
|-------|----------|--------|
| Spark Pool Startup | 2-4 min | First run only |
| Bronze → Silver | 1-2 min | Processing |
| Silver → Gold | 1-2 min | Aggregating |
| **Total** | **4-8 min** | ✅ Success |

---

## ✅ Verify Results

After pipeline succeeds, check the data:

```bash
# Check Silver layer
az storage fs file list \
  --file-system silver \
  --account-name xrsnexusdevstg2yd1hw \
  --auth-mode login \
  --query "[].name" -o table

# Check Gold layer
az storage fs file list \
  --file-system gold \
  --account-name xrsnexusdevstg2yd1hw \
  --auth-mode login \
  --query "[].name" -o table
```

Expected output:
- Silver: `metadata_clean.parquet/`
- Gold: `schema_stats.parquet/`

---

## 🎉 Success Criteria

✅ Pipeline status: **Succeeded**
✅ Both activities: **Succeeded**
✅ Data in Silver: `metadata_clean.parquet`
✅ Data in Gold: `schema_stats.parquet`
✅ Execution time: **4-8 minutes**

---

## Next Steps After Success

1. **Document the solution** ✍️
2. **Integrate with Prompt Flow** 🤖
3. **Set up scheduled triggers** ⏰
4. **Create monitoring alerts** 📊

---

**Ready to create the pipeline? Follow the steps above in ADF Studio!**
