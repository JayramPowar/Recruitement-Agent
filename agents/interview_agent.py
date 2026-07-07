from roadmap.roadmap_generator import generate_interview_questions

def interview_agent(resume_text, jd_text):
    questions = generate_interview_questions(resume_text, jd_text)
    return questions