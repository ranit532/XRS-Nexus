import os
import json
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticSearch,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField
)
from openai import AzureOpenAI

# Configuration
SERVICE_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = "xrs-nexus-metadata-index"
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
EMBEDDING_DEPLOYMENT = "text-embedding-3-large"

def get_embeddings(text):
    client = AzureOpenAI(
        api_key=OPENAI_KEY,
        api_version="2024-02-01",
        azure_endpoint=OPENAI_ENDPOINT
    )
    response = client.embeddings.create(input=text, model=EMBEDDING_DEPLOYMENT)
    return response.data[0].embedding

def create_index():
    client = SearchIndexClient(SERVICE_ENDPOINT, AzureKeyCredential(KEY))
    
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchField(name="content", type=SearchFieldDataType.String, sortable=True, filterable=True, searchable=True),
        SearchField(name="embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), 
                    searchable=True, vector_search_dimensions=3072, vector_search_profile_name="myHnswProfile"),
        SimpleField(name="source", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="type", type=SearchFieldDataType.String, filterable=True, facetable=True)
    ]
    
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
        profiles=[VectorSearchProfile(name="myHnswProfile", algorithm_configuration_name="myHnsw")]
    )
    
    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            content_fields=[SemanticField(field_name="content")]
        )
    )
    
    semantic_search = SemanticSearch(configurations=[semantic_config])
    
    index = SearchIndex(
        name=INDEX_NAME, 
        fields=fields, 
        vector_search=vector_search, 
        semantic_search=semantic_search
    )
    
    client.create_or_update_index(index)
    print(f"Index {INDEX_NAME} created/updated.")

def index_data():
    search_client = SearchClient(SERVICE_ENDPOINT, INDEX_NAME, AzureKeyCredential(KEY))
    
    # Load synthetic data
    with open("data/metadata_samples.json", "r") as f:
        data = json.load(f)
        
    documents = []
    for item in data[:50]: # Indexing first 50 for demo
        content = f"{item['object_name']} - {item['description']} ({item['system_type']})"
        doc = {
            "id": item["id"],
            "content": content,
            "embedding": get_embeddings(content),
            "source": item["system_id"],
            "type": "metadata"
        }
        documents.append(doc)
        
    result = search_client.upload_documents(documents)
    print(f"Indexed {len(result)} documents.")

if __name__ == "__main__":
    # print("Run this script to create index and upload data.")
    # create_index()
    # index_data()
    pass
