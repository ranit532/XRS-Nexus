import os
import pytest
import json
from metadata_ingestion.src import ingest_service

EXAMPLE_SAP = os.path.join(os.path.dirname(__file__), '../src/example_sap_metadata.json')
EXAMPLE_SF = os.path.join(os.path.dirname(__file__), '../src/example_salesforce_metadata.json')


def test_valid_sap_metadata():
    with open(EXAMPLE_SAP) as f:
        metadata_json = f.read()
    result = ingest_service.ingest_metadata(metadata_json)
    assert result['status'] == 'success'
    assert 'version' in result

def test_valid_salesforce_metadata():
    with open(EXAMPLE_SF) as f:
        metadata_json = f.read()
    result = ingest_service.ingest_metadata(metadata_json)
    assert result['status'] == 'success'
    assert 'version' in result

def test_invalid_metadata():
    bad_metadata = '{"objectType": "table"}'  # missing required fields
    result = ingest_service.ingest_metadata(bad_metadata)
    assert result['status'] == 'error'
    assert 'validation' in result['message'].lower()
