from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from rag.embeddings import get_embedding
import uuid

client = QdrantClient(":memory:")
COLLECTION_NAME = "recruitment_kb"

def create_collection():
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )

def store_document(text, metadata={}):
    embedding = get_embedding(text)
    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=embedding,
        payload={"text": text, **metadata}
    )
    client.upsert(collection_name=COLLECTION_NAME, points=[point])

def search_documents(query, top_k=3):
    embedding = get_embedding(query)
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        limit=top_k
    )
    return [r.payload["text"] for r in results]
