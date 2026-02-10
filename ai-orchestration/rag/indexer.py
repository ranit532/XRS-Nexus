import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)

try:
    # Optional: only required for vector embeddings mode.
    from openai import AzureOpenAI
except Exception:  # pragma: no cover
    AzureOpenAI = None

# Configuration
SERVICE_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = "xrs-nexus-metadata-index"
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
EMBEDDING_DEPLOYMENT = "text-embedding-3-large"
RAG_MODE = (os.getenv("RAG_MODE") or "text").strip().lower()

def _repo_root() -> Path:
    # ai-orchestration/rag/indexer.py -> repo root is 2 levels up from ai-orchestration/
    return Path(__file__).resolve().parents[2]


def _load_metadata_samples() -> List[Dict[str, Any]]:
    # Prefer generated synthetic sample file, fall back to enterprise_metadata if needed.
    candidates = [
        _repo_root() / "data" / "metadata_samples.json",
        _repo_root() / "data" / "enterprise_metadata.json",
    ]
    for p in candidates:
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(f"No metadata JSON found. Tried: {', '.join(str(p) for p in candidates)}")


def get_embeddings(text: str) -> List[float]:
    if AzureOpenAI is None:
        raise RuntimeError("openai package not installed; cannot compute embeddings")
    if not OPENAI_ENDPOINT or not OPENAI_KEY:
        raise RuntimeError("AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_KEY not set; cannot compute embeddings")

    client = AzureOpenAI(api_key=OPENAI_KEY, api_version="2024-02-01", azure_endpoint=OPENAI_ENDPOINT)
    response = client.embeddings.create(input=text, model=EMBEDDING_DEPLOYMENT)
    return response.data[0].embedding

def create_index():
    client = SearchIndexClient(SERVICE_ENDPOINT, AzureKeyCredential(KEY))
    
    # Free-trial friendly default: TEXT mode (no vectors, no semantic config).
    # VECTOR mode requires a Search SKU that supports vector fields + OpenAI embeddings.
    fields: List[Any] = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchField(name="content", type=SearchFieldDataType.String, sortable=False, filterable=False, searchable=True),
        SimpleField(name="source", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="type", type=SearchFieldDataType.String, filterable=True, facetable=True),
    ]

    vector_search: Optional[VectorSearch] = None

    if RAG_MODE == "vector":
        fields.append(
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=3072,
                vector_search_profile_name="myHnswProfile",
            )
        )
        vector_search = VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
            profiles=[VectorSearchProfile(name="myHnswProfile", algorithm_configuration_name="myHnsw")],
        )
    
    index = SearchIndex(
        name=INDEX_NAME, 
        fields=fields, 
        vector_search=vector_search,
    )
    
    client.create_or_update_index(index)
    print(f"Index {INDEX_NAME} created/updated (mode={RAG_MODE}).")

def index_data():
    search_client = SearchClient(SERVICE_ENDPOINT, INDEX_NAME, AzureKeyCredential(KEY))
    
    data = _load_metadata_samples()
        
    documents = []
    for item in data[:50]: # Indexing first 50 for demo
        content = f"{item['object_name']} - {item['description']} ({item['system_type']})"
        doc = {
            "id": item["id"],
            "content": content,
            "source": item["system_id"],
            "type": "metadata"
        }
        if RAG_MODE == "vector":
            doc["embedding"] = get_embeddings(content)
        documents.append(doc)
        
    result = search_client.upload_documents(documents)
    print(f"Indexed {len(result)} documents.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="XRS Nexus metadata indexer for Azure AI Search.")
    parser.add_argument("--create-index", action="store_true", help="Create or update the search index.")
    parser.add_argument("--index-data", action="store_true", help="Upload sample metadata documents to the index.")
    args = parser.parse_args()

    if not SERVICE_ENDPOINT or not KEY:
        raise SystemExit("Missing AZURE_SEARCH_ENDPOINT / AZURE_SEARCH_KEY environment variables.")

    if not args.create_index and not args.index_data:
        parser.print_help()
        raise SystemExit(2)

    if args.create_index:
        create_index()
    if args.index_data:
        index_data()
