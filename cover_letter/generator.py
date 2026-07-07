from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="D:\GenAI\AI-recruitement Copilot\AI-Recruitment-Copilot\.env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_cover_letter(resume_text, jd_text):
    prompt = f"""You are a professional cover letter writer.
Write a compelling cover letter based on this resume and job description.
Resume: {resume_text}
Job Description: {jd_text}
Write a professional cover letter under 300 words."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
