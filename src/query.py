# src/query.py

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI
from src.retrieve import retrieve_docs

# ✅ Load .env before anything else
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)


def ask_question(query):
    docs = retrieve_docs(query)

    context = "\n\n".join(docs)

    response = client.chat.completions.create(
        model=os.getenv("GPT_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": "Answer only from context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ],
        temperature=0
    )

    print("\n💡 Answer:\n")
    print(response.choices[0].message.content)