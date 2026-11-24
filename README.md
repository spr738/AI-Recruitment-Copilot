# AI Recruitment Copilot

An AI-assisted recruitment MVP for parsing PDF resumes, managing job descriptions, and ranking candidates with transparent skill-match explanations.

## Features
- Upload PDF resumes and extract text
- Create and store job descriptions
- Extract skills from resumes and job descriptions
- Rank candidates with explainable skill overlap scores
- FastAPI REST API with SQLite persistence
- Next.js recruiter dashboard

## Run locally
### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:3000. Set NEXT_PUBLIC_API_URL if the API is not at http://localhost:8000.

## Notes
This is a portfolio MVP, not an automated hiring decision system. Match scores are decision-support signals only. Review candidates consistently, validate extracted information, and never use protected characteristics in screening. Uploaded resumes are stored locally in the backend uploads directory; configure secure object storage, access controls, retention and consent before production use.