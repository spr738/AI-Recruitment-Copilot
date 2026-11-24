import os
import re
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pypdf import PdfReader
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'recruitment.db'}")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    candidates = relationship("Candidate", back_populates="job")


class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(320), default="")
    filename = Column(String(255), nullable=False)
    resume_text = Column(Text, nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    job = relationship("Job", back_populates="candidates")


Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="AI Recruitment Copilot API",
    version="1.1.0",
    description="Resume parsing and explainable candidate-job matching.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Canonical skill names mapped to common spellings and resume/JD variations.
# Matching is lexical and explainable; it does not infer experience from a degree.
SKILL_ALIASES = {
    "python": ["python"],
    "java": ["java"],
    "javascript": ["javascript", "java script"],
    "typescript": ["typescript"],
    "react": ["react", "react.js"],
    "next.js": ["next.js", "nextjs"],
    "node.js": ["node.js", "nodejs"],
    "express.js": ["express.js", "express"],
    "fastapi": ["fastapi"],
    "django": ["django"],
    "flask": ["flask"],
    "sql": ["sql"],
    "postgresql": ["postgresql", "postgres"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo db"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes"],
    "git": ["git"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "nlp": ["nlp", "natural language processing"],
    "pytorch": ["pytorch"],
    "tensorflow": ["tensorflow"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "matplotlib": ["matplotlib"],
    "data science": ["data science"],
    "data analysis": ["data analysis", "data analytics"],
    "data visualization": ["data visualization", "data visualisation"],
    "excel": ["excel", "microsoft excel"],
    "power bi": ["power bi", "powerbi"],
    "html": ["html"],
    "css": ["css"],
    "c++": ["c++", "cpp"],
    "c": ["c programming"],
    "rest api": ["rest api", "restful api"],
    "electrical engineering": ["electrical engineering"],
    "electrical circuits": ["electrical circuits", "electric circuits"],
    "electrical machines": ["electrical machines", "electric machines"],
    "electrical maintenance": ["electrical maintenance"],
    "electrical systems": ["electrical systems", "electric systems"],
    "power systems": ["power systems"],
    "substation": ["substation", "substations"],
    "motors": ["electric motors", "motor", "motors"],
    "control panels": ["control panel", "control panels"],
    "control circuits": ["control circuit", "control circuits"],
    "contactors": ["contactor", "contactors"],
    "relays": ["relay", "relays"],
    "circuit breakers": ["circuit breaker", "circuit breakers"],
    "electrical protection": ["electrical protection", "protection systems"],
    "troubleshooting": ["troubleshooting", "fault diagnosis", "fault diagnostics"],
    "preventive maintenance": ["preventive maintenance", "planned maintenance"],
    "predictive maintenance": ["predictive maintenance"],
    "vfd": ["vfd", "vfds", "variable frequency drive", "variable frequency drives"],
    "servo drives": ["servo drive", "servo drives"],
    "plc": ["plc", "plcs", "programmable logic controller", "programmable logic controllers"],
    "scada": ["scada"],
    "hmi": ["hmi", "human machine interface"],
    "automation": ["automation", "industrial automation"],
    "instrumentation": ["instrumentation"],
    "industrial communication": ["industrial communication", "industrial communication systems"],
    "sensors": ["sensor", "sensors"],
    "proximity sensors": ["proximity sensor", "proximity sensors", "proximity switch", "proximity switches"],
    "photoelectric sensors": ["photoelectric sensor", "photoelectric sensors"],
    "encoders": ["encoder", "encoders"],
    "load cells": ["load cell", "load cells"],
    "solenoid valves": ["solenoid valve", "solenoid valves"],
    "pid controllers": ["pid controller", "pid controllers"],
    "flow meters": ["flow meter", "flow meters"],
    "calibration": ["calibration", "calibrating"],
    "electrical measurement": ["electrical measurement", "electrical measuring instruments"],
    "machine safety": ["machine safety"],
    "electrical safety": ["electrical safety"],
    "loto": ["loto", "lockout tagout", "lockout/tagout"],
    "equipment reliability": ["equipment reliability", "reliability improvement"],
    "machine availability": ["machine availability", "equipment availability"],
    "oee": ["oee", "overall equipment effectiveness"],
    "mttr": ["mttr", "mean time to repair"],
    "mtbf": ["mtbf", "mean time between failures"],
    "tpm": ["tpm", "total productive maintenance"],
    "kaizen": ["kaizen"],
    "root cause analysis": ["root cause analysis", "rca"],
    "corrective actions": ["corrective action", "corrective actions"],
    "spare parts management": ["spare parts management", "critical spares"],
    "maintenance reporting": ["maintenance reporting", "breakdown reports"],
    "analytical thinking": ["analytical thinking", "analytical reasoning"],
    "problem solving": ["problem solving", "problem-solving"],
    "communication": ["communication", "communication skills"],
    "teamwork": ["teamwork", "team work"],
    "leadership": ["leadership"],
    "project management": ["project management"],
}

def _contains_term(text: str, term: str) -> bool:
    # Allow punctuation/spacing variations without matching inside larger words.
    escaped = re.escape(term.lower())
    return re.search(r"(?<![a-z0-9])" + escaped + r"(?![a-z0-9])", text) is not None


def extract_skills(text: str) -> List[str]:
    normalized = re.sub(r"\s+", " ", text.lower())
    found = []
    for canonical, aliases in SKILL_ALIASES.items():
        if any(_contains_term(normalized, alias) for alias in aliases):
            found.append(canonical)
    return sorted(found)


def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class JobIn(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=20)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "AI Recruitment Copilot API"}


@app.get("/api/jobs")
def list_jobs():
    db = SessionLocal()
    try:
        return [
            {"id": j.id, "title": j.title, "description": j.description}
            for j in db.query(Job).order_by(Job.id.desc()).all()
        ]
    finally:
        db.close()


@app.post("/api/jobs")
def create_job(payload: JobIn):
    db = SessionLocal()
    try:
        job = Job(title=payload.title.strip(), description=payload.description.strip())
        db.add(job)
        db.commit()
        db.refresh(job)
        return {"id": job.id, "title": job.title, "description": job.description}
    finally:
        db.close()


@app.post("/api/candidates/upload")
async def upload_resume(
    name: str = Form(...),
    email: str = Form(""),
    job_id: int | None = Form(None),
    file: UploadFile = File(...),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF resume.")
    raw = await file.read()
    if len(raw) > 8 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="PDF must be smaller than 8 MB.")
    try:
        from io import BytesIO

        reader = PdfReader(BytesIO(raw))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not read this PDF.") from exc
    if not text:
        raise HTTPException(
            status_code=400,
            detail="No selectable text found. Scanned PDFs need OCR, which is not included yet.",
        )
    db = SessionLocal()
    try:
        if job_id is not None and db.get(Job, job_id) is None:
            raise HTTPException(status_code=404, detail="Job not found.")
        candidate = Candidate(
            name=name.strip(),
            email=email.strip(),
            filename=Path(file.filename).name,
            resume_text=text,
            job_id=job_id,
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        return {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "filename": candidate.filename,
            "skills": extract_skills(text),
        }
    finally:
        db.close()


@app.get("/api/jobs/{job_id}/matches")
def matches(job_id: int):
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found.")

        required = set(extract_skills(job.description))
        results = []
        for candidate in db.query(Candidate).filter(Candidate.job_id == job_id).all():
            found = set(extract_skills(candidate.resume_text))
            matched = sorted(required & found)
            missing = sorted(required - found)
            score = round(100 * len(matched) / len(required)) if required else 0
            results.append(
                {
                    "id": candidate.id,
                    "name": candidate.name,
                    "email": candidate.email,
                    "filename": candidate.filename,
                    "score": score,
                    "matched_skills": matched,
                    "missing_skills": missing,
                }
            )
        return sorted(results, key=lambda item: item["score"], reverse=True)
    finally:
        db.close()
