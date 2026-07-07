from groq import Groq
import os
from dotenv import load_dotenv
from rag.qdrant_store import search_documents

load_dotenv(dotenv_path="D:/GenAI/AI-recruitement Copilot/AI-Recruitment-Copilot/.env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_with_rag(question):
    chunks = search_documents(question, top_k=3)
    context = "\n\n".join(chunks)
    prompt = f"""You are a helpful career assistant.
Use the following context to answer the question.
Context: {context}
Question: {question}
Answer:"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
