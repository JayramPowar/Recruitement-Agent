import pdfplumber
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="D:/GenAI/AI-recruitement Copilot/AI-Recruitment-Copilot/.env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_skills(text, source="resume"):
    prompt = f"""You are an expert HR analyst.
Extract all technical skills from this {source} text.
Return ONLY a Python list like: ['Python', 'SQL', 'Docker']
No explanation. Just the list.

Text:
{text}"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content.strip()
    skills = eval(raw)
    return skills
