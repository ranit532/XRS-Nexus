# AI-driven Logical Flow Generator

This agent:
- Accepts normalized metadata as input
- Determines extraction, transformation, and load steps
- Identifies upstream and downstream dependencies
- Produces a baseline logical execution plan (technology-agnostic)

## Decision Rules
- **SAP CDC Load**: If source is SAP and CDC is enabled, use extract_cdc, transform, load_incremental
- **Salesforce Full Refresh**: If source is Salesforce and CDC is not enabled, use extract_full, transform, load_full
- **Default Full Load**: Fallback for all other cases

## Output Structure
```
{
  "nodes": [
    {"id": "extract", "type": "extract", "label": "Extract from ..."},
    {"id": "transform", "type": "transform", "label": "Transform to canonical model"},
    {"id": "load", "type": "load", "label": "Load to target"}
  ],
  "edges": [
    {"from": "extract", "to": "transform", "step": "transform"},
    {"from": "transform", "to": "load", "step": "load_full|load_incremental"}
  ],
  "upstreamDependencies": [ ... ],
  "downstreamDependencies": [ ... ],
  "decisionRule": "SAP CDC Load|Salesforce Full Refresh|Default Full Load"
}
```

## Example Flows

### SAP CDC Load
```
{
  "decisionRule": "SAP CDC Load",
  ...
}
```

### Salesforce Full Refresh
```
{
  "decisionRule": "Salesforce Full Refresh",
  ...
}
```
