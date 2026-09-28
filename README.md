# ResumeLens - AI Recruitment Copilot

#### Click here for live demo - [https://recruitement-agent.vercel.app/](https://recruitement-agent.vercel.app/)

ResumeLens is an AI-powered career assistant that compares resumes with job descriptions, calculates ATS match scores, reviews resumes, generates cover letters, creates interview questions, builds learning roadmaps, supports recruiter outreach, and answers career queries through a RAG-based chatbot.

## Features

| Feature | Description |
| --- | --- |
| Upload Resume + JD | Upload a resume PDF and paste or upload a job description to unlock the rest of the app. |
| ATS Dashboard | Calculates overall ATS score using keyword match, semantic similarity, experience, education, and resume format checks. |
| Resume Analysis | Generates AI-based feedback on resume strengths, weaknesses, and improvements. |
| Cover Letter Generator | Creates a tailored cover letter from the uploaded resume and job description. |
| Interview Questions | Produces role-relevant interview questions based on the resume and JD. |
| Learning Roadmap | Builds a skill roadmap from missing skills identified in ATS analysis. |
| Cold Email Sender | Previews and sends personalized outreach emails to recruiters from an Excel file. |
| AI Chatbot | Uses retrieval over uploaded resume and JD context to answer career questions. |

## Tech Stack

| Layer | Tools / Libraries |
| --- | --- |
| Frontend | React, Vite, Tailwind CSS, Framer Motion, Lucide React |
| Backend API | FastAPI, Uvicorn |
| AI / LLM | Groq API, GPT OSS 120B |
| Embeddings | Hugging Face hosted `sentence-transformers/all-MiniLM-L6-v2` |
| Retrieval | In-memory vector search over hosted Hugging Face embeddings |
| Resume Parsing | pdfplumber |
| Data / Email | CSV, smtplib |
| Config | python-dotenv |

## Project Structure

```text
AI-Recruitment-Copilot/
|-- backend/
|   |-- api/
|   |   `-- server.py           # FastAPI adapter for frontend requests
|   |-- agents/
|   |-- ats/
|   |-- cold_email/
|   |-- cover_letter/
|   |-- rag/
|   |-- roadmap/
|   |-- data/
|   `-- requirements.txt
|
|-- frontend/
|   |-- src/
|   |   |-- api/
|   |   |-- components/
|   |   |-- context/
|   |   `-- views/
|   |-- package.json
|   |-- tailwind.config.js
|   `-- vite.config.js
|
`-- README.md
```

## Installation

### 1. Clone the project

```bash
git clone https://github.com/JayramPowar/Recruitement-Agent.git
cd AI-Recruitment-Copilot
```

### 2. Create and activate a Python virtual environment

Windows PowerShell:

```bash
python -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 5. Configure environment variables

Create `backend/.env` with:

```env
GROQ_API_KEY=your-groq-api-key
HF_TOKEN=your-hugging-face-token
```

Notes:

- RAG uses an in-memory vector store in [qdrant_store.py](backend/rag/qdrant_store.py), so vectors are rebuilt from the current resume, job description, and ATS context during chat requests.
- `HF_TOKEN` is required for hosted RAG embeddings. You can set `HF_EMBEDDING_MODEL` to use a different Hugging Face feature-extraction model.
- `GROQ_API_KEY` is required for skill extraction, resume review, cover letter generation, roadmap generation, chatbot answers, and interview questions.

### 6. Optional frontend API override

Create `frontend/.env` if you want to point the frontend to a custom backend port:

```env
VITE_API_BASE_URL=http://localhost:8001
```

## Running the App

### Start the backend

Use `8001` if `8000` is blocked on your machine.

```bash
cd backend
python -m uvicorn api.server:app --reload --port 8001
```

### Start the frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

## How to Use

1. Upload a resume PDF.
2. Upload or paste a job description.
3. Open the ATS Dashboard and run ATS analysis.
4. Use unlocked sections for resume review, cover letter generation, interview questions, roadmap generation, chatbot support, and cold email outreach.

## How ATS Score Is Calculated

The ATS scoring logic lives in [ats_score.py](backend/ats/ats_score.py).

The final ATS score is computed as:

```text
Final ATS Score =
  (Keyword Score   * 0.30) +
  (Semantic Score  * 0.30) +
  (Experience Score * 0.20) +
  (Education Score * 0.10) +
  (Format Score    * 0.10)
```

### ATS score components

| Component | Weight | How it works |
| --- | --- | --- |
| Keyword Score | 30% | Compares extracted resume skills against extracted JD skills. |
| Semantic Score | 30% | Uses lightweight token cosine similarity between resume and JD text. |
| Experience Score | 20% | Detects years of experience in JD and resume using regex patterns and scores the match. |
| Education Score | 10% | Matches degree levels such as Bachelor, M.Tech, MBA, MSc, PhD, Diploma, and related terms. |
| Format Score | 10% | Checks resume length, section headings, contact details, and overall ATS readability. |

### Resume format checks used in backend

The backend currently applies these checks:

- Penalizes resumes with extracted text shorter than 200 characters.
- Looks for `experience`, `education`, and `skills` section headings.
- Looks for contact indicators such as `@`, `phone`, `email`, `linkedin`, and `github`.
- Penalizes resumes with fewer than 100 words.

## Important Notes

- Resume upload expects a PDF file.
- Job description can be pasted directly or uploaded as `.txt`, `.md`, or `.pdf`.
- Cold email sender expects a `.csv` file with `Company Name`, `HR / Contact Person`, and `Email ID` columns.
- Gmail sending requires a Gmail app password, not the normal account password.
- RAG vectors are stored in memory and rebuilt during chat requests, so they are not persisted after restart.
