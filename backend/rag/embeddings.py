import hashlib
import json
import math
import os
import re
from collections import Counter
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LOCAL_VECTOR_SIZE = 384
TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}")
HF_MODEL = os.getenv("HF_EMBEDDING_MODEL", DEFAULT_MODEL)
HF_TOKEN = (
    os.getenv("HF_TOKEN")
    or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    or os.getenv("HUGGINGFACE_API_TOKEN")
)
HF_EMBEDDING_FALLBACK = os.getenv("HF_EMBEDDING_FALLBACK", "local").lower()
HF_API_URL = os.getenv(
    "HF_EMBEDDING_API_URL",
    f"https://api-inference.huggingface.co/pipeline/feature-extraction/{quote(HF_MODEL, safe='/')}",
)


def _normalize(vector):
    magnitude = math.sqrt(sum(value * value for value in vector))
    if not magnitude:
        return vector
    return [value / magnitude for value in vector]


def _mean_pool(vectors):
    if not vectors:
        return []

    dimensions = len(vectors[0])
    pooled = []
    for index in range(dimensions):
        pooled.append(sum(vector[index] for vector in vectors) / len(vectors))
    return pooled


def _coerce_embedding(payload):
    if not isinstance(payload, list) or not payload:
        return []

    if all(isinstance(value, (int, float)) for value in payload):
        return [float(value) for value in payload]

    if all(isinstance(row, list) and row and all(isinstance(value, (int, float)) for value in row) for row in payload):
        return _mean_pool([[float(value) for value in row] for row in payload])

    if (
        len(payload) == 1
        and isinstance(payload[0], list)
        and payload[0]
        and all(isinstance(value, (int, float)) for value in payload[0])
    ):
        return [float(value) for value in payload[0]]

    return []


def _local_embedding(text):
    vector = [0.0] * LOCAL_VECTOR_SIZE
    counts = Counter(token.lower() for token in TOKEN_PATTERN.findall(text or ""))

    for token, count in counts.items():
        digest = hashlib.md5(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % LOCAL_VECTOR_SIZE
        sign = 1 if digest[4] % 2 == 0 else -1
        vector[index] += sign * count

    return _normalize(vector)


def get_embedding(text):
    if not text or not text.strip():
        return []
    if not HF_TOKEN:
        if HF_EMBEDDING_FALLBACK == "local":
            return _local_embedding(text)
        raise RuntimeError("Missing Hugging Face token. Set HF_TOKEN in backend/.env or Render environment variables.")

    body = json.dumps({
        "inputs": text,
        "options": {"wait_for_model": True},
    }).encode("utf-8")
    request = Request(
        HF_API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if exc.code in {500, 502, 503, 504} and HF_EMBEDDING_FALLBACK == "local":
            return _local_embedding(text)
        raise RuntimeError(f"Hugging Face embedding request failed with status {exc.code}: {detail}") from exc
    except URLError as exc:
        if HF_EMBEDDING_FALLBACK == "local":
            return _local_embedding(text)
        raise RuntimeError(f"Hugging Face embedding request failed: {exc.reason}") from exc

    embedding = _coerce_embedding(payload)
    if not embedding:
        raise RuntimeError("Hugging Face embedding response did not contain a usable vector.")
    return _normalize(embedding)
