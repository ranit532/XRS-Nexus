import json
import random
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
from faker import Faker


RANDOM_SEED = 42

# Row count configuration by target layer
LAYER_ROW_COUNTS = {
    "Master Data Layer": 30,
    "Configuration / Control Data": 20,
    "Transactional / Application Data Layer": 50,
    "Analytical / Reporting Layer": 25,
}


def load_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Load the JSON manifest that defines entities, attributes and relationships."""
    with manifest_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _build_relationship_maps(manifest: Dict[str, Any]) -> Tuple[Dict[str, Dict[str, Tuple[str, str]]], Dict[str, List[Dict[str, str]]]]:
    """Build convenience maps for foreign-key lookup and parent relationships.

    Returns:
        fk_map: from_entity -> { from_key: (to_entity, to_key) }
        parent_rels: to_entity -> list of relationship dicts where it is parent
    """
    fk_map: Dict[str, Dict[str, Tuple[str, str]]] = {}
    parent_rels: Dict[str, List[Dict[str, str]]] = {}

    for rel in manifest.get("relationships", []):
        from_entity = rel["from_entity"]
        to_entity = rel["to_entity"]
        from_key = rel["from_key"]
        to_key = rel["to_key"]

        fk_map.setdefault(from_entity, {})[from_key] = (to_entity, to_key)
        parent_rels.setdefault(to_entity, []).append(rel)

    return fk_map, parent_rels


def _topological_entity_order(manifest: Dict[str, Any]) -> List[str]:
    """Derive an entity generation order that respects parent/child relationships."""
    entities = [f["entity_name"] for f in manifest.get("files", [])]
    relationships = manifest.get("relationships", [])

    # Build directed graph: parent (to_entity) -> child (from_entity)
    adjacency: Dict[str, List[str]] = {e: [] for e in entities}
    indegree: Dict[str, int] = {e: 0 for e in entities}

    for rel in relationships:
        parent = rel["to_entity"]
        child = rel["from_entity"]
        # Guard against entities not present in files
        if parent not in adjacency or child not in adjacency:
            continue
        adjacency[parent].append(child)
        indegree[child] += 1

    # Kahn's algorithm
    queue = [e for e in entities if indegree[e] == 0]
    order: List[str] = []

    while queue:
        node = queue.pop(0)
        order.append(node)
        for nbr in adjacency[node]:
            indegree[nbr] -= 1
            if indegree[nbr] == 0:
                queue.append(nbr)

    # Fallback: if there is a cycle or missing entities, just return original order
    if len(order) != len(entities):
        return entities

    return order


def _row_counts_for_entity(entity_cfg: Dict[str, Any]) -> int:
    layer = entity_cfg.get("target_layer", "")
    return LAYER_ROW_COUNTS.get(layer, 30)


def _build_business_key_map(manifest: Dict[str, Any]) -> Dict[str, List[str]]:
    """Map entity_name -> list of business key column names."""
    return {f["entity_name"]: f.get("business_keys", []) for f in manifest.get("files", [])}


def _detect_lob(entity_cfg: Dict[str, Any]) -> str:
    return entity_cfg.get("target_line_of_business", "Unknown")


def _generate_business_key_value(entity_name: str, attr_name: str, row_index: int, faker: Faker) -> Any:
    """Generate deterministic but realistic business-key style identifiers."""
    seq = row_index + 1

    # Life Insurance identifiers
    if attr_name == "life_customer_identifier":
        return f"LIFE_CUST_{seq:03d}"
    if attr_name == "beneficiary_party_identifier":
        return f"LIFE_BEN_{seq:03d}"
    if attr_name == "life_policy_number":
        return f"LIFE_POL_{seq:03d}"
    if attr_name == "annuity_product_code":
        return f"LIFE_PROD_{seq:03d}"
    if attr_name == "life_claim_number":
        return f"LIFE_CLM_{seq:04d}"
    if attr_name == "premium_invoice_number":
        return f"LIFE_INV_{seq:05d}"

    # Health Insurance identifiers
    if attr_name == "insured_member_identifier":
        return f"HLTH_MEM_{seq:03d}"
    if attr_name == "provider_party_identifier":
        return f"HLTH_PRV_{seq:03d}"
    if attr_name == "health_policy_number":
        return f"HLTH_POL_{seq:03d}"
    if attr_name == "health_product_code":
        return f"HLTH_PROD_{seq:03d}"
    if attr_name == "health_coverage_identifier":
        return f"HLTH_COV_{seq:03d}"
    if attr_name == "health_claim_number":
        return f"HLTH_CLM_{seq:04d}"

    # General Insurance identifiers
    if attr_name == "broker_partner_identifier":
        return f"GEN_BRK_{seq:03d}"
    if attr_name == "general_policy_number":
        return f"GEN_POL_{seq:03d}"
    if attr_name == "general_product_code":
        return f"GEN_PROD_{seq:03d}"
    if attr_name == "underwriting_rule_identifier":
        return f"GEN_UW_{seq:03d}"
    if attr_name == "general_claim_number":
        return f"GEN_CLM_{seq:04d}"
    if attr_name == "ledger_account_code":
        return f"LEDGER_{seq:04d}"

    # Fallback for any other business key style field
    if attr_name.endswith("_number") or attr_name.endswith("_id") or attr_name.endswith("_identifier"):
        prefix = attr_name.upper().replace("_", "")[:6]
        return f"{prefix}_{seq:04d}"

    return faker.uuid4()


def _random_date_pair(faker: Faker, min_year: int = 2015, max_year: int = 2025) -> Tuple[str, str]:
    """Generate a realistic issue/maturity date pair using concrete date objects."""
    start_issue = date(min_year, 1, 1)
    end_issue = date(max_year, 6, 30)
    issue = faker.date_between(start_date=start_issue, end_date=end_issue)

    start_maturity = issue
    end_maturity = date(max_year + 5, 12, 31)
    maturity = faker.date_between(start_date=start_maturity, end_date=end_maturity)

    return issue.isoformat(), maturity.isoformat()


def _generate_generic_value(attr_name: str, faker: Faker, row_ctx: Dict[str, Any]) -> Any:
    lower = attr_name.lower()

    if "email" in lower:
        return faker.email()
    if "phone" in lower or "contact" in lower:
        return faker.msisdn()[:10]
    if "address" in lower:
        return faker.address().replace("\n", ", ")
    if "name" in lower:
        return faker.name()
    if "date_of_birth" in lower:
        return faker.date_of_birth(minimum_age=18, maximum_age=80).isoformat()
    if "date" in lower:
        # Some date fields participate in pairs we control separately
        if lower == "policy_issue_date" or lower == "coverage_start_date":
            # handled via row_ctx in dedicated logic
            pass
        if lower.endswith("_date"):
            start_generic = date(2018, 1, 1)
            end_generic = date(2025, 12, 31)
            return faker.date_between(start_date=start_generic, end_date=end_generic).isoformat()

    if "amount" in lower or "premium" in lower or "sum_assured" in lower or "exposure" in lower:
        return round(random.uniform(1000, 250000), 2)
    if "percentage" in lower or "rate" in lower:
        return round(random.uniform(0, 100), 2)
    if lower.endswith("_count"):
        return random.randint(0, 500)

    if "status" in lower:
        if "policy" in lower:
            return random.choice(["ACTIVE", "LAPSED", "MATURED"])
        if "claim" in lower:
            return random.choice(["OPEN", "APPROVED", "REJECTED", "PENDING_DOCS"])
        if "kyc" in lower:
            return random.choice(["VERIFIED", "PENDING", "FAILED"])
        return random.choice(["ACTIVE", "INACTIVE"])

    if "frequency" in lower:
        return random.choice(["MONTHLY", "QUARTERLY", "ANNUAL"])

    if "bucket" in lower:
        return random.choice(["0-1Y", "1-3Y", "3-5Y", ">5Y"])

    if "diagnosis" in lower:
        return random.choice(["D001", "D045", "D123", "D999"])

    if "treatment" in lower:
        return random.choice(["SURGERY", "PHYSIOTHERAPY", "CHEMOTHERAPY", "MEDICATION"])

    if "region" in lower:
        return random.choice(["NORTH", "SOUTH", "EAST", "WEST"])

    if "journal_entry_type" in lower:
        return random.choice(["PREMIUM", "CLAIM_RESERVE", "COMMISSION", "ADJUSTMENT"])

    # default string
    return faker.word().upper()


def _generate_rows_for_entity(
    entity_cfg: Dict[str, Any],
    business_keys_map: Dict[str, List[str]],
    fk_map: Dict[str, Dict[str, Tuple[str, str]]],
    key_registry: Dict[Tuple[str, str], List[Any]],
    faker: Faker,
) -> pd.DataFrame:
    """Generate base (valid) rows for a single entity, plus row category labels."""
    entity_name = entity_cfg["entity_name"]
    attributes = [a["attribute_name"] for a in entity_cfg.get("attributes", [])]
    total_rows = _row_counts_for_entity(entity_cfg)

    # Distribute row categories
    valid_rows = int(round(total_rows * 0.7))
    borderline_rows = int(round(total_rows * 0.15))
    invalid_rows = total_rows - valid_rows - borderline_rows

    categories: List[str] = ["VALID"] * valid_rows + ["BORDERLINE"] * borderline_rows + ["INVALID"] * invalid_rows
    random.shuffle(categories)

    entity_bks = set(business_keys_map.get(entity_name, []))
    entity_fk_map = fk_map.get(entity_name, {})

    rows: List[Dict[str, Any]] = []

    for i in range(total_rows):
        row: Dict[str, Any] = {}
        row_ctx: Dict[str, Any] = {}

        # Pre-handle known date pairs when present
        if "policy_issue_date" in attributes and "policy_maturity_date" in attributes:
            issue, maturity = _random_date_pair(faker)
            row_ctx["policy_issue_date"] = issue
            row_ctx["policy_maturity_date"] = maturity
        if "coverage_start_date" in attributes and "coverage_end_date" in attributes:
            start, end = _random_date_pair(faker)
            row_ctx["coverage_start_date"] = start
            row_ctx["coverage_end_date"] = end

        for attr in attributes:
            # Business key columns
            if attr in entity_bks:
                value = _generate_business_key_value(entity_name, attr, i, faker)
                row[attr] = value
                continue

            # Foreign keys based on manifest relationships
            if attr in entity_fk_map:
                parent_entity, parent_key = entity_fk_map[attr]
                parent_values = key_registry.get((parent_entity, parent_key)) or []
                if parent_values:
                    value = random.choice(parent_values)
                else:
                    # Fallback to synthetically generated identifier
                    value = _generate_business_key_value(parent_entity, parent_key, i, faker)
                row[attr] = value
                continue

            # Date pairs
            if attr in ("policy_issue_date", "policy_maturity_date", "coverage_start_date", "coverage_end_date") and attr in row_ctx:
                row[attr] = row_ctx[attr]
                continue

            # Reporting month field
            if attr == "reporting_month":
                year = random.choice([2023, 2024, 2025])
                month = random.randint(1, 12)
                row[attr] = f"{year}-{month:02d}"
                continue

            # Fallback generic attribute value
            row[attr] = _generate_generic_value(attr, faker, row_ctx)

        row["__row_category"] = categories[i]
        rows.append(row)

    df = pd.DataFrame(rows)

    # Register business keys for downstream FK sampling
    for bk in entity_bks:
        key_registry[(entity_name, bk)] = df[bk].tolist()

    return df


def inject_data_quality_issues(
    manifest: Dict[str, Any],
    dataframes: Dict[str, pd.DataFrame],
    fk_map: Dict[str, Dict[str, Tuple[str, str]]],
    key_registry: Dict[Tuple[str, str], List[Any]],
) -> Dict[str, Dict[str, Any]]:
    """Inject borderline and invalid data patterns for DQ and lineage testing.

    Returns per-entity error profile metadata for summary file.
    """
    error_profiles: Dict[str, Dict[str, Any]] = {}

    # Prepare helper for identifying business and foreign keys
    business_keys_map = _build_business_key_map(manifest)

    for file_cfg in manifest.get("files", []):
        entity_name = file_cfg["entity_name"]
        # Work on an object-typed copy so we can safely mix
        # numeric and string corruptions in the same column.
        df = dataframes[entity_name].astype("object").copy()
        dataframes[entity_name] = df
        bks = set(business_keys_map.get(entity_name, []))
        fks = set(fk_map.get(entity_name, {}).keys())

        injected_issue_types: set = set()
        semantic_tests: set = set()
        lineage_tests: set = set()

        # Work on a copy to avoid chained-assignment issues
        for idx, row in df.iterrows():
            category = row["__row_category"]

            if category == "VALID":
                # Leave valid rows untouched for clean referential integrity
                continue

            # Borderline rows: suspicious but mostly valid
            if category == "BORDERLINE":
                # Example: slightly malformed contact/email or outlier numeric
                for col in df.columns:
                    if col == "__row_category" or col in bks:
                        continue
                    lower = col.lower()

                    if "email" in lower and isinstance(row[col], str):
                        df.at[idx, col] = row[col].replace("@", ".")  # syntactically odd
                        injected_issue_types.add("borderline_email_format")
                        semantic_tests.add("contact_channel_quality")
                        break

                    if ("amount" in lower or "premium" in lower or "sum_assured" in lower) and isinstance(row[col], (int, float)):
                        df.at[idx, col] = row[col] * random.choice([0.1, 10])
                        injected_issue_types.add("borderline_outlier_amount")
                        semantic_tests.add("numeric_outlier")
                        break

                continue

            # INVALID rows: apply multiple strong corruptions
            if category == "INVALID":
                columns = [c for c in df.columns if c != "__row_category"]

                # 1) Broken foreign keys / orphan references
                for fk_col in fks:
                    if fk_col in columns and isinstance(row[fk_col], str):
                        df.at[idx, fk_col] = "i" + row[fk_col]
                        injected_issue_types.add("broken_foreign_key_i_prefixed")
                        lineage_tests.add("orphan_reference")
                        break

                # 2) Invalid status values and enumerations
                for col in columns:
                    lower = col.lower()
                    if "status" in lower and isinstance(row[col], str):
                        df.at[idx, col] = random.choice(["iACTIVE", "UNKNOWN_X", "INVALID_STATUS"])
                        injected_issue_types.add("invalid_status_value")
                        semantic_tests.add("invalid_enumeration")
                        break

                # 3) Malformed dates and impossible temporal logic
                for col in columns:
                    lower = col.lower()
                    if "date" in lower and isinstance(row[col], str):
                        # malformed date
                        df.at[idx, col] = random.choice(["2025-13-40", "1900-00-00"])
                        injected_issue_types.add("malformed_date")
                        semantic_tests.add("temporal_anomaly")
                        break

                # 4) String in numeric fields / negative amounts / >100 percentages
                for col in columns:
                    lower = col.lower()
                    val = row[col]
                    if ("amount" in lower or "premium" in lower or "sum_assured" in lower) and isinstance(val, (int, float)):
                        choice = random.choice(["string_in_numeric", "negative_amount"])
                        if choice == "string_in_numeric":
                            df.at[idx, col] = "i" + str(val)
                            injected_issue_types.add("string_in_numeric_field")
                        else:
                            df.at[idx, col] = -abs(val)
                            injected_issue_types.add("negative_amount")
                        semantic_tests.add("numeric_quality")
                        break
                    if "percentage" in lower and isinstance(val, (int, float)):
                        df.at[idx, col] = 150.0
                        injected_issue_types.add("percentage_over_100")
                        semantic_tests.add("range_violation")
                        break

                # 5) Duplicate identifiers with conflicting payload in transactional / reporting entities
                entity_layer = file_cfg.get("target_layer", "")
                if entity_layer in ("Transactional / Application Data Layer", "Analytical / Reporting Layer") and bks:
                    bk = list(bks)[0]
                    if isinstance(row[bk], str):
                        df.at[idx, bk] = df[bk].iloc[0]
                        injected_issue_types.add("duplicate_business_key")
                        lineage_tests.add("duplicate_identifier_conflict")

                # 6) Attribute-level corruption with i-prefix and cross-domain contamination
                for col in columns:
                    if col in bks or col in fks:
                        continue
                    if isinstance(df.at[idx, col], str):
                        df.at[idx, col] = "i" + str(df.at[idx, col])
                        injected_issue_types.add("attribute_i_prefix_corruption")
                        semantic_tests.add("semantic_corruption")
                        break

        total_rows = int(len(df))
        valid_rows = int((df["__row_category"] == "VALID").sum())
        borderline_rows = int((df["__row_category"] == "BORDERLINE").sum())
        invalid_rows = int((df["__row_category"] == "INVALID").sum())

        error_profiles[entity_name] = {
            "entity_name": entity_name,
            "total_rows": total_rows,
            "valid_rows": valid_rows,
            "borderline_rows": borderline_rows,
            "invalid_rows": invalid_rows,
            "injected_issue_types": sorted(list(injected_issue_types)),
            "business_keys_tested": business_keys_map.get(entity_name, []),
            "foreign_keys_tested": sorted(list(fks)),
            "semantic_domain_tests": sorted(list(semantic_tests)),
            "lineage_tests": sorted(list(lineage_tests)),
        }

    return error_profiles


def validate_relationships_for_valid_rows(
    manifest: Dict[str, Any], dataframes: Dict[str, pd.DataFrame]
) -> List[Dict[str, Any]]:
    """Validate referential integrity for rows marked as VALID only."""
    results: List[Dict[str, Any]] = []

    for rel in manifest.get("relationships", []):
        from_entity = rel["from_entity"]
        to_entity = rel["to_entity"]
        from_key = rel["from_key"]
        to_key = rel["to_key"]

        df_from = dataframes[from_entity]
        df_to = dataframes[to_entity]

        valid_from = df_from[df_from["__row_category"] == "VALID"]
        parent_keys = set(df_to[to_key].astype(str).tolist())
        missing = 0
        total = 0
        for _, row in valid_from.iterrows():
            val = str(row[from_key])
            if val is None or val == "" or val == "nan":
                continue
            total += 1
            if val not in parent_keys:
                missing += 1

        results.append(
            {
                "from_entity": from_entity,
                "to_entity": to_entity,
                "from_key": from_key,
                "to_key": to_key,
                "valid_rows_checked": total,
                "missing_parents": missing,
            }
        )

    return results


def write_csv_outputs(
    manifest: Dict[str, Any], dataframes: Dict[str, pd.DataFrame], output_root: Path
) -> None:
    """Write one CSV per entity to the appropriate layer folder."""
    for file_cfg in manifest.get("files", []):
        rel_path = file_cfg["relative_path"]
        entity_name = file_cfg["entity_name"]
        df = dataframes[entity_name].copy()
        # Drop helper column from physical output
        if "__row_category" in df.columns:
            df.drop(columns=["__row_category"], inplace=True)

        output_path = output_root / rel_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)


def generate_summary_file(
    manifest: Dict[str, Any],
    error_profiles: Dict[str, Dict[str, Any]],
    relationship_checks: List[Dict[str, Any]],
    output_root: Path,
    random_seed: int,
) -> None:
    """Write synthetic_data_generation_summary.json and a human-readable README.md."""
    summary = {
        "dataset_name": manifest.get("dataset_name"),
        "purpose": manifest.get("purpose"),
        "random_seed": random_seed,
        "row_count_configuration": LAYER_ROW_COUNTS,
        "entities": list(error_profiles.values()),
        "relationship_checks": relationship_checks,
    }

    summary_path = output_root / "synthetic_data_generation_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # README for consumers of the synthetic data
    readme_path = output_root / "README.md"
    lines: List[str] = []
    lines.append("# Synthetic Salesforce-Style Multi-Layer Dataset")
    lines.append("")
    lines.append("This folder contains synthetic CSV files generated from the manifest")
    lines.append(f"`{manifest.get('dataset_name')}` for data quality, lineage, and discovery testing.")
    lines.append("")
    lines.append("## Files and Row Counts")
    lines.append("")
    lines.append("| Entity | Relative Path | Total | Valid | Borderline | Invalid |")
    lines.append("|--------|---------------|-------|-------|------------|---------|")
    for file_cfg in manifest.get("files", []):
        entity_name = file_cfg["entity_name"]
        rel_path = file_cfg["relative_path"]
        prof = error_profiles[entity_name]
        lines.append(
            f"| {entity_name} | {rel_path} | {prof['total_rows']} | {prof['valid_rows']} | {prof['borderline_rows']} | {prof['invalid_rows']} |"
        )

    lines.append("")
    lines.append("## Relationship Logic")
    lines.append("")
    lines.append("The following referential relationships are enforced for VALID rows:")
    lines.append("")
    for rel in manifest.get("relationships", []):
        lines.append(
            f"- {rel['from_entity']}.{rel['from_key']} → {rel['to_entity']}.{rel['to_key']} ({rel['relationship_type']})"
        )

    lines.append("")
    lines.append("## Error Injection Strategy")
    lines.append("")
    lines.append("The generator creates three categories of rows per entity:")
    lines.append("- **VALID (≈70%)**: Fully consistent with business keys and relationships.")
    lines.append("- **BORDERLINE (≈15%)**: Suspicious but mostly consistent (e.g., odd emails, numeric outliers).")
    lines.append("- **INVALID (≈15%)**: Intentionally corrupted for DQ tests.")
    lines.append("")
    lines.append("Invalid patterns include:")
    lines.append("- Broken foreign keys with `i`-prefixed identifiers (orphan references).")
    lines.append("- Invalid enumerations like `iACTIVE` and `UNKNOWN_X`.")
    lines.append("- Malformed dates such as `2025-13-40` and impossible ranges.")
    lines.append("- Negative premium and amount values, and percentages > 100.")
    lines.append("- String values injected into numeric fields and vice versa.")
    lines.append("- Duplicate business keys in transactional/reporting entities with conflicting attributes.")
    lines.append("- Attribute-level `i`-prefix corruption to simulate semantic mismatches.")
    lines.append("")
    lines.append("## Usage for Testing")
    lines.append("")
    lines.append("- Use master and configuration entities as golden sources for keys and domain semantics.")
    lines.append("- Join transactional entities to master/configuration to validate foreign-key integrity and orphan detection.")
    lines.append("- Validate that reporting-layer aggregates reconcile with underlying detail rows for VALID records, and flag inconsistencies from INVALID rows.")
    lines.append("- Apply semantic classification and lineage tools to verify correct layer, LOB, and business-domain detection.")

    with readme_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _generate_all_data(manifest: Dict[str, Any], output_root: Path, random_seed: int = RANDOM_SEED) -> None:
    """Core orchestration: generate all entities across all layers."""
    random.seed(random_seed)
    faker = Faker()
    faker.seed_instance(random_seed)

    fk_map, _ = _build_relationship_maps(manifest)
    business_keys_map = _build_business_key_map(manifest)

    key_registry: Dict[Tuple[str, str], List[Any]] = {}
    dataframes: Dict[str, pd.DataFrame] = {}

    # Use topological order so that parent entities are available for FK sampling
    entity_order = _topological_entity_order(manifest)
    entity_cfg_by_name = {f["entity_name"]: f for f in manifest.get("files", [])}

    for entity_name in entity_order:
        cfg = entity_cfg_by_name[entity_name]
        df = _generate_rows_for_entity(cfg, business_keys_map, fk_map, key_registry, faker)
        dataframes[entity_name] = df

    # Inject data quality issues for BORDERLINE and INVALID rows
    error_profiles = inject_data_quality_issues(manifest, dataframes, fk_map, key_registry)

    # Relationship validation for VALID rows only
    relationship_checks = validate_relationships_for_valid_rows(manifest, dataframes)

    # Write out CSVs and summary artefacts
    write_csv_outputs(manifest, dataframes, output_root)
    generate_summary_file(manifest, error_profiles, relationship_checks, output_root, random_seed)


def generate_master_data(*args, **kwargs) -> None:
    """Kept for API completeness; core logic is in _generate_all_data."""
    # Master data is generated as part of the full pipeline.
    return None


def generate_configuration_data(*args, **kwargs) -> None:
    """Kept for API completeness; core logic is in _generate_all_data."""
    return None


def generate_transaction_data(*args, **kwargs) -> None:
    """Kept for API completeness; core logic is in _generate_all_data."""
    return None


def generate_reporting_data(*args, **kwargs) -> None:
    """Kept for API completeness; core logic is in _generate_all_data."""
    return None


def main() -> None:
    """Entry point: load manifest, generate synthetic data and summaries."""
    project_root = Path(__file__).resolve().parent.parent
    manifest_path = project_root / "data" / "salesforce_sample_layers_semantic_relational_manifest.json"
    output_root = project_root / "synthetic-data-generator" / "output"

    manifest = load_manifest(manifest_path)
    _generate_all_data(manifest, output_root, RANDOM_SEED)


if __name__ == "__main__":
    main()
