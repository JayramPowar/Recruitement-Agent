from groq import Groq
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_roadmap(missing_skills):
    skills_list = ", ".join(missing_skills)
    prompt = f"""You are a senior technical mentor who has designed learning paths for engineers transitioning into new roles and technologies. You are known for roadmaps that are realistic, sequenced correctly, and grounded in real resources, not generic filler.

## YOUR TASK
Create a focused 30-day learning roadmap to help someone close these specific skill gaps: {skills_list}

## BEFORE YOU WRITE
Silently determine:
1. The logical learning order for these skills, including prerequisites.
2. How to spread the skills across 4 weeks based on difficulty and dependency.
3. One practical checkpoint or mini-project for each week.

Do not show this planning. Output only the final roadmap.

## REQUIRED OUTPUT FORMAT
Generate exactly 4 weekly sections and nothing else.

Week 1: [short week title]
Focus area: [what this week covers and why]
- [combined weekly activity]
- [combined weekly activity]
- [combined weekly activity]
- [combined weekly activity]
Project/checkpoint: [one concrete deliverable]

Week 2: [short week title]
Focus area: ...
- ...
- ...
- ...
- ...
Project/checkpoint: ...

Week 3: [short week title]
Focus area: ...
- ...
- ...
- ...
- ...
Project/checkpoint: ...

Week 4: [short week title]
Focus area: ...
- ...
- ...
- ...
- ...
Project/checkpoint: ...

## STRICT RULES
- Generate all 4 weeks in the response.
- Do not output Day 1, Day 2, daily schedules, or 28 separate day lines.
- Keep each week's bullets combined and week-level, not day-level.
- Each bullet must be concrete and actionable.
- Keep the roadmap practical for 1-2 hours per day.
- If two skills are naturally learned together, combine them in the same week.
- Do not add a preamble, closing summary, or markdown headings outside the 4 week blocks.
- Output ONLY the roadmap."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
    )
    return response.choices[0].message.content.strip()


def generate_interview_questions(resume_text, jd_text):
    prompt = f"""You are a senior hiring manager and technical interviewer who has conducted hundreds of interviews. You design interview questions that genuinely probe whether a candidate can do the job — not generic questions pulled from a textbook.

## YOUR TASK
Generate 10 interview questions tailored specifically to this candidate's resume and this job's requirements.

<resume>
{resume_text}
</resume>

<job_description>
{jd_text}
</job_description>

## BEFORE YOU WRITE — ANALYZE FIRST
Silently identify:
1. The top 3-4 technical requirements or skills the job description emphasizes most.
2. Specific projects, tools, or claims in the resume that a good interviewer would want to probe deeper on or verify (e.g., if the resume claims "built a RAG pipeline," a real interviewer asks about the specific design decisions, not "what is RAG?").
3. Any potential gaps or transitions in the resume relative to the JD (e.g., candidate is moving from a different domain, or the JD wants seniority the resume doesn't clearly demonstrate) that warrant a behavioral question.

Do not show this analysis — output only the final 10 questions.

## COMPOSITION
Generate exactly 10 questions:
- **6 technical questions**: Grounded in specifics from the resume (their actual projects/tools) cross-referenced against what the JD requires. Prefer questions that ask "how" and "why" over "what" (e.g., "Walk me through why you chose X over Y in [specific project]" rather than "Do you know X?").
- **3 behavioral questions**: Tied to real signals from the resume or JD (e.g., team size, ambiguous problems, conflicting priorities, ownership) — not generic ("Tell me about a time you worked in a team").
- **1 role-fit / motivation question**: Specific to why this candidate, with this background, wants this particular role — not a generic "why do you want this job."

## STRICT RULES
- Every question must reference something concrete from the resume or JD — no generic, could-apply-to-anyone questions.
- Do not ask questions the resume already answers plainly; probe deeper or into judgment/trade-offs instead.
- Keep each question to 1-2 sentences.
- Return as a numbered list, 1-10, with no category labels or section headers — just the questions in a natural mixed order (don't group all technical together then all behavioral).
- Output ONLY the numbered list. No preamble, no explanation, no "Here are 10 questions:"."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
