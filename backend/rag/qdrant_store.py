from rag.embeddings import get_embedding
import uuid

COLLECTION_NAME = "recruitment_kb"
VECTOR_SIZE = 384
_documents = []

def create_collection():
    return COLLECTION_NAME

def reset_collection():
    _documents.clear()

def store_document(text, metadata=None):
    metadata = metadata or {}
    embedding = get_embedding(text)
    _documents.append({
        "id": str(uuid.uuid4()),
        "vector": embedding,
        "payload": {"text": text, **metadata},
    })

def search_documents(query, top_k=3):
    create_collection()
    query_embedding = get_embedding(query)
    ranked = sorted(
        _documents,
        key=lambda item: sum(a * b for a, b in zip(query_embedding, item["vector"])),
        reverse=True,
    )
    return [item["payload"] for item in ranked[:top_k] if item["payload"]]
