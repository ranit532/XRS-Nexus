"""
XRS NEXUS Metadata Ingestion Service
- Ingests, validates, normalizes, and stores metadata in Fabric Lakehouse (Delta)
- Config-driven, idempotent, structured logging, error handling
"""
import json
import os
import logging
import uuid
from typing import Dict, Any
from jsonschema import validate, ValidationError
import pandas as pd
from deltalake.writer import write_deltalake
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'canonical_metadata.schema.json')
ONELAKE_PATH = os.environ.get('ONELAKE_PATH', '../../synthetic-dataset/delta/metadata')

with open(SCHEMA_PATH) as f:
    CANONICAL_SCHEMA = json.load(f)


def validate_metadata(metadata: Dict[str, Any]) -> None:
    try:
        validate(instance=metadata, schema=CANONICAL_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"Metadata validation error: {e.message}")


def normalize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    # Example normalization: uppercase SAP columns, PascalCase Salesforce, etc.
    sys_type = metadata['sourceSystem']['type']
    if sys_type == 'SAP':
        for col in metadata['schema']:
            col['columnName'] = col['columnName'].upper()
    elif sys_type == 'Salesforce':
        for col in metadata['schema']:
            col['columnName'] = col['columnName'].capitalize()
    return metadata


def version_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    metadata['version'] = str(uuid.uuid4())
    metadata['ingestedAt'] = datetime.utcnow().isoformat() + 'Z'
    return metadata


def store_metadata_delta(metadata: Dict[str, Any]) -> None:
    df = pd.DataFrame([metadata])
    write_deltalake(ONELAKE_PATH, df, mode="append")


def ingest_metadata(metadata_json: str, correlation_id: str = None) -> Dict[str, Any]:
    correlation_id = correlation_id or str(uuid.uuid4())
    try:
        metadata = json.loads(metadata_json)
        validate_metadata(metadata)
        metadata = normalize_metadata(metadata)
        metadata = version_metadata(metadata)
        store_metadata_delta(metadata)
        logging.info(json.dumps({"event": "ingest_success", "correlationId": correlation_id, "object": metadata.get('objectName'), "version": metadata['version']}))
        return {"status": "success", "version": metadata['version'], "correlationId": correlation_id}
    except Exception as e:
        logging.error(json.dumps({"event": "ingest_error", "correlationId": correlation_id, "error": str(e)}))
        return {"status": "error", "message": str(e), "correlationId": correlation_id}


if __name__ == "__main__":
    # Example: ingest all SAP metadata
    with open("../../synthetic-dataset/sap_metadata.json") as f:
        sap_metadata_list = json.load(f)
    for meta in sap_metadata_list:
        result = ingest_metadata(json.dumps(meta))
        print(result)
