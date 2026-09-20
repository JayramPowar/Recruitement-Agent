from groq import Groq
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def resume_agent(resume_text):
    prompt = f"""You are an expert resume reviewer for software and AI roles.
Review the resume text carefully and return a concise but specific analysis in this exact format:
1. Overall strength: X/10
2. Score justification: one short sentence explaining the score based on clarity, relevance, achievements, formatting, and impact.
3. Key strengths: 3-5 specific strengths grounded in the resume content.
4. Weaknesses: 3-5 issues or gaps that are clearly visible in the resume.
5. Suggestions to improve: 3-5 practical, concrete recommendations directly tied to the resume.

Avoid generic praise. Use the resume text to identify actual examples. Do not invent details.

Resume:
{resume_text}"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
