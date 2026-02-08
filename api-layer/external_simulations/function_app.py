import azure.functions as func
import logging
import json
import random

app = func.FunctionApp()

@app.route(route="external_metadata", auth_level=func.AuthLevel.ANONYMOUS)
def external_metadata(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('External Metadata API triggered.')
    
    # Simulate fetching external metadata
    mock_response = {
        "source": "ExternalVendor",
        "objects": [
            {"name": "Vendor_Invoices", "schema": "id, amount, date"},
            {"name": "Vendor_Payments", "schema": "id, status, timestamp"}
        ]
    }
    
    return func.HttpResponse(
        json.dumps(mock_response),
        mimetype="application/json",
        status_code=200
    )
