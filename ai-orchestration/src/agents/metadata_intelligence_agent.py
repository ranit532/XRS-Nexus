"""
Metadata Intelligence Agent
- Ingests, validates, enriches, and standardizes source metadata into the canonical model.
"""
import json
from jsonschema import validate, ValidationError

class MetadataIntelligenceAgent:
    def __init__(self, canonical_schema_path):
        with open(canonical_schema_path) as f:
            self.canonical_schema = json.load(f)

    def run(self, input_json):
        try:
            source_system = input_json['sourceSystem']
            raw_metadata = input_json['rawMetadata']
            # Example enrichment/standardization (identity for now)
            canonical_metadata = raw_metadata
            validate(instance=canonical_metadata, schema=self.canonical_schema)
            return {
                "canonicalMetadata": canonical_metadata,
                "validationStatus": "success",
                "errors": []
            }
        except ValidationError as e:
            return {
                "canonicalMetadata": None,
                "validationStatus": "error",
                "errors": [str(e)]
            }
        except Exception as e:
            return {
                "canonicalMetadata": None,
                "validationStatus": "error",
                "errors": [str(e)]
            }

    @staticmethod
    def prompt_template():
        return (
            "You are a metadata intelligence agent. Given the following raw metadata from a {sourceSystem.type} system, "
            "validate and transform it into the canonical metadata model. Report any validation errors."
        )
