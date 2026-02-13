# XRS NEXUS: Enterprise AI-Driven Integration Platform

## 1. Platform Overview

**XRS NEXUS** is an Azure-native, metadata-driven, AI-orchestrated integration platform for XRS Group UK. It revolutionizes how enterprise data is ingested, processed, and governed by replacing static ETL pipelines with dynamic, AI-generated integration flows.

The platform ingests metadata from 15+ heterogeneous enterprise systems (SAP, Salesforce, REST APIs, etc.), normalizes it into a canonical model, and uses **Azure AI Foundry (Prompt Flow + RAG)** to automatically generate and execute ETL/ELT pipelines on **Microsoft Fabric**.

---

## 2. Key Features & AI Capabilities

### 🧠 Core AI Brain (Azure AI Foundry)
We leverage **Azure AI Foundry** to orchestrate intelligent workflows using **Prompt Flow** and **GPT-4o**.

| Feature | Description | AI Technology |
|---------|-------------|---------------|
| **Intelligent Schema Mapping** | Auto-maps source fields to target schemas using historical patterns. | **RAG (Azure AI Search)** + Prompt Flow |
| **PII Detection & Governance** | Scans data payloads to identify and tag Sensitive/Confidential info. | **Prompty** + GPT-4o |
| **Automated Error Resolution** | Analyzes stack traces and error logs to suggest root causes and fixes. | Prompt Flow + **Self-Correction** |
| **SLA Breach Prediction** | Predicts pipeline runtime based on volume and historical telemetry. | Predictive AI (LLM-based) |
| **Natural Language to SQL** | Converts business questions ("Total sales in UK") into SparkSQL. | **NL2SQL** Prompt Flow |
| **Natural Language DQ Rules** | Converts English rules ("Revenue must be positive") into Python assertions. | **Prompty** + Data Quality |
| **Impact Analysis** | Generates human-readable reports on downstream impact of schema changes. | Lineage Graph + GenAI Summarization |

---

## 3. Technology Stack & Architecture

### Core Azure Services
| Service | Role |
|:--------|:-----|
| **Azure AI Foundry** | Unified platform for building and managing AI solutions (Hub & Projects). |
| **Azure OpenAI** | Provides LLM models (GPT-4o) and Embeddings for intelligence. |
| **Azure AI Search** | Vector Store and Retrieval engine for RAG (Schema Mapping). |
| **Prompt Flow** | Orchestration tool for linking LLMs, Python code, and data tools. |
| **Microsoft Fabric** | Unified data platform for Lakehouse storage and Spark compute. |
| **Terraform** | Infrastructure as Code (IaC) for reproducible deployments. |

### End-to-End Workflow
The platform operates in a continuous loop of **Listen -> Think -> Act**.

1.  **Ingest (Listen)**:
    *   Metadata is ingested from SAP/Salesforce into the **Bronze Lakehouse**.
    *   The **Metadata Intelligence Agent** scans this for new schema definitions.
2.  **Orchestrate (Think)**:
    *   **Prompt Flow** triggers a RAG lookup in **Azure AI Search** to find historical mapping patterns.
    *   **GPT-4o** analyzes the new fields and suggests a normalized schema.
    *   **Prompty** scans sample data for PII and tags it for governance.
3.  **Execute (Act)**:
    *   A dynamic **Spark Job** is generated and submitted to **Microsoft Fabric**.
    *   Data flows from Bronze -> Silver -> Gold tiers.
4.  **Monitor (Observe)**:
    *   Telemetry is logged to **Application Insights**.
    *   **SLA Agent** predicts completion times and alerts on breach risks.

### Architecture Diagram
```mermaid
flowchart TD
    subgraph "Ingestion Sources"
        SAP[SAP ECC]
        SFDC[Salesforce]
        API[REST APIs]
        ExtADLS[External ADLS Gen2]
    end

    subgraph "Microsoft Fabric Data Platform"
        direction TB
        
        subgraph "OneLake & Ingestion"
            Shortcut["OneLake Shortcuts"]
            DF["Dataflow Gen2"]
            Pipe["Data Factory Pipelines"]
        end

        subgraph "Lakehouse Architecture"
            Bronze[("Bronze Lake<br>Raw")]
            Silver[("Silver Lake<br>Clean")]
            Gold[("Gold Lake<br>Star Schema")]
        end

        subgraph "Compute & Intelligence"
            Spark["Spark Notebooks<br>(PySpark)"]
            SQL["SQL Endpoint<br>(T-SQL)"]
        end
        
        subgraph "Serving"
            PBI["Power BI<br>DirectLake"]
        end
    end

    subgraph "AI Brain (Azure AI Foundry)"
        Search["Azure AI Search<br>(Vector Store)"]
        OpenAI["Azure OpenAI<br>(GPT-4o)"]
        Flow[Prompt Flow Orchestrator]
    end

    %% Flows
    SAP & SFDC & API --> Pipe
    Pipe --> Bronze
    ExtADLS -.->|Shortcut| Shortcut
    Shortcut --> Bronze
    
    API --> DF
    DF --> Bronze

    Bronze -->|Run| Spark
    Spark -->|Transform| Silver
    Spark -->|Aggregate| Gold
    
    Gold -->|DirectLake| PBI
    Gold -->|Query| SQL
    
    %% AI Integration
    Bronze -->|Metadata Trigger| Flow
    Flow -->|Schema/Logic| Spark
    Flow <--> Search
    Flow <--> OpenAI
```

---

## 4. Microsoft Fabric Components

The project includes a comprehensive set of **Microsoft Fabric** artifacts to demonstrate a complete enterprise analytics solution.

| Component | Path | Description |
|:----------|:-----|:------------|
| **Lakehouse** | `/fabric/lakehouse/` | Bronze/Silver/Gold structures, DDLs, and table registration. |
| **Pipelines** | `/fabric/pipelines/` | Data Factory pipelines for orchestration and ingestion. |
| **Dataflows** | `/fabric/dataflows/` | Gen2 Dataflows for low-code transformation and mapping. |
| **OneLake** | `/fabric/onelake/` | Shortcuts to external ADLS/S3 and cross-workspace links. |
| **Notebooks** | `/fabric/notebooks/` | PySpark notebooks for Bronze->Silver->Gold ETL and DQ checks. |
| **SQL Endpoint** | `/fabric/sql/` | T-SQL scripts for analytics and NL2SQL validation. |
| **Power BI** | `/fabric/powerbi/` | Semantic models and report metadata for DirectLake. |
| **Governance** | `/fabric/governance/` | Lineage extraction and monitoring configurations. |

---

## 4.1. Azure Data Factory Pipeline Use Case

### Overview
In addition to the Microsoft Fabric-based architecture, this project includes a **cost-effective Azure Data Factory (ADF) implementation** that demonstrates:
- **Medallion Architecture**: Bronze → Silver → Gold data layers
- **AI-Powered Data Quality**: Automated validation using Azure Functions
- **Data Lineage Tracking**: Complete traceability with interactive visualizations
- **Enterprise Patterns**: Managed identity, secure credential management, monitoring


### ADF Pipeline Architecture

```mermaid
flowchart LR
    subgraph "Data Generation"
        GEN[Synthetic Data<br/>Generator<br/>20,500 records]
    end

    subgraph "ADLS Gen2 Storage Layers"
        BRONZE[(Bronze Layer<br/>Raw CSV<br/>customers, orders,<br/>products, transactions,<br/>events)]
        SILVER[(Silver Layer<br/>Cleaned Parquet<br/>Schema validated)]
        GOLD[(Gold Layer<br/>Analytics-Ready<br/>Aggregated)]
        LINEAGE[(Lineage Store<br/>Metadata JSON)]
    end

    subgraph "Azure Data Factory"
        direction TB
        PIPE1[Ingest Pipeline<br/>Copy Activities<br/>CSV → Parquet]
        PIPE2[Transform Pipeline<br/>Data Flows<br/>Join & Aggregate]
    end

    subgraph "AI Orchestration"
        FUNC[Azure Function<br/>/validate-data]
        AI[AI Validation<br/>• Null checks<br/>• Duplicates<br/>• PII detection]
    end

    subgraph "Monitoring & Lineage"
        CAP[Lineage Capture<br/>ADF API]
        VIZ[HTML Visualizer<br/>Mermaid Diagrams]
        APPI[Application<br/>Insights]
    end

    GEN -->|Upload| BRONZE
    BRONZE -->|Trigger| PIPE1
    PIPE1 -->|Call| FUNC
    FUNC -->|Validate| AI
    AI -->|Results| PIPE1
    PIPE1 -->|Write| SILVER
    
    SILVER -->|Transform| PIPE2
    PIPE2 -->|Write| GOLD
    
    PIPE1 & PIPE2 -->|Metadata| CAP
    CAP -->|Store| LINEAGE
    LINEAGE -->|Generate| VIZ
    PIPE1 & PIPE2 -->|Logs| APPI

    style BRONZE fill:#cd7f32,stroke:#8b4513,color:#fff
    style SILVER fill:#c0c0c0,stroke:#808080,color:#000
    style GOLD fill:#ffd700,stroke:#daa520,color:#000
    style FUNC fill:#0078d4,stroke:#005a9e,color:#fff
    style VIZ fill:#00d4aa,stroke:#00a884,color:#fff
```

### Data Flow Details

```mermaid
sequenceDiagram
    participant Gen as Data Generator
    participant Bronze as Bronze Layer
    participant ADF as ADF Pipeline
    participant AI as AI Validation
    participant Silver as Silver Layer
    participant Gold as Gold Layer
    participant Lin as Lineage Store

    Gen->>Bronze: Upload 20,500 records<br/>(5 datasets: CSV + JSON)
    
    Note over ADF: Pipeline: ingest_synthetic_data
    ADF->>Bronze: Read customers.csv
    ADF->>Bronze: Read orders.csv
    
    ADF->>AI: POST /validate-data<br/>{datasets: [customers, orders]}
    AI-->>ADF: {status: warning,<br/>checks: [nulls, duplicates, PII]}
    
    ADF->>Silver: Write customers.parquet<br/>(Snappy compressed)
    ADF->>Silver: Write orders.parquet
    
    Note over ADF: Pipeline: transform_and_merge
    ADF->>Silver: Read customers + orders
    ADF->>Gold: Write customer_analytics.parquet<br/>(Joined & aggregated)
    
    ADF->>Lin: Capture pipeline metadata
    Lin->>Lin: Generate lineage graph
    Lin-->>Lin: Create HTML visualization
```

### Deployed Components

| Component | Status | Description |
|-----------|--------|-------------|
| **ADLS Gen2 Containers** | ✅ Deployed | `bronze`, `silver`, `gold`, `synthetic-data`, `lineage` |
| **ADF Linked Services** | ✅ Deployed | Connections to all storage layers (managed identity) |
| **ADF Datasets** | ✅ Deployed | 5 datasets (CSV + Parquet formats) |
| **ADF Pipeline** | ✅ Deployed | `ingest_synthetic_data` (tested successfully) |
| **Synthetic Data** | ✅ Uploaded | 20,500 records across 5 datasets |
| **AI Validation** | ⚠️ Optional | Azure Function endpoint (code ready) |
| **Lineage Tracking** | ✅ Ready | Capture and visualization scripts |

### 5. Real-Time AI Validation Architecture

To enable real-time, intelligent validation within ADF pipelines without direct ADF-to-PromptFlow connectivity, we implemented a **Function-as-a-Proxy** pattern.

#### Architecture Flow
```mermaid
sequenceDiagram
    participant ADF as ADF Pipeline
    participant Func as Azure Function (Python)
    participant PF as Prompt Flow (Azure AI)
    participant LLM as GPT-4o Model

    ADF->>Func: POST /validate-data (Sample Data)
    Note over Func: api-layer/ai_validator.py
    
    Func->>PF: Invoke Flow "pii_detection"
    
    alt GPT Quota Available
        PF->>LLM: Analyze Payload
        LLM-->>PF: {has_pii: true, fields: [email]}
        PF-->>Func: Intelligent Result
        Func-->>ADF: {status: warning, ai_powered: true}
    else GPT Quota Exceeded (Fallback)
        PF--xFunc: Error (429/404)
        Func->>Func: Run Enhanced Regex Patterns
        Func-->>ADF: {status: warning, ai_powered: false}
    end
```

#### Why this approach?
1.  **Overcomes ADF Limitations**: ADF cannot natively call Prompt Flow endpoints with complex payloads easily.
2.  **Encapsulation**: The Azure Function acts as a "Smart Gateway", handling authentication, data sampling, and fallback logic.
3.  **Resilience**: If Azure AI services are down or quota is exceeded, the Function falls back to robust pattern matching, ensuring the pipeline never fails.
4.  **Cost Control**: We can cache results or limit AI calls within the Function logic.

### Quick Start - ADF Pipeline

#### 1. Generate and Upload Data
```bash
# Generate synthetic datasets
python3 synthetic-dataset/generate_adf_datasets.py

# Upload to ADLS Gen2
export AZURE_STORAGE_ACCOUNT_NAME=xrsnexusdevstg2yd1hw
python3 scripts/upload_to_adls.py
```

#### 2. Deploy Infrastructure
```bash
cd infra
terraform init
terraform plan -out adf.tfplan
terraform apply adf.tfplan
```

#### 3. Run Pipeline
```bash
# Trigger pipeline via Azure CLI
az datafactory pipeline create-run \
  --resource-group xrs-nexus-dev-rg \
  --factory-name xrs-nexus-dev-adf-2yd1hw \
  --name ingest_synthetic_data

# Or use the testing script
python3 scripts/test_adf_pipeline.py --pipeline ingest_synthetic_data
```

#### 4. Capture Lineage
```bash
# Get run ID from previous step
RUN_ID="<your-run-id>"

# Capture lineage metadata
python3 telemetry-lineage/adf_lineage_capture.py $RUN_ID

# Generate visualization
python3 telemetry-lineage/visualize_lineage.py lineage/adf_runs/lineage_*.json

# Open in browser
open lineage/adf_runs/lineage_*.html
```

### Test Results

**Latest Pipeline Run**:
- **Status**: ✅ Succeeded
- **Duration**: 30.9 seconds
- **Activities**: 2 copy activities (customers, orders)
- **Data Processed**: 7,000 records (2,000 customers + 5,000 orders)
- **Output**: Parquet files in silver layer with Snappy compression

**Verification**:
```bash
# Check silver layer contents
az storage fs directory list -f silver \
  --account-name xrsnexusdevstg2yd1hw \
  --auth-mode login

# Output:
# customers/
# orders/
```

### AI Validation Features

The AI orchestration layer provides:

1. **Null Value Detection**: Flags fields with >5% null values
2. **Duplicate Detection**: Identifies duplicate primary keys
3. **PII Scanning**: Detects email, phone, SSN patterns
4. **Data Type Validation**: Ensures schema compliance
5. **Recommendations**: Suggests data masking, encryption, or cleansing

**Example Response**:
```json
{
  "status": "warning",
  "validation_results": [{
    "dataset": "silver/customers",
    "checks": [
      {
        "check_name": "pii_detection",
        "status": "warning",
        "details": {"pii_fields_detected": ["email", "phone"]},
        "recommendation": "Apply data masking or encryption"
      }
    ]
  }]
}
```

### Lineage Visualization

The lineage capture system generates interactive HTML visualizations showing:
- **Data Flow**: Visual graph of transformations
- **Activity Details**: Individual pipeline activities
- **Metadata**: Run ID, status, duration, timestamps
- **Color-Coded Nodes**: Sources (blue), sinks (purple), transformations (orange)

**Sample Lineage Graph**:
```mermaid
graph LR
    DS1[ds_bronze_customers<br/>CSV Source]
    DS2[ds_bronze_orders<br/>CSV Source]
    ACT1[CopyCustomersToSilver<br/>Copy Activity]
    ACT2[CopyOrdersToSilver<br/>Copy Activity]
    DS3[ds_silver_customers<br/>Parquet Sink]
    DS4[ds_silver_orders<br/>Parquet Sink]

    DS1 -->|reads| ACT1
    ACT1 -->|writes| DS3
    DS2 -->|reads| ACT2
    ACT2 -->|writes| DS4

    style DS1 fill:#4a90e2,stroke:#2e5c8a,color:#fff
    style DS2 fill:#4a90e2,stroke:#2e5c8a,color:#fff
    style DS3 fill:#9b59b6,stroke:#6c3483,color:#fff
    style DS4 fill:#9b59b6,stroke:#6c3483,color:#fff
    style ACT1 fill:#e67e22,stroke:#a04000,color:#fff
    style ACT2 fill:#e67e22,stroke:#a04000,color:#fff
```

### Documentation

- **Deployment Guide**: [ADF_DEPLOYMENT_GUIDE.md](./ADF_DEPLOYMENT_GUIDE.md)
- **Walkthrough**: [walkthrough.md](./.gemini/antigravity/brain/2e618bc4-4cb3-4538-976b-c80bc0c991bd/walkthrough.md)
- **Implementation Plan**: [implementation_plan.md](./.gemini/antigravity/brain/2e618bc4-4cb3-4538-976b-c80bc0c991bd/implementation_plan.md)
- **Deployment Status**: [DEPLOYMENT_STATUS.md](./DEPLOYMENT_STATUS.md)



## 5. Comprehensive Deployment Guide

Follow these steps to deploy the platform from scratch.

### Step 1: Clone & Configure
1.  Clone the repository:
    ```bash
    git clone https://github.com/xps-group/xrs-nexus.git
    cd xrs-nexus
    ```
2.  Set up environment variables in a `.env` file (template provided below):
    ```ini
    AZURE_OPENAI_API_KEY=your_key
    AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
    AZURE_SEARCH_KEY=your_key
    AZURE_SEARCH_ENDPOINT=https://your-resource.search.windows.net/
    ```

### Step 2: Infrastructure Provisioning (Terraform)
We use Terraform to stand up the Azure AI and Data resources.
1.  Navigate to the infra directory:
    ```bash
    cd infra
    ```
2.  Initialize Terraform:
    ```bash
    terraform init
    ```
3.  Plan and Apply:
    ```bash
    terraform plan -out main.tfplan
    terraform apply main.tfplan
    ```
    *Note: In this repository Terraform provisions core low-cost resources (Resource Group, Storage account, Application Insights, and Azure Search). Microsoft Fabric workspace and Azure AI Foundry / Prompt Flow are NOT created automatically — they require tenant admin enablement and manual portal steps (see below).*

### Step 2.1: Fabric Environment Setup (Manual/Scripted)
Since automating Fabric Capacity requires specific tenant entitlements, we provide a script to set up your Fabric environment once you have a valid Capacity (or Trial).

1.  Keep your Azure Credential active (`az login`).
2.  Run the setup script:
    ```bash
    # Creates Workspace 'xrs-nexus-workspace', creates Lakehouse, and uploads simulated data
    python3 fabric/setup_fabric.py
    ```
    *(If you don't have a specific capacity to assign via API, simply creating the workspace in the UI and naming it `xrs-nexus-workspace` is sufficient, then run the script to create items).*

    > **Fallback: Simulation Mode**
    > If you cannot provision a Fabric Capacity yet, you can skip to **Step 6** and run the **Spark Simulation** scripts locally. The project is designed to run end-to-end using local JSON files as a robust fallback.

### PoC Infra Applied (Tenant Verification)

The following core resources have been provisioned and verified in the target subscription (examples from a verification run):

- **Resource Group:** xrs-nexus-dev-rg
- **Storage Account(s):** xrsnexusstg (and a secondary storage account `xrsnexusdevdc84ca6e`)
- **Log Analytics Workspace:** xrs-nexus-dev-law
- **Application Insights:** xrs-nexus-appi
- **Azure Cognitive Search:** xrs-nexus-dev-search (SKU: free)

You can verify these resources locally with the Azure CLI (example):

```bash
az group show -n xrs-nexus-dev-rg
az resource list -g xrs-nexus-dev-rg -o table
az storage account show -g xrs-nexus-dev-rg -n xrsnexusstg -o json
az search service show -g xrs-nexus-dev-rg -n xrs-nexus-dev-search -o json
az monitor app-insights component show -g xrs-nexus-dev-rg -n xrs-nexus-appi -o json
```

Next steps to complete the end-to-end PoC (manual actions required):

- Create a **Microsoft Fabric workspace** in the Azure portal or request tenant enablement for Fabric capacities.
- Create an **Azure AI Foundry / Prompt Flow project** in AI Studio (requires a portal action and appropriate subscription access).
- Once the Fabric workspace and Foundry/Prompt Flow project exist, run the provided import scripts in `/infra/import_promptflow.sh` to import flows from `ai-orchestration/flows/` (the scripts are dry-run safe; they require the Foundry/Prompt Flow admin endpoint and token).

See `/infra/README_PROVISIONING.md`, `/infra/foundry_runbook.md` and `/infra/promptflow_runbook.md` for detailed step-by-step guidance and tenant-runbook tasks.

### Step 3: Data Generation (Simulation)
Generate synthetic data to simulate a production workload for testing.
1.  Generate Metadata (Simulates SAP/Salesforce schemas):
    ```bash
    python3 synthetic-dataset/generate_metadata.py
    # Output: data/metadata_samples.json (1000+ records)
    ```
2.  Generate Telemetry (Simulates execution logs):
    ```bash
    python3 synthetic-dataset/generate_telemetry.py
    # Output: data/telemetry_logs.json (1000+ records)
    ```

### Step 4: RAG System Setup
Index the generated metadata into Azure AI Search to enable the "Intelligent Mapping" capability.
1.  Run the indexer script:
    ```bash
    python3 ai-orchestration/rag/indexer.py
    ```
    *This chunks the metadata descriptions, creates embeddings using OpenAI, and pushes them to the Vector Store.*

### Step 5: Executing AI Workflows
Now you can run the actual Prompt Flows.
1.  **Schema Mapping Flow**:
    ```bash
    # Test mapping a field 'KUNNR' (German for Customer Number in SAP)
    pf flow test --flow ai-orchestration/flows/schema_mapping --inputs source_field="KUNNR"
    ```
    pf flow test --flow ai-orchestration/flows/nl2sql --inputs user_question="Show total revenue for UK"
    ```

### Step 5.1: Executing Advanced Python SDK Flows
We have implemented 5 advanced use cases using the **Prompt Flow Python SDK**.
1.  **Multi-Source Schema Mapping** (Simulated RAG)
2.  **Context-Aware NL2SQL** (with Validation)
3.  **Intelligent PII Redaction** (Prompty-based)
4.  **Automated Error Root Cause Analysis** (Log Analysis)
5.  **Natural Language Data Quality Rules** (English to Python)

To run all these flows locally:
```bash
# Install dependencies
python3 -m pip install prompty promptflow-tools

# Run the master orchestration script (Unit Tests)
python3 ai-orchestration/setup_flows.py
```

### Step 5.2: Running the Integrated "Connected" Demo
To demonstrate the full Metadata Driven Architecture (Data -> AI -> Insights), run the integrated simulation script. This script:
1.  Ingests real metadata records from the simulated Bronze Lakehouse.
2.  Triggers "Schema Mapping" and "DQ Rule" flows dynamically based on that data.
3.  Simulates a "Critical Error" in telemetry and triggers the "RCA" flow.

```bash
python3 ai-orchestration/run_integrated_demo.py
```


Deploy the Azure Function to expose the platform APIs.
1.  Navigate to the API folder:
    ```bash
    cd api-layer
    ```
2.  Start locally:
    ```bash
    func start
    ```

---

## 6. Advanced AI Use Cases & Execution Guide
This section details the 5 advanced Prompt Flow use cases implemented in the project, including their logic and how to test them.

### Use Case 1: Multi-Source Schema Mapping (RAG)
**Goal:** Map disparate fields from source systems (SAP, Salesforce) to the Enterprise Canonical Model.
**Logic:**
1.  **Retrieve:** Simulates searching a Vector Store (RAG) for field definitions in SAP/Salesforce dictionaries.
2.  **Resolve:** Uses GPT-4o to semantically match the source field to a target Canonical Field.
**Test Input:**
```json
{
  "source_field": "KUNNR",
  "source_system": "SAP"
}
```
**Expected Output:** Match `KUNNR` -> `CustomerID` with high confidence.

---

### Use Case 2: Context-Aware NL2SQL
**Goal:** Convert natural language business questions into executable SparkSQL.
**Logic:**
1.  **Schema Lookup:** Retrieves the schema for the requested table.
2.  **SQL Gen:** Prompty generates the SparkSQL query.
3.  **Validation:** Python tool validates syntax (e.g., ensures `SELECT` only, no `DROP`).
**Test Input:**
```json
{
  "question": "Show total sales by region",
  "table_name": "sales_data"
}
```
**Expected Output:** `SELECT region, SUM(amount) FROM sales_data GROUP BY region...`

---

### Use Case 3: Intelligent PII Redaction
**Goal:** Redact sensitive personal data while preserving business context.
**Logic:** Uses a Prompty to identify PII (Names, Emails) and replace them with tokens (`[PERSON]`, `[EMAIL]`) without removing non-sensitive IDs.
**Test Input:**
```json
{
  "text": "Please contact John Doe (john.doe@enterprise.com) regarding invoice #INV-2024-001."
}
```
**Expected Output:** `Please contact [PERSON] ([EMAIL]) regarding invoice #INV-2024-001.`

---

### Use Case 4: Automated Error Root Cause Analysis (RCA)
**Goal:** Diagnose Spark/Application errors from log traces.
**Logic:**
1.  **Retrieve:** Searches a "Known Error Database" for similar past issues.
2.  **Analyze:** LLM combines the log and context to suggest a Root Cause and Fix.
**Test Input:**
```json
{
  "error_log": "java.lang.OutOfMemoryError: Java heap space"
}
```
**Expected Output:** Suggests increasing `spark.executor.memory`.

---

### Use Case 5: Natural Language Data Quality Rules
**Goal:** Enable business users to define DQ rules in plain English.
**Logic:** Translates English requirements into Python `Great Expectations` syntax.
**Test Input:**
```json
{
  "rule": "Revenue must be positive."
}
```
**Expected Output:** `df.expect_column_values_to_be_between("revenue", min_value=0)`

---

## 7. Project Structure Reference

*   **`/ai-orchestration`**: The "Brain". Contains Prompt Flows, RAG scripts, and Prompty files.
*   **`/infra`**: The "Body". Terraform code to build the Azure environment.
*   **`/synthetic-dataset`**: The "Fuel". Scripts to generate large-scale test data.
*   **`/etl-execution`**: The "Muscle". Spark scripts that effectively transform the data.
*   **`/fabric`**: The "Platform". Integration artifacts for Microsoft Fabric (Lakehouse, Pipelines, Notebooks).

---

## 8. Alternative Architecture (Option B: No Fabric)

If Microsoft Fabric is not available in your tenant, the solution can be deployed using the "Modern Data Stack" on Azure (Synapse + Databricks + ADF).

### Architecture Diagram (Standard Azure)
```mermaid
flowchart TD
    subgraph "Ingestion"
        Sources[SAP / Salesforce] --> ADF[Azure Data Factory]
        ADF --> ADLS["ADLS Gen2 (Bronze)"]
    end

    subgraph "Processing & AI"
        ADLS --> DB[Azure Databricks]
        DB -->|Spark ETL| ADLS_Silver["ADLS Gen2 (Silver)"]
        DB <-->|AI Skills| PF[Prompt Flow]
    end

    subgraph "Serving"
        ADLS_Silver --> Synapse[Synapse Serverless SQL]
        Synapse --> PBI[Power BI]
    end
```

### Setup Instructions (Option B)

1.  **Provision Infrastructure**:
    The terraform configuration in `infra/modern_data_stack.tf` will provision ADF, Databricks, and Synapse automatically.
    ```bash
    cd infra
    terraform apply
    ```

2.  **Upload Data (ADLS Gen2)**:
    Instead of OneLake, we push data to standard ADLS Gen2 containers.
    ```bash
    python3 scripts/upload_to_adls.py
    ```

3.  **Run Processing**:
    Use the Databricks Workspace to mount the ADLS containers and run the same PySpark logic found in `etl-execution/spark_jobs/`.