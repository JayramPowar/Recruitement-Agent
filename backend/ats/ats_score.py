import math
import re
from collections import Counter
from functools import lru_cache

try:
    from rag.embeddings import get_embedding
except ImportError:
    from backend.rag.embeddings import get_embedding

TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}")
SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+")
LEADING_BULLET_PATTERN = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s*")
MAX_RESUME_CHUNKS = 24
MAX_JD_REQUIREMENTS = 18
RESUME_CHUNK_TOKENS = 120
RESUME_CHUNK_OVERLAP = 30
JD_CHUNK_TOKENS = 80
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have",
    "in", "into", "is", "it", "of", "on", "or", "our", "that", "the", "their", "this",
    "to", "with", "you", "your",
}
TECH_EXPANSIONS = [
    (r"\bai\b", "artificial intelligence"),
    (r"\bml\b", "machine learning"),
    (r"\bnlp\b", "natural language processing"),
    (r"\bcv\b", "computer vision"),
    (r"\bgenai\b", "generative ai"),
    (r"\bgen ai\b", "generative ai"),
    (r"\bjs\b", "javascript"),
    (r"\bts\b", "typescript"),
    (r"\bci/cd\b", "continuous integration continuous delivery"),
    (r"\bimage classification\b", "computer vision"),
    (r"\bobject detection\b", "computer vision"),
    (r"\bimage recognition\b", "computer vision"),
]
SKILL_CANONICAL_NAMES = {
    "ai": "AI",
    "ml": "Machine Learning",
    "llm": "LLM",
    "genai": "Generative AI",
    "nlp": "NLP",
    "cv": "Computer Vision",
    "rag": "RAG",
    "langchain": "LangChain",
}
SKILL_ALIASES = {
    "artificialintelligence": "ai",
    "aiml": "ml",
    "machinelearning": "ml",
    "largelanguagemodel": "llm",
    "largelanguagemodels": "llm",
    "llms": "llm",
    "generativeai": "genai",
    "genai": "genai",
    "naturalanguageprocessing": "nlp",
    "naturallanguageprocessing": "nlp",
    "computervision": "cv",
    "retrievalaugmentedgeneration": "rag",
    "rag": "rag",
    "langchain": "langchain",
}
RELATED_SKILL_KEYS = {
    "ai": {"ai", "ml", "llm", "genai", "rag"},
    "ml": {"ml", "ai"},
    "llm": {"llm", "genai", "ai"},
    "genai": {"genai", "llm", "ai", "rag"},
    "rag": {"rag", "llm", "genai"},
}
EMBEDDED_SKILL_PATTERNS = [
    (r"\bAI\s*/\s*ML\b", ["ai", "ml"]),
    (r"\bArtificial Intelligence\b", ["ai"]),
    (r"\bMachine Learning\b", ["ml"]),
    (r"\bML\b", ["ml"]),
    (r"\bAI\b", ["ai"]),
    (r"\bGenerative AI\b", ["genai"]),
    (r"\bGen\s*AI\b", ["genai"]),
    (r"\bGenAI\b", ["genai"]),
    (r"\bLarge Language Models?\b", ["llm"]),
    (r"\bLLMs?\b", ["llm"]),
    (r"\bRetrieval[-\s]+Augmented Generation\b", ["rag"]),
    (r"\bRAG\b", ["rag"]),
    (r"\bLangChain\b", ["langchain"]),
]


def _token_counts(text):
    return Counter(
        token.lower()
        for token in TOKEN_PATTERN.findall(_expand_common_terms(text))
        if token.lower() not in STOPWORDS
    )


def _expand_common_terms(text):
    expanded = text or ""
    for pattern, expansion in TECH_EXPANSIONS:
        expanded = re.sub(pattern, lambda match: f"{match.group(0)} {expansion}", expanded, flags=re.IGNORECASE)
    return expanded


def _compact_skill_key(skill):
    compacted = re.sub(r"[^a-z0-9+#]+", "", (skill or "").lower())
    if compacted.endswith("s") and compacted[:-1] in SKILL_ALIASES:
        compacted = compacted[:-1]
    return SKILL_ALIASES.get(compacted, compacted)


def _skill_match_keys(skill):
    normalized = re.sub(r"\s*/\s*", "/", (skill or "").strip().lower())
    parts = [
        part.strip()
        for part in re.split(r"/|,|\band\b", normalized)
        if part.strip()
    ]

    keys = {_compact_skill_key(normalized)}
    keys.update(_compact_skill_key(part) for part in parts)
    keys.update(_embedded_skill_keys(skill))
    return {key for key in keys if key}


def _embedded_skill_keys(skill):
    keys = []
    for pattern, pattern_keys in EMBEDDED_SKILL_PATTERNS:
        if re.search(pattern, skill or "", flags=re.IGNORECASE):
            keys.extend(pattern_keys)
    return keys


def _jd_skill_requirements(skill):
    embedded_keys = list(dict.fromkeys(_embedded_skill_keys(skill)))
    if len(embedded_keys) > 1:
        return [
            {
                "key": key,
                "display": SKILL_CANONICAL_NAMES.get(key, skill.strip()),
                "match_keys": {key},
            }
            for key in embedded_keys
        ]

    primary_key = _compact_skill_key(skill)
    return [
        {
            "key": primary_key,
            "display": _skill_display_name(skill, primary_key),
            "match_keys": _skill_match_keys(skill),
        }
    ]


def _skill_display_name(skill, key):
    return SKILL_CANONICAL_NAMES.get(key, (skill or key).strip())


def _build_skill_index(skills):
    index = {}
    for skill in skills:
        for key in _skill_match_keys(skill):
            index.setdefault(key, _skill_display_name(skill, key))
    return index


def _has_matching_skill(jd_keys, resume_keys):
    expanded_resume_keys = set(resume_keys)
    for key in resume_keys:
        expanded_resume_keys.update(RELATED_SKILL_KEYS.get(key, set()))

    for key in jd_keys:
        accepted_keys = {key}
        accepted_keys.update(RELATED_SKILL_KEYS.get(key, set()))
        if accepted_keys.intersection(expanded_resume_keys):
            return True
    return False


def _lexical_similarity(resume_text, jd_text):
    resume_counts = _token_counts(resume_text)
    jd_counts = _token_counts(jd_text)
    if not resume_counts or not jd_counts:
        return 0

    common_tokens = set(resume_counts).intersection(jd_counts)
    dot_product = sum(resume_counts[token] * jd_counts[token] for token in common_tokens)
    resume_magnitude = math.sqrt(sum(count * count for count in resume_counts.values()))
    jd_magnitude = math.sqrt(sum(count * count for count in jd_counts.values()))
    if not resume_magnitude or not jd_magnitude:
        return 0

    return round((dot_product / (resume_magnitude * jd_magnitude)) * 100, 2)


def _cosine_similarity(vector_a, vector_b):
    if not vector_a or not vector_b or len(vector_a) != len(vector_b):
        return 0

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = math.sqrt(sum(value * value for value in vector_a))
    magnitude_b = math.sqrt(sum(value * value for value in vector_b))
    if not magnitude_a or not magnitude_b:
        return 0

    return dot_product / (magnitude_a * magnitude_b)


@lru_cache(maxsize=256)
def _cached_embedding(text):
    return tuple(get_embedding(text))


def _tokenize(text):
    return TOKEN_PATTERN.findall(_expand_common_terms(text))


def _chunk_tokens(tokens, chunk_size, overlap):
    if not tokens:
        return []

    chunks = []
    step = max(chunk_size - overlap, 1)
    for start in range(0, len(tokens), step):
        chunk = tokens[start:start + chunk_size]
        if len(chunk) < 8 and chunks:
            break
        chunks.append(" ".join(chunk))
        if start + chunk_size >= len(tokens):
            break
    return chunks


def _chunk_text(text, chunk_size=RESUME_CHUNK_TOKENS, overlap=RESUME_CHUNK_OVERLAP, max_chunks=MAX_RESUME_CHUNKS):
    tokens = _tokenize(text)
    if not tokens:
        return []
    if len(tokens) <= chunk_size:
        return [" ".join(tokens)]
    return _chunk_tokens(tokens, chunk_size, overlap)[:max_chunks]


def _split_jd_requirements(jd_text):
    requirements = []
    blocks = [block.strip() for block in re.split(r"[\r\n]+", jd_text or "") if block.strip()]

    for block in blocks:
        block = LEADING_BULLET_PATTERN.sub("", block).strip()
        if not block:
            continue

        parts = SENTENCE_PATTERN.split(block)
        for part in parts:
            part = LEADING_BULLET_PATTERN.sub("", part).strip(" :-\t")
            tokens = _tokenize(part)
            if 4 <= len(tokens) <= JD_CHUNK_TOKENS:
                requirements.append(part)
            elif len(tokens) > JD_CHUNK_TOKENS:
                requirements.extend(_chunk_tokens(tokens, JD_CHUNK_TOKENS, 10))

    if not requirements:
        requirements = _chunk_text(jd_text, JD_CHUNK_TOKENS, 10, MAX_JD_REQUIREMENTS)

    return requirements[:MAX_JD_REQUIREMENTS]


def _embedding_similarity(resume_text, jd_text):
    resume_chunks = _chunk_text(resume_text)
    jd_requirements = _split_jd_requirements(jd_text)
    if not resume_chunks or not jd_requirements:
        return {
            "score": 0,
            "method": "embedding_chunked",
            "resume_chunks": len(resume_chunks),
            "jd_requirements": len(jd_requirements),
        }

    resume_vectors = []
    for chunk in resume_chunks:
        vector = _cached_embedding(chunk)
        if vector:
            resume_vectors.append(vector)

    if not resume_vectors:
        return {
            "score": 0,
            "method": "embedding_chunked",
            "resume_chunks": len(resume_chunks),
            "jd_requirements": len(jd_requirements),
        }

    best_scores = []
    for requirement in jd_requirements:
        requirement_vector = _cached_embedding(requirement)
        if not requirement_vector:
            continue

        best_match = max(_cosine_similarity(requirement_vector, resume_vector) for resume_vector in resume_vectors)
        best_scores.append(max(best_match, 0) * 100)

    if not best_scores:
        score = 0
    else:
        score = sum(best_scores) / len(best_scores)

    return {
        "score": round(score, 2),
        "method": "embedding_chunked",
        "resume_chunks": len(resume_chunks),
        "jd_requirements": len(jd_requirements),
    }


def semantic_similarity_details(resume_text, jd_text):
    try:
        return _embedding_similarity(resume_text, jd_text)
    except Exception:
        return {
            "score": _lexical_similarity(resume_text, jd_text),
            "method": "lexical_fallback",
            "resume_chunks": 0,
            "jd_requirements": 0,
        }


def semantic_similarity(resume_text, jd_text):
    return semantic_similarity_details(resume_text, jd_text)["score"]


def extract_years_required(jd_text):
    patterns = [
        r'(\d+)\+?\s*years?\s*of\s*experience',
        r'(\d+)\+?\s*years?\s*experience',
        r'minimum\s*(\d+)\s*years?',
        r'at\s*least\s*(\d+)\s*years?',
        r'(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?',
    ]
    for pattern in patterns:
        match = re.search(pattern, jd_text.lower())
        if match:
            return int(match.group(1))
    return 0

def extract_years_in_resume(resume_text):
    text = resume_text.lower()
    year_patterns = [
        r'(\d+(?:\.\d+)?)\+?\s*years?\s*of\s*experience',
        r'(\d+(?:\.\d+)?)\+?\s*years?\s*experience',
        r'experience\s*of\s*(\d+(?:\.\d+)?)\s*years?',
        r'(\d+(?:\.\d+)?)\+?\s*yrs?\s*of\s*experience',
        r'(\d+(?:\.\d+)?)\+?\s*yrs?\s*experience',
    ]
    month_patterns = [
        r'(\d+(?:\.\d+)?)\+?\s*months?\s*of\s*experience',
        r'(\d+(?:\.\d+)?)\+?\s*months?\s*experience',
        r'(\d+(?:\.\d+)?)\+?\s*month\s*internship',
    ]

    years = []
    for pattern in year_patterns:
        years.extend(float(match.group(1)) for match in re.finditer(pattern, text))
    for pattern in month_patterns:
        years.extend(float(match.group(1)) / 12 for match in re.finditer(pattern, text))

    if years:
        return max(years)

    internship_terms = ["internship", "intern ", "intern\n", "trainee", "apprentice"]
    if any(term in text for term in internship_terms):
        return 0.5

    fresher_terms = ["fresher", "entry level", "entry-level", "student"]
    if any(term in text for term in fresher_terms):
        return 0

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


def check_experience_match(resume_text, jd_text):
    required = extract_years_required(jd_text)
    available = extract_years_in_resume(resume_text)
    if required == 0:
        return 100, "No specific experience requirement found in JD"
    if available >= required:
        return 100, f"Required: {required}+ years | Detected: {available:g} years"
    if available > 0:
        score = min(round((available / required) * 100), 70)
        if available < 1:
            score = min(score, 15)
            return score, f"Required: {required}+ years | Resume appears to show internship-level experience (<1 year)"
        return score, f"Required: {required}+ years | Detected: {available:g} years"
    return 20, f"Required: {required}+ years | Could not detect professional years in resume"


def calculate_ats_score(resume_skills, jd_skills, resume_text="", jd_text=""):
    resume_index = _build_skill_index(resume_skills)
    resume_keys = set(resume_index)
    resume_keys.update(_embedded_skill_keys(resume_text))

    matched = []
    missing = []
    matched_keys = set()
    missing_keys = set()

    for jd_skill in jd_skills:
        for requirement in _jd_skill_requirements(jd_skill):
            primary_key = requirement["key"]
            if primary_key in matched_keys or primary_key in missing_keys:
                continue

            if _has_matching_skill(requirement["match_keys"], resume_keys):
                matched.append(requirement["display"])
                matched_keys.add(primary_key)
            else:
                missing.append(requirement["display"])
                missing_keys.add(primary_key)

    total_jd_skills = len(matched) + len(missing)
    keyword_score = round((len(matched) / total_jd_skills) * 100) if total_jd_skills else 0

    if resume_text and jd_text:
        semantic_details = semantic_similarity_details(resume_text, jd_text)
        semantic_score = semantic_details["score"]
        experience_score, experience_msg = check_experience_match(resume_text, jd_text)
        education_score, education_msg = check_education_match(resume_text, jd_text)
        format_score, format_issues, format_suggestions = check_resume_format(resume_text)
    else:
        semantic_details = {
            "method": "not_run",
            "resume_chunks": 0,
            "jd_requirements": 0,
        }
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
        "semantic_method": semantic_details["method"],
        "semantic_resume_chunks": semantic_details["resume_chunks"],
        "semantic_jd_requirements": semantic_details["jd_requirements"],
        "experience_score": experience_score,
        "experience_msg": experience_msg,
        "education_score": education_score,
        "education_msg": education_msg,
        "format_score": format_score,
        "format_issues": format_issues,
        "format_suggestions": format_suggestions,
        "matched_skills": matched,
        "missing_skills": missing,
        "total_jd_skills": total_jd_skills,
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
