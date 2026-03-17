# Synthetic Salesforce-Style Multi-Layer Dataset

This folder contains synthetic CSV files generated from the manifest
`salesforce_sample_layers_semantic_relational` for data quality, lineage, and discovery testing.

## Files and Row Counts

| Entity | Relative Path | Total | Valid | Borderline | Invalid |
|--------|---------------|-------|-------|------------|---------|
| sf_life_customer_profile_master | 01_master_data_layer/sf_life_customer_profile_master.csv | 30 | 21 | 4 | 5 |
| sf_life_beneficiary_party_master | 01_master_data_layer/sf_life_beneficiary_party_master.csv | 30 | 21 | 4 | 5 |
| sf_life_policy_contract_master | 01_master_data_layer/sf_life_policy_contract_master.csv | 30 | 21 | 4 | 5 |
| sf_health_member_profile_master | 01_master_data_layer/sf_health_member_profile_master.csv | 30 | 21 | 4 | 5 |
| sf_health_provider_party_master | 01_master_data_layer/sf_health_provider_party_master.csv | 30 | 21 | 4 | 5 |
| sf_health_policy_contract_master | 01_master_data_layer/sf_health_policy_contract_master.csv | 30 | 21 | 4 | 5 |
| sf_general_broker_distribution_master | 01_master_data_layer/sf_general_broker_distribution_master.csv | 30 | 21 | 4 | 5 |
| sf_general_policy_contract_master | 01_master_data_layer/sf_general_policy_contract_master.csv | 30 | 21 | 4 | 5 |
| sf_life_beneficiary_payout_claim_transaction | 02_transactional_application_data_layer/sf_life_beneficiary_payout_claim_transaction.csv | 50 | 35 | 8 | 7 |
| sf_life_premium_invoice_collection_transaction | 02_transactional_application_data_layer/sf_life_premium_invoice_collection_transaction.csv | 50 | 35 | 8 | 7 |
| sf_health_hospital_claim_transaction | 02_transactional_application_data_layer/sf_health_hospital_claim_transaction.csv | 50 | 35 | 8 | 7 |
| sf_general_motor_loss_claim_transaction | 02_transactional_application_data_layer/sf_general_motor_loss_claim_transaction.csv | 50 | 35 | 8 | 7 |
| sf_life_annuity_product_configuration | 03_configuration_control_data_layer/sf_life_annuity_product_configuration.csv | 20 | 14 | 3 | 3 |
| sf_health_plan_product_configuration | 03_configuration_control_data_layer/sf_health_plan_product_configuration.csv | 20 | 14 | 3 | 3 |
| sf_health_benefit_coverage_configuration | 03_configuration_control_data_layer/sf_health_benefit_coverage_configuration.csv | 20 | 14 | 3 | 3 |
| sf_general_motor_product_configuration | 03_configuration_control_data_layer/sf_general_motor_product_configuration.csv | 20 | 14 | 3 | 3 |
| sf_general_underwriting_risk_configuration | 03_configuration_control_data_layer/sf_general_underwriting_risk_configuration.csv | 20 | 14 | 3 | 3 |
| sf_general_accounting_posting_control_configuration | 03_configuration_control_data_layer/sf_general_accounting_posting_control_configuration.csv | 20 | 14 | 3 | 3 |
| sf_life_policy_maturity_reporting | 04_analytical_reporting_layer/sf_life_policy_maturity_reporting.csv | 25 | 18 | 4 | 3 |
| sf_health_claim_authorization_reporting | 04_analytical_reporting_layer/sf_health_claim_authorization_reporting.csv | 25 | 18 | 4 | 3 |
| sf_general_broker_profitability_reporting | 04_analytical_reporting_layer/sf_general_broker_profitability_reporting.csv | 25 | 18 | 4 | 3 |
| sf_general_claim_reserve_reporting | 04_analytical_reporting_layer/sf_general_claim_reserve_reporting.csv | 25 | 18 | 4 | 3 |

## Relationship Logic

The following referential relationships are enforced for VALID rows:

- sf_life_policy_contract_master.life_customer_identifier → sf_life_customer_profile_master.life_customer_identifier (many_to_one)
- sf_life_policy_contract_master.beneficiary_party_identifier → sf_life_beneficiary_party_master.beneficiary_party_identifier (many_to_one)
- sf_life_policy_contract_master.annuity_product_code → sf_life_annuity_product_configuration.annuity_product_code (many_to_one)
- sf_life_beneficiary_payout_claim_transaction.related_life_policy_number → sf_life_policy_contract_master.life_policy_number (many_to_one)
- sf_life_beneficiary_payout_claim_transaction.beneficiary_party_identifier → sf_life_beneficiary_party_master.beneficiary_party_identifier (many_to_one)
- sf_life_premium_invoice_collection_transaction.life_policy_number → sf_life_policy_contract_master.life_policy_number (many_to_one)
- sf_life_premium_invoice_collection_transaction.life_customer_identifier → sf_life_customer_profile_master.life_customer_identifier (many_to_one)
- sf_life_policy_maturity_reporting.annuity_product_code → sf_life_annuity_product_configuration.annuity_product_code (many_to_one)
- sf_health_policy_contract_master.insured_member_identifier → sf_health_member_profile_master.insured_member_identifier (many_to_one)
- sf_health_policy_contract_master.preferred_provider_party_identifier → sf_health_provider_party_master.provider_party_identifier (many_to_one)
- sf_health_policy_contract_master.health_product_code → sf_health_plan_product_configuration.health_product_code (many_to_one)
- sf_health_policy_contract_master.health_coverage_identifier → sf_health_benefit_coverage_configuration.health_coverage_identifier (many_to_one)
- sf_health_hospital_claim_transaction.health_policy_number → sf_health_policy_contract_master.health_policy_number (many_to_one)
- sf_health_hospital_claim_transaction.insured_member_identifier → sf_health_member_profile_master.insured_member_identifier (many_to_one)
- sf_health_hospital_claim_transaction.provider_party_identifier → sf_health_provider_party_master.provider_party_identifier (many_to_one)
- sf_health_claim_authorization_reporting.health_product_code → sf_health_plan_product_configuration.health_product_code (many_to_one)
- sf_health_claim_authorization_reporting.provider_party_identifier → sf_health_provider_party_master.provider_party_identifier (many_to_one)
- sf_general_policy_contract_master.broker_partner_identifier → sf_general_broker_distribution_master.broker_partner_identifier (many_to_one)
- sf_general_policy_contract_master.general_product_code → sf_general_motor_product_configuration.general_product_code (many_to_one)
- sf_general_policy_contract_master.underwriting_rule_identifier → sf_general_underwriting_risk_configuration.underwriting_rule_identifier (many_to_one)
- sf_general_motor_loss_claim_transaction.general_policy_number → sf_general_policy_contract_master.general_policy_number (many_to_one)
- sf_general_motor_loss_claim_transaction.underwriting_rule_identifier → sf_general_underwriting_risk_configuration.underwriting_rule_identifier (many_to_one)
- sf_general_broker_profitability_reporting.broker_partner_identifier → sf_general_broker_distribution_master.broker_partner_identifier (many_to_one)
- sf_general_broker_profitability_reporting.general_product_code → sf_general_motor_product_configuration.general_product_code (many_to_one)
- sf_general_claim_reserve_reporting.ledger_account_code → sf_general_accounting_posting_control_configuration.ledger_account_code (many_to_one)
- sf_general_claim_reserve_reporting.underwriting_rule_identifier → sf_general_underwriting_risk_configuration.underwriting_rule_identifier (many_to_one)
- sf_general_claim_reserve_reporting.general_product_code → sf_general_motor_product_configuration.general_product_code (many_to_one)

## Error Injection Strategy

The generator creates three categories of rows per entity:
- **VALID (≈70%)**: Fully consistent with business keys and relationships.
- **BORDERLINE (≈15%)**: Suspicious but mostly consistent (e.g., odd emails, numeric outliers).
- **INVALID (≈15%)**: Intentionally corrupted for DQ tests.

Invalid patterns include:
- Broken foreign keys with `i`-prefixed identifiers (orphan references).
- Invalid enumerations like `iACTIVE` and `UNKNOWN_X`.
- Malformed dates such as `2025-13-40` and impossible ranges.
- Negative premium and amount values, and percentages > 100.
- String values injected into numeric fields and vice versa.
- Duplicate business keys in transactional/reporting entities with conflicting attributes.
- Attribute-level `i`-prefix corruption to simulate semantic mismatches.

## Usage for Testing

- Use master and configuration entities as golden sources for keys and domain semantics.
- Join transactional entities to master/configuration to validate foreign-key integrity and orphan detection.
- Validate that reporting-layer aggregates reconcile with underlying detail rows for VALID records, and flag inconsistencies from INVALID rows.
- Apply semantic classification and lineage tools to verify correct layer, LOB, and business-domain detection.