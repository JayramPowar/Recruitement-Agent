from groq import Groq
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def router_agent(user_query, resume_text="", jd_text="", missing_skills=[]):
    prompt = f"""You are a router. Based on the user query, decide which agent to call.
Return ONLY one of these words: resume_agent, ats_agent, interview_agent, career_agent
User Query: {user_query}"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    agent_name = response.choices[0].message.content.strip().lower()

    if agent_name == "resume_agent":
        from agents.resume_agent import resume_agent
        return resume_agent(resume_text)
    elif agent_name == "ats_agent":
        from agents.ats_agent import ats_agent
        return ats_agent(resume_text, jd_text)
    elif agent_name == "interview_agent":
        from agents.interview_agent import interview_agent
        return interview_agent(resume_text, jd_text)
    elif agent_name == "career_agent":
        from agents.career_agent import career_agent
        return career_agent(missing_skills)
    else:
        return "Sorry, I could not understand your request."
