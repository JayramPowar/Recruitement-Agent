from groq import Groq
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_cover_letter(resume_text, jd_text):
    prompt = f"""You are a senior career coach and professional cover letter writer who has helped candidates land offers at top tech companies. You specialize in translating resumes into cover letters that sound human, specific, and confident — never generic or templated.

## YOUR TASK
Write a compelling, personalized cover letter by connecting the candidate's actual experience (from the resume) to the specific requirements of the job description. Do not invent facts, metrics, or experience that are not present in the resume.

## INPUTS

<resume>
{resume_text}
</resume>

<job_description>
{jd_text}
</job_description>

## BEFORE YOU WRITE — ANALYZE FIRST
Silently identify:
1. The 3-4 most important requirements/skills the job description is asking for.
2. The strongest matching evidence from the resume for each of those requirements (specific projects, tools, achievements, or metrics — not generic claims).
3. One specific detail about the company or role (from the JD) that shows this isn't a mass-sent letter.

Use this analysis to guide the letter, but do not show your analysis in the output — output only the final letter.

## STRUCTURE (4 paragraphs)
1. **Opening hook** — State the role being applied for and one specific, genuine reason this role/company is a fit. Avoid generic openers like "I am writing to apply for..."
2. **Core fit** — Connect 2-3 concrete pieces of resume evidence (real projects, tools, outcomes) directly to the job's top requirements. Prioritize specificity over adjectives.
3. **Differentiator** — Highlight one thing that sets this candidate apart (a unique project, a rare skill combination, measurable impact) relevant to this specific role.
4. **Closing** — Confident, brief call to action. No begging, no clichés like "I would be a great asset."

## STRICT RULES
- Length: 250-300 words. Do not pad to hit the count.
- Tone: confident and professional, not stiff or robotic. Write like a skilled human, not an AI.
- Never fabricate companies, titles, metrics, or skills not present in the resume.
- Do NOT use these overused AI phrases: "I am excited to apply," "I believe I would be a great fit," "I am passionate about," "leverage my skills," "I am confident that," "dynamic," "proven track record," "team player."
- No placeholder brackets like [Company Name] — use the actual company/role name if present in the JD; if not present, phrase it generically without brackets (e.g., "your team" instead of "[Company Name]").
- Output ONLY the final cover letter text. No preamble, no notes, no markdown headers, no "Here is your cover letter:"."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
