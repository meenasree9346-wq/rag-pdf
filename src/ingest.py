import os
import fitz
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

print("ENV CHECK:")
print("  AZURE_SEARCH_ENDPOINT :", repr(os.getenv("AZURE_SEARCH_ENDPOINT")))
print("  AZURE_SEARCH_INDEX    :", repr(os.getenv("AZURE_SEARCH_INDEX")))
print("  AZURE_SEARCH_KEY      :", repr(os.getenv("AZURE_SEARCH_KEY")))
print("  AZURE_OPENAI_ENDPOINT :", repr(os.getenv("AZURE_OPENAI_ENDPOINT")))
print("  EMBEDDING_DEPLOYMENT  :", repr(os.getenv("EMBEDDING_DEPLOYMENT")))

from src.blob_loader import load_pdfs_from_blob
from src.utils import clean_text, chunk_text_semantic

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


def ingest_from_blob():
    file_paths = load_pdfs_from_blob()
    docs = []
    doc_id = 0

    for file_path in file_paths:
        print(f"\n📄 Processing: {file_path}")

        pdf = fitz.open(file_path)
        text = ""
        for page in pdf:
            text += page.get_text()
        pdf.close()

        if not text.strip():
            print(f"  ⚠️  No text found in {file_path}, skipping.")
            continue

        text = clean_text(text)
        chunks = chunk_text_semantic(text)
        print(f"  Semantic chunks created: {len(chunks)}")

        for chunk in chunks:
            embedding = client.embeddings.create(
                input=chunk,
                model=os.getenv("EMBEDDING_DEPLOYMENT")
            ).data[0].embedding

            docs.append({
                "id": str(doc_id),
                "content": chunk,
                "source": os.path.basename(file_path),
                "embedding": embedding
            })
            doc_id += 1

    if not docs:
        print("No documents to upload.")
        return

    batch_size = 100
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i + batch_size]
        search_client.upload_documents(batch)
        print(f"  Uploaded batch {i // batch_size + 1} ({len(batch)} docs)")

    print(f"\nIngestion completed! Total chunks uploaded: {doc_id}")