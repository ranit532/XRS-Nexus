# Synthetic Salesforce-Style Data Generator

This folder contains a Python-based generator that produces a complete synthetic, multi-layer Salesforce-inspired insurance dataset for data quality, lineage, and semantic discovery testing.

## Contents

- `generate_synthetic_salesforce_data.py` – main generator script.
- `output/` – generated CSV files organized by layer:
  - `01_master_data_layer/`
  - `02_transactional_application_data_layer/`
  - `03_configuration_control_data_layer/`
  - `04_analytical_reporting_layer/`
  - `synthetic_data_generation_summary.json`
  - `README.md` (auto-generated description of the dataset and DQ scenarios)

## How to Run

1. Ensure you have Python 3.9+ installed.
2. From the project root (`discover-your-data`), install dependencies:

   ```bash
   pip install pandas faker
   ```

3. Run the generator from the project root so the manifest path resolves correctly:

   ```bash
   python synthetic-data-generator/generate_synthetic_salesforce_data.py
   ```

4. Inspect the generated files under `synthetic-data-generator/output/`.

## Generation Logic (High Level)

- Parses `data/salesforce_sample_layers_semantic_relational_manifest.json` for:
  - entities and attributes
  - business keys
  - target layer and line-of-business
  - cross-entity relationships
- Generates data for all entities with default row counts per layer:
  - Master Data Layer: ~30 rows per entity
  - Configuration / Control Data: ~20 rows per entity
  - Transactional / Application Data Layer: ~50 rows per entity
  - Analytical / Reporting Layer: ~25 rows per entity
- Uses deterministic ID patterns by line of business (e.g. `LIFE_CUST_###`, `HLTH_MEM_###`, `GEN_POL_###`, `LEDGER_###`).
- Enforces referential integrity for **VALID** rows by sampling foreign keys according to the manifest relationships.

## Data Quality and Lineage Scenarios

For each entity, rows are split into three categories (tracked internally and in the summary JSON):

- **VALID (~70%)** – clean, relationship-compliant records.
- **BORDERLINE (~15%)** – plausible but low-quality records (e.g. odd emails, numeric outliers).
- **INVALID (~15%)** – intentionally corrupted records.

The generator injects a variety of DQ patterns, including:

- Broken foreign keys and orphan references using `i`-prefixed identifiers.
- Cross-entity inconsistencies and wrong-domain values.
- Malformed and impossible dates (e.g. `2025-13-40`).
- Negative premiums and amounts, and percentages greater than 100.
- String values in numeric fields / numeric-like values in classification fields.
- Invalid status values such as `iACTIVE` and `UNKNOWN_X`.
- Duplicate business keys (in transactional/reporting entities) with conflicting attributes.
- Attribute-level corruption using an `i` prefix to simulate semantic mismatch.

These patterns support testing for:

- exact and near-match relationships
- broken lineage and orphan detection
- wrong business domain / LOB / layer classification
- duplicate key handling and conflict resolution
- cross-file dependency failures and inconsistent reporting aggregates

## Sample Output Schema (Overview)

Examples of generated entities and key fields:

- Master (Life):
  - `sf_life_customer_profile_master.csv` – `life_customer_identifier`, `customer_full_name`, `date_of_birth`, `customer_email_address`, `customer_phone_number`, KYC and risk profile.
  - `sf_life_policy_contract_master.csv` – `life_policy_number`, `life_customer_identifier`, `beneficiary_party_identifier`, `annuity_product_code`, issue/maturity dates, status, premium frequency, sum assured.
- Master (Health / General):
  - `sf_health_member_profile_master.csv` – `insured_member_identifier`, demographics and contact fields.
  - `sf_general_policy_contract_master.csv` – `general_policy_number`, `broker_partner_identifier`, `general_product_code`, `underwriting_rule_identifier`, coverage dates and insured value.
- Configuration:
  - `sf_life_annuity_product_configuration.csv` – `annuity_product_code`, plan and rule fields.
  - `sf_general_accounting_posting_control_configuration.csv` – `ledger_account_code`, posting and reserve control fields.
- Transactional:
  - `sf_life_premium_invoice_collection_transaction.csv` – `premium_invoice_number`, `life_policy_number`, `life_customer_identifier`, billing dates, premium amounts, payment status.
  - `sf_health_hospital_claim_transaction.csv` – `health_claim_number`, `health_policy_number`, `insured_member_identifier`, `provider_party_identifier`, hospitalization and claim amounts.
- Reporting:
  - `sf_life_policy_maturity_reporting.csv` – `reporting_month`, `annuity_product_code`, maturity buckets, policy counts, exposure and premium totals.
  - `sf_general_claim_reserve_reporting.csv` – `reporting_month`, `ledger_account_code`, `underwriting_rule_identifier`, `general_product_code`, reserve and settlement metrics.

Use the generated CSVs, the summary JSON, and the auto-generated dataset README under `output/` to drive end-to-end data quality monitoring, lineage validation, semantic classification, and data discovery tests.