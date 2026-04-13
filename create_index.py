import os
from pathlib import Path
from dotenv import load_dotenv
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)
from azure.core.credentials import AzureKeyCredential

load_dotenv(dotenv_path=Path(".env"))

index_client = SearchIndexClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)

try:
    index_client.delete_index(os.getenv("AZURE_SEARCH_INDEX"))
    print("Old index deleted.")
except:
    print("No existing index found.")

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
    SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
    SimpleField(name="source", type=SearchFieldDataType.String, filterable=True, sortable=True),
    SearchField(
        name="embedding",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=1536,
        vector_search_profile_name="myHnswProfile"
    ),
]

vector_search = VectorSearch(
    algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
    profiles=[VectorSearchProfile(name="myHnswProfile", algorithm_configuration_name="myHnsw")],
)

result = index_client.create_or_update_index(
    SearchIndex(
        name=os.getenv("AZURE_SEARCH_INDEX"),
        fields=fields,
        vector_search=vector_search
    )
)
print("Index created:", result.name)