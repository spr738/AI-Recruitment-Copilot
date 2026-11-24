# AI Recruitment Copilot

A portfolio MVP for parsing PDF resumes, organizing applicants, and ranking candidates against job descriptions with transparent skill-match explanations.

## What works today
- Upload text-based PDF resumes (8 MB limit) and extract selectable text
- Create and persist job descriptions
- Detect a curated set of technical and workplace skills
- Rank candidates by detected required-skill overlap and show matched/missing skills
- FastAPI REST API, SQLAlchemy and local SQLite database
- Next.js recruiter dashboard

**Matching is currently deterministic keyword/skill matching, not an LLM or embeddings model.** This keeps the score explainable and avoids sending resume data to an external AI provider. Semantic matching and interview-question generation are future extensions.

## Run locally
### Backend
```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

Run backend tests:
```bash
pip install -r requirements-dev.txt
pytest
```

### Frontend
Open a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:3000. If the API is hosted elsewhere, create `frontend/.env.local` and set `NEXT_PUBLIC_API_URL=http://localhost:8000` to your backend URL.

## API endpoints
- `GET /api/health` — health check
- `GET /api/jobs` — list jobs
- `POST /api/jobs` — create a job (`title`, `description`)
- `POST /api/candidates/upload` — upload a PDF (`name`, optional `email`, `job_id`, `file`)
- `GET /api/jobs/{job_id}/matches` — ranked candidate matches

## Important limitations and privacy
This is a learning/portfolio MVP, not a production hiring system or an automated hiring decision tool. A skill-overlap percentage is not a measure of candidate quality. Human review is required; do not use protected characteristics or proxies to screen applicants. Scanned PDFs requiring OCR are not supported. Resume text is stored in a local SQLite database; files are not retained after parsing. Before real-world use, add authentication and role-based access, encryption, secure storage, consent and retention controls, audit logs, rate limiting, robust validation, and a privacy/security review.
