from promptflow import tool
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import os

@tool
def rag_lookup(query: str):
    # Free-trial friendly behavior:
    # - If AI Search is configured, use TEXT search against the demo index.
    # - Otherwise fall back to a small deterministic in-code mapping.
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT") or ""
    key = os.getenv("AZURE_SEARCH_KEY") or ""
    rag_mode = (os.getenv("RAG_MODE") or "text").strip().lower()

    if endpoint and key and rag_mode in {"text", "vector"}:
        try:
            client = SearchClient(endpoint=endpoint, index_name="xrs-nexus-metadata-index", credential=AzureKeyCredential(key))
            results = list(client.search(search_text=query, top=3))
            if results:
                # Return the best matching content snippet
                return results[0].get("content") or "Found match but no content field."
        except Exception:
            # Fall through to mock mapping if Search isn't reachable / index not created yet.
            pass

    mock_knowledge = {
        "KUNNR": "Mapped to CustomerID in CRM",
        "MATNR": "Mapped to MaterialID in ERP",
        "BUKRS": "Mapped to CompanyCode in Finance"
    }
    return mock_knowledge.get(query, "No historical mapping found.")
