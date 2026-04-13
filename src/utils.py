# src/utils.py

import os
import re
import numpy as np
from dotenv import load_dotenv
from pathlib import Path
from openai import AzureOpenAI

# ✅ Load .env
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# ✅ Azure OpenAI client for embedding sentences
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)


def clean_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_into_sentences(text):
    return re.split(r'(?<=[.!?]) +', text)


def get_embedding(text):
    """Embed a single piece of text using ada-002."""
    response = client.embeddings.create(
        input=text,
        model=os.getenv("EMBEDDING_DEPLOYMENT")
    )
    return np.array(response.data[0].embedding)


def cosine_similarity(a, b):
    """Measure how similar two embeddings are. 1 = identical, 0 = unrelated."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def chunk_text_semantic(text, threshold=0.7, max_sentences_per_chunk=10):
    """
    Semantic chunking strategy:
    1. Split text into sentences
    2. Embed each sentence individually
    3. Compare similarity between consecutive sentences
    4. When similarity drops below threshold, meaning has changed, cut chunk here
    5. Also cut if chunk gets too long (max_sentences_per_chunk)

    threshold: 0.7 means if two consecutive sentences are less than 70% similar,
               start a new chunk. Lower = more chunks. Higher = fewer bigger chunks.
    """
    sentences = split_into_sentences(text)

    if not sentences:
        return []

    print(f"    Embedding {len(sentences)} sentences for semantic chunking...")

    # ✅ Embed every sentence individually
    embeddings = []
    for sentence in sentences:
        if sentence.strip():
            emb = get_embedding(sentence.strip())
            embeddings.append(emb)
        else:
            embeddings.append(None)

    # ✅ Group sentences into chunks based on meaning similarity
    chunks = []
    current_chunk = [sentences[0]]

    for i in range(1, len(sentences)):
        if embeddings[i] is None or embeddings[i - 1] is None:
            current_chunk.append(sentences[i])
            continue

        # Measure similarity between current sentence and previous sentence
        similarity = cosine_similarity(embeddings[i], embeddings[i - 1])

        # If meaning drops significantly OR chunk is too long, start new chunk
        if similarity < threshold or len(current_chunk) >= max_sentences_per_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentences[i]]
        else:
            current_chunk.append(sentences[i])

    # ✅ Don't forget the last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# ✅ Keep old function as fallback (not used anymore but kept for reference)
def chunk_text_advanced(text, max_tokens=400, overlap=80):
    """Original sentence-aware chunking - kept as fallback."""
    import tiktoken
    tokenizer = tiktoken.get_encoding("cl100k_base")
    sentences = split_into_sentences(text)
    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        tokens = len(tokenizer.encode(sentence))
        if current_tokens + tokens > max_tokens:
            chunks.append(" ".join(current_chunk))
            overlap_chunk = []
            overlap_tokens = 0
            for s in reversed(current_chunk):
                t = len(tokenizer.encode(s))
                if overlap_tokens + t > overlap:
                    break
                overlap_chunk.insert(0, s)
                overlap_tokens += t
            current_chunk = overlap_chunk
            current_tokens = overlap_tokens
        current_chunk.append(sentence)
        current_tokens += tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks