import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from agents.resume_agent import resume_agent
from agents.router_agent import router_agent
from ats.ats_score import calculate_ats_score
from ats.skill_extractor import extract_skills, extract_text_from_pdf
from cold_email.sender import generate_email_body, load_recruiters, send_cold_emails
from cover_letter.generator import generate_cover_letter
from roadmap.roadmap_generator import generate_interview_questions, generate_roadmap

UPLOAD_DIR = ROOT_DIR / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="AI Recruitment Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextPayload(BaseModel):
    resume_text: str
    jd_text: str


class ResumePayload(BaseModel):
    resume_text: str


class RoadmapPayload(BaseModel):
    missing_skills: list[str]


class ChatPayload(BaseModel):
    query: str
    resume_text: str = ""
    jd_text: str = ""
    missing_skills: list[str] = []


class ColdEmailSendPayload(BaseModel):
    sender_email: str
    app_password: str
    resume_skills: list[str] = []
    delay: int = 30


def _save_upload(upload: UploadFile, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return destination


def _read_text_upload(upload: UploadFile) -> str:
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix == ".pdf":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(upload.file, tmp)
            temp_path = tmp.name
        try:
            return extract_text_from_pdf(temp_path).strip()
        finally:
            os.unlink(temp_path)

    raw = upload.file.read()
    try:
        return raw.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="JD file must be PDF or UTF-8 text.") from exc


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/upload/resume")
def upload_resume(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF resume.")

    resume_path = _save_upload(file, UPLOAD_DIR / "resume.pdf")
    resume_text = extract_text_from_pdf(str(resume_path)).strip()
    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract readable text from this resume.")

    return {
        "filename": file.filename,
        "resume_text": resume_text,
        "word_count": len(resume_text.split()),
    }


@app.post("/api/upload/jd")
def upload_jd(
    file: Optional[UploadFile] = File(default=None),
    jd_text: Optional[str] = Form(default=None),
):
    text = ""
    filename = None
    if file and file.filename:
        filename = file.filename
        text = _read_text_upload(file)
    elif jd_text:
        text = jd_text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="Please upload or paste a job description.")

    (UPLOAD_DIR / "job_description.txt").write_text(text, encoding="utf-8")
    return {
        "filename": filename,
        "jd_text": text,
        "word_count": len(text.split()),
    }


@app.post("/api/ats")
def run_ats(payload: TextPayload):
    resume_skills = extract_skills(payload.resume_text, "resume")
    jd_skills = extract_skills(payload.jd_text, "job description")
    result = calculate_ats_score(
        resume_skills,
        jd_skills,
        resume_text=payload.resume_text,
        jd_text=payload.jd_text,
    )
    return {"result": result, "resume_skills": resume_skills, "jd_skills": jd_skills}


@app.post("/api/resume-analysis")
def analyze_resume(payload: ResumePayload):
    return {"analysis": resume_agent(payload.resume_text)}


@app.post("/api/cover-letter")
def cover_letter(payload: TextPayload):
    return {"cover_letter": generate_cover_letter(payload.resume_text, payload.jd_text)}


@app.post("/api/interview-questions")
def interview_questions(payload: TextPayload):
    return {"questions": generate_interview_questions(payload.resume_text, payload.jd_text)}


@app.post("/api/roadmap")
def roadmap(payload: RoadmapPayload):
    return {"roadmap": generate_roadmap(payload.missing_skills)}


@app.post("/api/chat")
def chat(payload: ChatPayload):
    return {
        "answer": router_agent(
            payload.query,
            resume_text=payload.resume_text,
            jd_text=payload.jd_text,
            missing_skills=payload.missing_skills,
        )
    }


@app.post("/api/cold-email/preview")
def cold_email_preview(file: UploadFile = File(...), resume_skills: str = Form(default="")):
    recruiters_path = _save_upload(file, UPLOAD_DIR / "recruiters.xlsx")
    df = load_recruiters(str(recruiters_path))
    recruiters = df[["Company Name", "HR / Contact Person", "Email ID"]].to_dict("records")
    skills = [skill.strip() for skill in resume_skills.split(",") if skill.strip()]
    sample = recruiters[0] if recruiters else None
    preview = ""
    if sample:
        preview = generate_email_body(sample["HR / Contact Person"], sample["Company Name"], skills)
    return {"count": len(recruiters), "recruiters": recruiters, "preview": preview}


@app.post("/api/cold-email/send")
def cold_email_send(payload: ColdEmailSendPayload):
    resume_path = UPLOAD_DIR / "resume.pdf"
    recruiters_path = UPLOAD_DIR / "recruiters.xlsx"
    if not resume_path.exists() or not recruiters_path.exists():
        raise HTTPException(status_code=400, detail="Upload a resume and recruiter Excel file first.")

    results, total = send_cold_emails(
        str(recruiters_path),
        str(resume_path),
        payload.sender_email,
        payload.app_password,
        payload.resume_skills,
        payload.delay,
    )
    return {"results": results, "total": total}
