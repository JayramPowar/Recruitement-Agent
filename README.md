# AI Recruitment Copilot

AI Recruitment Copilot is an AI-powered career assistant that compares resumes with job descriptions, calculates ATS match scores, reviews resumes, generates cover letters, creates interview questions, builds learning roadmaps, supports recruiter outreach, and answers career queries through a RAG-based chatbot.

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
| AI / LLM | Groq API, LLaMA 3.3 70B |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector Store | Qdrant Client (`:memory:` mode in current code) |
| Resume Parsing | pdfplumber |
| Data / Email | pandas, openpyxl, smtplib |
| Config | python-dotenv |

## Project Structure

```text
AI-Recruitment-Copilot/
|-- api/
|   |-- server.py                # FastAPI adapter for frontend requests
|
|-- agents/
|   |-- ats_agent.py
|   |-- career_agent.py
|   |-- interview_agent.py
|   |-- resume_agent.py
|   |-- router_agent.py
|
|-- ats/
|   |-- ats_score.py            # ATS scoring logic
|   |-- skill_extractor.py      # Resume/JD text extraction and skill extraction
|
|-- cold_email/
|   |-- sender.py               # Recruiter parsing, preview, and email sending
|
|-- cover_letter/
|   |-- generator.py
|
|-- rag/
|   |-- embeddings.py
|   |-- qdrant_store.py         # In-memory Qdrant store
|   |-- retriever.py
|
|-- roadmap/
|   |-- roadmap_generator.py
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
|-- requirements.txt
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
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 5. Configure environment variables

Create a root `.env` file with:

```env
GROQ_API_KEY=your-groq-api-key
QDRANT_HOST=https://your-qdrant-cluster-url
QDRANT_PORT=6333
```

Notes:

- The current code uses in-memory Qdrant in [qdrant_store.py](<D:\GenAI\AI-recruitement Copilot\AI-Recruitment-Copilot\rag\qdrant_store.py>), so `QDRANT_HOST` and `QDRANT_API` are not actively used yet.
- `GROQ_API_KEY` is required for skill extraction, resume review, cover letter generation, roadmap generation, chatbot routing, and interview questions.

### 6. Optional frontend API override

Create `frontend/.env` if you want to point the frontend to a custom backend port:

```env
VITE_API_BASE_URL=http://localhost:8001
```

## Running the App

### Start the backend

Use `8001` if `8000` is blocked on your machine.

```bash
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

The ATS scoring logic lives in [ats_score.py](<D:\GenAI\AI-recruitement Copilot\AI-Recruitment-Copilot\ats\ats_score.py>).

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
| Semantic Score | 30% | Uses `all-MiniLM-L6-v2` embeddings and cosine similarity between resume and JD text. |
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
- Cold email sender expects an `.xlsx` file with `Company Name`, `HR / Contact Person`, and `Email ID` columns.
- Gmail sending requires a Gmail app password, not the normal account password.
- Qdrant is currently used in in-memory mode, so vectors are not persisted after restart.

