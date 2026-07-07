from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="D:\GenAI\AI-recruitement Copilot\AI-Recruitment-Copilot\.env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_roadmap(missing_skills):
    skills_list = ", ".join(missing_skills)
    prompt = f"""You are a career coach.
Create a 30-day learning roadmap to learn: {skills_list}
Format week by week:
Week 1: ...
Week 2: ...
Week 3: ...
Week 4: ..."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def generate_interview_questions(resume_text, jd_text):
    prompt = f"""You are an expert interviewer.
Generate 10 interview questions based on this resume and job description.
Mix technical and behavioral questions.
Resume: {resume_text}
Job Description: {jd_text}
Return as a numbered list."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
