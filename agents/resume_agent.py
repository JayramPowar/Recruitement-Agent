from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="D:\GenAI\AI-recruitement Copilot\AI-Recruitment-Copilot\.env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def resume_agent(resume_text):
    prompt = f"""You are an expert resume reviewer.
Analyze this resume and provide:
1. Overall strength (out of 10)
2. Key strengths
3. Weaknesses
4. Suggestions to improve
Resume: {resume_text}"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
