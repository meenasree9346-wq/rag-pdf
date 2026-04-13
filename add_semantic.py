# add_semantic.py
# Run this ONCE to add semantic reranking to your existing index.
# Usage: python add_semantic.py

import os
from pathlib import Path
from dotenv import load_dotenv
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)
from azure.core.credentials import AzureKeyCredential

load_dotenv(dotenv_path=Path(".env"))

index_client = SearchIndexClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)

# ✅ Get existing index
index = index_client.get_index(os.getenv("AZURE_SEARCH_INDEX"))

# ✅ Add semantic configuration
index.semantic_search = SemanticSearch(
    configurations=[
        SemanticConfiguration(
            name="my-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="content")]
            )
        )
    ]
)

# ✅ Update the index
result = index_client.create_or_update_index(index)
print(f"✅ Semantic configuration added to index: {result.name}")