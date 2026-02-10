import json
import logging
import os
from typing import Any, Dict, List, Optional

import azure.functions as func

try:
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient
except Exception:  # pragma: no cover
    # Allows local import even if deps aren't installed yet.
    AzureKeyCredential = None
    SearchClient = None


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


# ---------------------------------------------------------------------
# Mock execution status API (free-tier friendly, no external deps)
# ---------------------------------------------------------------------
MOCK_EXECUTION_DB: Dict[str, Dict[str, Any]] = {
    "run_123": {
        "run_id": "run_123",
        "flow_id": "SAP_KNA1_CUSTOMER",
        "status": "RUNNING",
        "progress_percentage": 45,
        "current_stage": "TRANSFORM",
        "start_time": "2023-10-27T10:00:00Z",
        "sla_risk": "LOW",
        "error_details": None,
    },
    "run_124": {
        "run_id": "run_124",
        "flow_id": "SFDC_OPPORTUNITY",
        "status": "FAILED",
        "progress_percentage": 20,
        "current_stage": "EXTRACT",
        "start_time": "2023-10-27T09:00:00Z",
        "sla_risk": "BREACHED",
        "error_details": "Connection timeout to Salesforce API",
    },
}


@app.route(route="health")
def health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({"ok": True}),
        mimetype="application/json",
        status_code=200,
    )


@app.route(route="execution-status")
def execution_status_list(req: func.HttpRequest) -> func.HttpResponse:
    # NOTE: simplified demo response; real impl would query Fabric / OneLake.
    return func.HttpResponse(
        json.dumps(list(MOCK_EXECUTION_DB.values())),
        mimetype="application/json",
        status_code=200,
    )


@app.route(route="execution-status/{runId}")
def execution_status_get(req: func.HttpRequest) -> func.HttpResponse:
    run_id = req.route_params.get("runId")
    if not run_id:
        return func.HttpResponse("Missing runId", status_code=400)

    payload = MOCK_EXECUTION_DB.get(run_id)
    if not payload:
        return func.HttpResponse("Run ID not found", status_code=404)

    return func.HttpResponse(
        json.dumps(payload),
        mimetype="application/json",
        status_code=200,
    )


# ---------------------------------------------------------------------
# External metadata simulation endpoint
# ---------------------------------------------------------------------
@app.route(route="external_metadata")
def external_metadata(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("External Metadata API triggered.")
    mock_response = {
        "source": "ExternalVendor",
        "objects": [
            {"name": "Vendor_Invoices", "schema": "id, amount, date"},
            {"name": "Vendor_Payments", "schema": "id, status, timestamp"},
        ],
    }
    return func.HttpResponse(
        json.dumps(mock_response),
        mimetype="application/json",
        status_code=200,
    )


# ---------------------------------------------------------------------
# Azure AI Search (text-mode) lookup endpoint
# Works on free tiers that support basic text search.
# ---------------------------------------------------------------------
def _get_search_client() -> Optional["SearchClient"]:
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT") or ""
    key = os.getenv("AZURE_SEARCH_KEY") or ""
    if not endpoint or not key or SearchClient is None or AzureKeyCredential is None:
        return None
    return SearchClient(endpoint=endpoint, index_name="xrs-nexus-metadata-index", credential=AzureKeyCredential(key))


@app.route(route="rag/lookup")
def rag_lookup(req: func.HttpRequest) -> func.HttpResponse:
    q = (req.params.get("q") or "").strip()
    if not q:
        return func.HttpResponse("Missing query param 'q'", status_code=400)

    rag_mode = (os.getenv("RAG_MODE") or "text").strip().lower()
    if rag_mode not in {"text", "vector", "mock"}:
        rag_mode = "text"

    # For free-trial safety, we default to text mode. Vector mode is allowed
    # only if your Search SKU supports vector fields and you've indexed vectors.
    client = _get_search_client() if rag_mode in {"text", "vector"} else None

    # deterministic fallback: small built-in knowledge used when Search is
    # unavailable or doesn't return any hits. This keeps the README's
    # KUNNR example working even on fresh/demo data.
    mock_knowledge = {
        "KUNNR": "Mapped to CustomerID in CRM",
        "MATNR": "Mapped to MaterialID in ERP",
        "BUKRS": "Mapped to CompanyCode in Finance",
    }

    if client is None:
        return func.HttpResponse(
            json.dumps({"mode": "mock", "query": q, "answer": mock_knowledge.get(q, "No historical mapping found.")}),
            mimetype="application/json",
            status_code=200,
        )

    try:
        results: List[Dict[str, Any]] = []
        for r in client.search(search_text=q, top=5):
            results.append(
                {
                    "id": r.get("id"),
                    "content": r.get("content"),
                    "source": r.get("source"),
                    "type": r.get("type"),
                }
            )

        if not results:
            # no hits in Search; fall back to mock mapping
            return func.HttpResponse(
                json.dumps({"mode": "mock", "query": q, "answer": mock_knowledge.get(q, "No historical mapping found.")}),
                mimetype="application/json",
                status_code=200,
            )

        return func.HttpResponse(
            json.dumps({"mode": rag_mode, "query": q, "results": results}),
            mimetype="application/json",
            status_code=200,
        )
    except Exception as e:
        logging.exception("Search lookup failed")
        return func.HttpResponse(
            json.dumps({"mode": rag_mode, "query": q, "error": str(e)}),
            mimetype="application/json",
            status_code=500,
        )

