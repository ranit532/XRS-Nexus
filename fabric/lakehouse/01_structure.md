# Fabric Lakehouse Folder Structure

This document defines the physical storage structure for the XRS NEXUS Lakehouse in Microsoft Fabric.

## 1. Bronze Layer (Raw Ingestion)
**Path:** `Tables/Bronze` or `Files/Bronze` (depending on management style)
**Format:** Parquet / JSON (Landing), Delta (Managed)
**Retention:** 30 Days

| Folder | Description | Partitioning |
|:-------|:------------|:-------------|
| `/landing/sap_ecc/` | Raw SAP exports (IDocs, csv) | `year/month/day` |
| `/landing/sfdc/` | Salesforce object dumps | `year/month/day` |
| `/landing/apis/` | JSON responses from REST APIs | `year/month/day` |
| `/error_quarantine/` | Malformed records rejected by ingestion | `date/source_system` |

## 2. Silver Layer (Cleaned & Enriched)
**Path:** `Tables/Silver`
**Format:** Delta Lake (V-Order enabled)
**Optimization:** Z-Ordered by Join Keys

| Table Name | Description | Schema Enforcement |
|:-----------|:------------|:-------------------|
| `sap_kna1` | Customer Master Data (Cleaned) | Strict |
| `sfdc_account` | Salesforce Accounts (Cleaned) | Strict |
| `product_master` | Unified Product Catalog | Strict |

## 3. Gold Layer (Business Aggregates)
**Path:** `Tables/Gold`
**Format:** Delta Lake (V-Order enabled)
**Optimization:** Optimized for Read (DirectLake)

| Table Name | Description | Grain |
|:-----------|:------------|:------|
| `dim_customer` | Customer Dimension (Star Schema) | One row per customer |
| `fact_sales` | Sales Transactions | One row per line item |
| `agg_revenue_region` | Revenue Aggregates | Region / Month |

## 4. Temporary/Staging
**Path:** `Files/Staging`
- Used for ephemeral processing by Notebooks.
- Automatically cleaned up after 24 hours.
