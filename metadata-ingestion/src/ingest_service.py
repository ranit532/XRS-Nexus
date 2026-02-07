import json
import os
from typing import Any, Dict
from jsonschema import validate, ValidationError
import pandas as pd
from deltalake.writer import write_deltalake
from datetime import datetime
import uuid

# Load canonical schema
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'canonical_metadata.schema.json')
with open(SCHEMA_PATH) as f:
    CANONICAL_SCHEMA = json.load(f)

# OneLake/Delta output path (simulate for local dev)
ONELAKE_PATH = os.environ.get('ONELAKE_PATH', './onelake_metadata_delta')


def validate_metadata(metadata: Dict[str, Any]) -> None:
    """Validate metadata against canonical schema."""
    try:
        validate(instance=metadata, schema=CANONICAL_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"Metadata validation error: {e.message}")


def normalize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize source-specific fields to canonical model."""
    # Example: normalize SAP field names to lower case, Salesforce to PascalCase, etc.
    if metadata['sourceSystem']['type'] == 'SAP':
        for col in metadata['schema']:
            col['columnName'] = col['columnName'].upper()
    elif metadata['sourceSystem']['type'] == 'Salesforce':
        for col in metadata['schema']:
            col['columnName'] = col['columnName'].capitalize()
    # Add more normalization as needed
    return metadata


def version_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Add versioning info to metadata."""
    metadata['version'] = str(uuid.uuid4())
    metadata['ingestedAt'] = datetime.utcnow().isoformat() + 'Z'
    return metadata


def store_metadata_delta(metadata: Dict[str, Any]) -> None:
    """Store metadata in Delta format (OneLake)."""
    df = pd.DataFrame([metadata])
    # Write to Delta Lake (append mode)
    write_deltalake(ONELAKE_PATH, df, mode="append")


def ingest_metadata(metadata_json: str) -> Dict[str, Any]:
    """Main ingestion function."""
    try:
        metadata = json.loads(metadata_json)
        validate_metadata(metadata)
        metadata = normalize_metadata(metadata)
        metadata = version_metadata(metadata)
        store_metadata_delta(metadata)
        return {"status": "success", "version": metadata['version']}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    # Example input (SAP)
    with open("example_sap_metadata.json") as f:
        example_input = f.read()
    result = ingest_metadata(example_input)
    print(json.dumps(result, indent=2))
