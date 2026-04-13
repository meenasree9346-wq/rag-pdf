# src/retrieve.py

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import (
    VectorizedQuery,
    QueryType,
    QueryCaptionType,
    QueryAnswerType,
)
from azure.core.credentials import AzureKeyCredential

# ✅ Load .env before anything else
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)


def retrieve_docs(query):
    # ✅ Step 1: Embed the query (for vector search)
    query_embedding = client.embeddings.create(
        input=query,
        model=os.getenv("EMBEDDING_DEPLOYMENT")
    ).data[0].embedding

    # ✅ Step 2: Build vector query
    vector_query = VectorizedQuery(
        vector=query_embedding,
        k_nearest_neighbors=5,
        fields="embedding"
    )

    # ✅ Step 3: Hybrid search + semantic reranking
    results = search_client.search(
        search_text=query,                                  # keyword search (BM25)
        vector_queries=[vector_query],                      # vector search (HNSW)
        query_type=QueryType.SEMANTIC,                      # enable semantic reranking
        semantic_configuration_name="my-semantic-config",  # config we added
        query_caption=QueryCaptionType.EXTRACTIVE,          # extract key sentences
        query_answer=QueryAnswerType.EXTRACTIVE,            # extract direct answer
        select=["content", "source"],
        top=5
    )

    docs = [doc["content"] for doc in results]
    return docs