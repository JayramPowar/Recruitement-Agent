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
from ats.ats_score import calculate_ats_score
from ats.skill_extractor import extract_skills, extract_text_from_pdf
from cold_email.sender import generate_email_body, load_recruiters, send_cold_emails
from cover_letter.generator import generate_cover_letter
from rag.retriever import ask_with_rag
from roadmap.roadmap_generator import generate_interview_questions, generate_roadmap

UPLOAD_DIR = ROOT_DIR / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESUME_TEXT_PATH = UPLOAD_DIR / "resume.txt"
JD_TEXT_PATH = UPLOAD_DIR / "job_description.txt"

app = FastAPI(title="AI Recruitment Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
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


def _read_cached_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/upload/resume")
def upload_resume(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF resume.")

    try:
        resume_path = _save_upload(file, UPLOAD_DIR / "resume.pdf")
        resume_text = extract_text_from_pdf(str(resume_path)).strip()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Resume upload failed: {exc}") from exc

    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract readable text from this resume.")

    RESUME_TEXT_PATH.write_text(resume_text, encoding="utf-8")
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
    try:
        text = ""
        filename = None
        if file and file.filename:
            filename = file.filename
            text = _read_text_upload(file)
        elif jd_text:
            text = jd_text.strip()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Job description upload failed: {exc}") from exc

    if not text:
        raise HTTPException(status_code=400, detail="Please upload or paste a job description.")

    JD_TEXT_PATH.write_text(text, encoding="utf-8")
    return {
        "filename": filename,
        "jd_text": text,
        "word_count": len(text.split()),
    }


@app.post("/api/ats")
def run_ats(payload: TextPayload):
    if not payload.resume_text.strip() or not payload.jd_text.strip():
        raise HTTPException(status_code=400, detail="Resume and job description are required.")

    try:
        resume_skills = extract_skills(payload.resume_text, "resume")
        jd_skills = extract_skills(payload.jd_text, "job description")
        result = calculate_ats_score(
            resume_skills,
            jd_skills,
            resume_text=payload.resume_text,
            jd_text=payload.jd_text,
        )
        return {"result": result, "resume_skills": resume_skills, "jd_skills": jd_skills}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"ATS analysis failed: {exc}") from exc


@app.post("/api/resume-analysis")
def analyze_resume(payload: ResumePayload):
    if not payload.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is required.")

    try:
        return {"analysis": resume_agent(payload.resume_text)}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Resume analysis failed: {exc}") from exc


@app.post("/api/cover-letter")
def cover_letter(payload: TextPayload):
    if not payload.resume_text.strip() or not payload.jd_text.strip():
        raise HTTPException(status_code=400, detail="Resume and job description are required.")

    try:
        return {"cover_letter": generate_cover_letter(payload.resume_text, payload.jd_text)}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Cover letter generation failed: {exc}") from exc


@app.post("/api/interview-questions")
def interview_questions(payload: TextPayload):
    if not payload.resume_text.strip() or not payload.jd_text.strip():
        raise HTTPException(status_code=400, detail="Resume and job description are required.")

    try:
        return {"questions": generate_interview_questions(payload.resume_text, payload.jd_text)}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Interview question generation failed: {exc}") from exc


@app.post("/api/roadmap")
def roadmap(payload: RoadmapPayload):
    skills = [skill.strip() for skill in payload.missing_skills if skill and skill.strip()]
    if not skills:
        raise HTTPException(status_code=400, detail="Missing skills are required to generate a roadmap.")

    try:
        return {"roadmap": generate_roadmap(skills)}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Roadmap generation failed: {exc}") from exc


@app.post("/api/chat")
def chat(payload: ChatPayload):
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="A chat question is required.")

    try:
        rag_result = ask_with_rag(
            payload.query,
            resume_text=payload.resume_text or _read_cached_text(RESUME_TEXT_PATH),
            jd_text=payload.jd_text or _read_cached_text(JD_TEXT_PATH),
            missing_skills=payload.missing_skills,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Chat request failed: {exc}") from exc

    return {
        "answer": rag_result["answer"],
        "sources": rag_result["sources"],
        "indexed_chunks": rag_result["indexed_chunks"],
    }


@app.post("/api/cold-email/preview")
def cold_email_preview(file: UploadFile = File(...), resume_skills: str = Form(default="")):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV recruiter file.")

    try:
        recruiters_path = _save_upload(file, UPLOAD_DIR / "recruiters.csv")
        recruiters = load_recruiters(str(recruiters_path))
    except (ValueError, HTTPException) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Recruiter preview failed: {exc}") from exc

    skills = [skill.strip() for skill in resume_skills.split(",") if skill.strip()]
    sample = recruiters[0] if recruiters else None
    preview = ""
    if sample:
        preview = generate_email_body(sample["HR / Contact Person"], sample["Company Name"], skills)
    return {"count": len(recruiters), "recruiters": recruiters, "preview": preview}


@app.post("/api/cold-email/send")
def cold_email_send(payload: ColdEmailSendPayload):
    resume_path = UPLOAD_DIR / "resume.pdf"
    recruiters_path = UPLOAD_DIR / "recruiters.csv"
    if not resume_path.exists() or not recruiters_path.exists():
        raise HTTPException(status_code=400, detail="Upload a resume and recruiter CSV file first.")

    try:
        results, total = send_cold_emails(
            str(recruiters_path),
            str(resume_path),
            payload.sender_email,
            payload.app_password,
            payload.resume_skills,
            payload.delay,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Cold email sending failed: {exc}") from exc

    return {"results": results, "total": total}
