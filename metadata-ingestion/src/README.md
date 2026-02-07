# Metadata Ingestion Service

This Python service ingests metadata from multiple source systems, validates it against the canonical schema, normalizes source-specific fields, stores it in Microsoft Fabric OneLake (Delta format), and versions metadata changes.

## Features
- Accepts JSON metadata from SAP, Salesforce, REST APIs, files, and streams
- Validates against canonical schema (`canonical_metadata.schema.json`)
- Normalizes source-specific fields (e.g., SAP uppercases columns)
- Stores metadata in Delta format (OneLake)
- Versions metadata with UUID and timestamp
- Error handling and validation reporting

## Example Usage

```python
from ingest_service import ingest_metadata

with open('example_sap_metadata.json') as f:
    metadata_json = f.read()
result = ingest_metadata(metadata_json)
print(result)
```

## Example Input
See `example_sap_metadata.json` and `example_salesforce_metadata.json`.

## Example Output
```json
{
  "status": "success",
  "version": "b1c2d3e4-..."
}
```

## Unit Tests
- `tests/test_ingest_service.py` covers valid/invalid input and error handling.

## Requirements
- Python 3.8+
- `jsonschema`, `pandas`, `deltalake`, `pytest`
