import logging
import json
import azure.functions as func

# Mock database - in production this would query Delta Lake via SQL Endpoint
MOCK_EXECUTION_DB = {
    "run_123": {
        "run_id": "run_123",
        "flow_id": "SAP_KNA1_CUSTOMER",
        "status": "RUNNING",
        "progress_percentage": 45,
        "current_stage": "TRANSFORM",
        "start_time": "2023-10-27T10:00:00Z",
        "sla_risk": "LOW",
        "error_details": None
    },
    "run_124": {
        "run_id": "run_124",
        "flow_id": "SFDC_OPPORTUNITY",
        "status": "FAILED",
        "progress_percentage": 20,
        "current_stage": "EXTRACT",
        "start_time": "2023-10-27T09:00:00Z",
        "sla_risk": "BREACHED",
        "error_details": "Connection timeout to Salesforce API"
    }
}

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    run_id = req.params.get('run_id')
    if not run_id:
        # Return all active runs summary
        return func.HttpResponse(
            json.dumps(list(MOCK_EXECUTION_DB.values())),
            mimetype="application/json",
            status_code=200
        )

    if run_id in MOCK_EXECUTION_DB:
        return func.HttpResponse(
            json.dumps(MOCK_EXECUTION_DB[run_id]),
            mimetype="application/json",
            status_code=200
        )
    else:
        return func.HttpResponse(
            "Run ID not found",
            status_code=404
        )
