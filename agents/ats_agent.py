from ats.skill_extractor import extract_skills
from ats.ats_score import calculate_ats_score

def ats_agent(resume_text, jd_text):
    resume_skills = extract_skills(resume_text, source="resume")
    jd_skills = extract_skills(jd_text, source="job description")
    result = calculate_ats_score(resume_skills, jd_skills)
    return result
