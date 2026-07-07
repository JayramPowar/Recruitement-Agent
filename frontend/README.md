# AI Recruitment Copilot Frontend

Vite + React frontend for the AI Recruitment Copilot.

## Setup

```bash
cd frontend
npm install
```

Create `frontend/.env` if your API is not running on the default URL:

```bash
VITE_API_BASE_URL=http://localhost:8001
```

## Run

From the project root, run the backend API:

```bash
uvicorn api.server:app --reload --port 8001
```

In another terminal:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`.

The sidebar unlocks after both the Resume PDF and Job Description are successfully processed by the backend.
