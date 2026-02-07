import os
import json
import pytest
from agents.metadata_intelligence_agent import MetadataIntelligenceAgent
from agents.logical_flow_generator_agent import LogicalFlowGeneratorAgent
from agents.etl_strategy_agent import ETLStrategyAgent
from agents.runtime_telemetry_agent import RuntimeTelemetryAgent
from agents.lineage_impact_analysis_agent import LineageImpactAnalysisAgent

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '../../metadata-ingestion/src/canonical_metadata.schema.json')

# Example input for Metadata Intelligence Agent
def test_metadata_intelligence_agent_success():
    agent = MetadataIntelligenceAgent(SCHEMA_PATH)
    with open(os.path.join(os.path.dirname(__file__), '../../metadata-ingestion/src/example_sap_metadata.json')) as f:
        raw_metadata = json.load(f)
    input_json = {
        "sourceSystem": raw_metadata["sourceSystem"],
        "rawMetadata": raw_metadata
    }
    result = agent.run(input_json)
    assert result["validationStatus"] == "success"
    assert result["canonicalMetadata"] is not None

def test_logical_flow_generator_agent():
    agent = LogicalFlowGeneratorAgent()
    canonical_metadata = {"objectName": "TestTable"}
    input_json = {
        "canonicalMetadata": canonical_metadata,
        "targetSystem": {"type": "DataLake", "name": "OneLake"}
    }
    result = agent.run(input_json)
    assert result["status"] == "success"
    assert "nodes" in result["logicalFlow"]

def test_etl_strategy_agent():
    agent = ETLStrategyAgent()
    input_json = {
        "logicalFlow": {"nodes": [], "edges": []},
        "canonicalMetadata": {"objectName": "TestTable"},
        "constraints": {}
    }
    result = agent.run(input_json)
    assert result["status"] == "success"
    assert result["etlStrategy"]["mode"] == "batch"

def test_runtime_telemetry_agent():
    agent = RuntimeTelemetryAgent()
    input_json = {
        "pipelineId": "pipeline-123",
        "executionContext": {"startTime": "2024-01-01T00:00:00Z", "parameters": {}}
    }
    result = agent.run(input_json)
    assert "metrics" in result
    assert result["metrics"]["status"] == "success"

def test_lineage_impact_analysis_agent():
    agent = LineageImpactAnalysisAgent()
    input_json = {
        "pipelineId": "pipeline-123",
        "changeSet": {"type": "schema", "details": {}}
    }
    result = agent.run(input_json)
    assert result["status"] == "success"
    assert "lineageGraph" in result
