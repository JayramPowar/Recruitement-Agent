from sentence_transformers import SentenceTransformer, util
import re

model = SentenceTransformer("all-MiniLM-L6-v2")

def semantic_similarity(resume_text, jd_text):
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    jd_embedding = model.encode(jd_text, convert_to_tensor=True)
    similarity = util.cos_sim(resume_embedding, jd_embedding)
    return round(float(similarity) * 100, 2)

def extract_years_required(jd_text):
    patterns = [
        r'(\d+)\+?\s*years?\s*of\s*experience',
        r'(\d+)\+?\s*years?\s*experience',
        r'minimum\s*(\d+)\s*years?',
        r'at\s*least\s*(\d+)\s*years?',
    ]
    for pattern in patterns:
        match = re.search(pattern, jd_text.lower())
        if match:
            return int(match.group(1))
    return 0

def extract_years_in_resume(resume_text):
    patterns = [
        r'(\d+)\+?\s*years?\s*of\s*experience',
        r'(\d+)\+?\s*years?\s*experience',
        r'experience\s*of\s*(\d+)\s*years?',
    ]
    for pattern in patterns:
        match = re.search(pattern, resume_text.lower())
        if match:
            return int(match.group(1))
    return 0

def check_experience_match(resume_text, jd_text):
    required = extract_years_required(jd_text)
    available = extract_years_in_resume(resume_text)
    if required == 0:
        return 100, f"No specific experience requirement found in JD"
    if available >= required:
        return 100, f"✅ Required: {required}+ years | You have: {available} years"
    elif available > 0:
        score = round((available / required) * 100)
        return score, f"⚠️ Required: {required}+ years | You have: {available} years"
    else:
        return 50, f"ℹ️ Required: {required}+ years | Could not detect years in resume"

def check_education_match(resume_text, jd_text):
    education_levels = {
        "phd": 5, "doctorate": 5,
        "m.tech": 4, "mtech": 4, "m.e": 4, "masters": 4, "mba": 4, "msc": 4, "m.sc": 4,
        "b.tech": 3, "btech": 3, "b.e": 3, "bachelor": 3, "bsc": 3, "b.sc": 3, "degree": 3,
        "diploma": 2,
        "12th": 1, "hsc": 1, "intermediate": 1,
        "10th": 0, "ssc": 0,
    }
    jd_lower = jd_text.lower()
    resume_lower = resume_text.lower()

    jd_level = 0
    jd_edu = "Not specified"
    for edu, level in education_levels.items():
        if edu in jd_lower:
            if level > jd_level:
                jd_level = level
                jd_edu = edu.upper()

    resume_level = 0
    resume_edu = "Not found"
    for edu, level in education_levels.items():
        if edu in resume_lower:
            if level > resume_level:
                resume_level = level
                resume_edu = edu.upper()

    if jd_level == 0:
        return 100, "✅ No specific education requirement in JD"
    if resume_level >= jd_level:
        return 100, f"✅ Required: {jd_edu} | You have: {resume_edu}"
    else:
        return 50, f"⚠️ Required: {jd_edu} | You have: {resume_edu}"

def check_resume_format(resume_text):
    score = 100
    issues = []
    suggestions = []

    if len(resume_text) < 200:
        score -= 30
        issues.append("❌ Resume text too short — ATS may not read it properly")
        suggestions.append("Add more content to your resume")

    important_sections = ["experience", "education", "skills"]
    for section in important_sections:
        if section not in resume_text.lower():
            score -= 15
            issues.append(f"❌ Missing '{section.upper()}' section heading")
            suggestions.append(f"Add a clear '{section.upper()}' section")

    contact_indicators = ["@", "phone", "email", "linkedin", "github"]
    has_contact = any(c in resume_text.lower() for c in contact_indicators)
    if not has_contact:
        score -= 10
        issues.append("❌ No contact information detected")
        suggestions.append("Add email, phone, LinkedIn to your resume")

    if len(resume_text.split()) < 100:
        score -= 20
        issues.append("❌ Resume seems too short")
        suggestions.append("Expand your experience and skills sections")

    if not issues:
        issues.append("✅ Resume format looks good!")

    return max(score, 0), issues, suggestions

def calculate_ats_score(resume_skills, jd_skills, resume_text="", jd_text=""):
    resume_set = set([s.lower() for s in resume_skills])
    jd_set = set([s.lower() for s in jd_skills])

    matched = resume_set.intersection(jd_set)
    missing = jd_set - resume_set

    keyword_score = round((len(matched) / len(jd_set)) * 100) if jd_set else 0

    if resume_text and jd_text:
        semantic_score = semantic_similarity(resume_text, jd_text)
        experience_score, experience_msg = check_experience_match(resume_text, jd_text)
        education_score, education_msg = check_education_match(resume_text, jd_text)
        format_score, format_issues, format_suggestions = check_resume_format(resume_text)
    else:
        semantic_score = 0
        experience_score = 0
        experience_msg = "No data"
        education_score = 0
        education_msg = "No data"
        format_score = 0
        format_issues = []
        format_suggestions = []

    final_score = round(
        (keyword_score * 0.30) +
        (semantic_score * 0.30) +
        (experience_score * 0.20) +
        (education_score * 0.10) +
        (format_score * 0.10)
    )

    return {
        "ats_score": final_score,
        "keyword_score": keyword_score,
        "semantic_score": semantic_score,
        "experience_score": experience_score,
        "experience_msg": experience_msg,
        "education_score": education_score,
        "education_msg": education_msg,
        "format_score": format_score,
        "format_issues": format_issues,
        "format_suggestions": format_suggestions,
        "matched_skills": list(matched),
        "missing_skills": list(missing),
        "total_jd_skills": len(jd_set),
        "total_matched": len(matched)
    }

# def calculate_ats_score(resume_skills, jd_skills):
#     resume_set = set([s.lower() for s in resume_skills])
#     jd_set = set([s.lower() for s in jd_skills])
#     matched = resume_set.intersection(jd_set)
#     missing = jd_set - resume_set
#     score = round((len(matched) / len(jd_set)) * 100) if jd_set else 0
#     return {
#         "ats_score": score,
#         "matched_skills": list(matched),
#         "missing_skills": list(missing),
#         "total_jd_skills": len(jd_set),
#         "total_matched": len(matched)
#     }
