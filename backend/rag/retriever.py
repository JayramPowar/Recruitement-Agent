from groq import Groq
import os
import re
from dotenv import load_dotenv
from pathlib import Path
from rag.qdrant_store import reset_collection, search_documents, store_document

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def chunk_text(text, source, max_words=120, overlap=30):
    words = re.findall(r"\S+", text or "")
    if not words:
        return []

    chunks = []
    step = max_words - overlap
    for start in range(0, len(words), step):
        chunk_words = words[start:start + max_words]
        if not chunk_words:
            continue
        chunks.append({
            "text": " ".join(chunk_words),
            "source": source,
            "chunk_index": len(chunks),
        })
    return chunks

def index_career_context(resume_text="", jd_text="", missing_skills=None):
    reset_collection()
    indexed = 0

    for chunk in chunk_text(resume_text, "resume"):
        store_document(chunk["text"], {"source": chunk["source"], "chunk_index": chunk["chunk_index"]})
        indexed += 1

    for chunk in chunk_text(jd_text, "job_description"):
        store_document(chunk["text"], {"source": chunk["source"], "chunk_index": chunk["chunk_index"]})
        indexed += 1

    skills = missing_skills or []
    if skills:
        store_document(
            "Missing skills from ATS analysis: " + ", ".join(skills),
            {"source": "ats_missing_skills", "chunk_index": 0}
        )
        indexed += 1

    return indexed

def ask_with_rag(question, resume_text="", jd_text="", missing_skills=None):
    indexed = index_career_context(resume_text, jd_text, missing_skills)
    chunks = search_documents(question, top_k=5)
    context = "\n\n".join(
        f"[{chunk.get('source', 'context')}] {chunk.get('text', '')}"
        for chunk in chunks
    )
    if not context.strip():
        context = "No indexed resume or job description context was available."

    prompt = f"""You are a helpful career assistant.
Answer the user's question using only the retrieved resume, job description, and ATS context below.
If the context does not contain enough information, say what is missing and give the best next step.
Context: {context}
Question: {question}
Answer:"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    return {
        "answer": response.choices[0].message.content.strip(),
        "sources": chunks,
        "indexed_chunks": indexed,
    }
