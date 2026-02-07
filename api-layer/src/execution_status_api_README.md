# Integration Execution Status API

This REST API exposes integration pipeline execution status for UI consumption.

## Endpoints

### GET /execution-status/{runId}
- Returns status, percent complete, current stage, errors, and stage details for a specific run.

#### Sample Response
```
{
  "pipelineId": "pipeline-123",
  "runId": "run-1707331200000",
  "status": "running",
  "percentComplete": 66,
  "currentStage": "load",
  "errors": [],
  "stages": {
    "extract": {"status": "completed", "startTime": 1707331200.0, "endTime": 1707331201.0},
    "transform": {"status": "completed", "startTime": 1707331201.0, "endTime": 1707331202.0},
    "load": {"status": "running", "startTime": 1707331202.0, "endTime": null}
  },
  "slaBreached": false,
  "estimatedTimeRemaining": 1
}
```

### GET /execution-status
- Returns a paginated, filterable list of historical pipeline runs.
- Supports filtering by pipelineId and status.
- Pagination via `limit` and `offset` query params.

#### Sample Response
```
{
  "total": 2,
  "runs": [
    {
      "pipelineId": "pipeline-123",
      "runId": "run-1707331200000",
      "status": "completed",
      "percentComplete": 100,
      "currentStage": null,
      "errors": [],
      "slaBreached": false,
      "startTime": 1707331200.0,
      "endTime": 1707331210.0
    },
    {
      "pipelineId": "pipeline-456",
      "runId": "run-1707331300000",
      "status": "failed",
      "percentComplete": 50,
      "currentStage": "transform",
      "errors": ["Transformation error"],
      "slaBreached": true,
      "startTime": 1707331300.0,
      "endTime": 1707331310.0
    }
  ]
}
```

## Pagination & Filtering
- Use `limit` and `offset` for pagination.
- Filter by `pipelineId` and `status`.
