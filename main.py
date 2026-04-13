from src.ingest import ingest_from_blob
from src.query import ask_question

# Run once
ingest_from_blob()

# Chat loop
while True:
    q = input("\nAsk: ")
    ask_question(q)