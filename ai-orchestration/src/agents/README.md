# AI Orchestration Agents

This directory contains Python implementations of the multi-agent orchestration layer for Azure AI Foundry.

## Agents

- **Metadata Intelligence Agent**: Ingests, validates, enriches, and standardizes source metadata into the canonical model.
- **Logical Flow Generator Agent**: Generates logical data flow graphs from canonical metadata.
- **ETL Strategy Agent**: Selects and parameterizes the optimal ETL/ELT strategy for the logical flow.
- **Runtime Telemetry Agent**: Monitors pipeline execution, collects metrics, and detects anomalies.
- **Lineage & Impact Analysis Agent**: Traces data lineage, assesses downstream impact, and exposes lineage as JSON.

Each agent exposes:
- `run(input_json)` method (input/output contracts as discussed)
- `prompt_template()` for LLM orchestration
- Built-in error/failure handling

See each agent's Python file for details and example usage.
