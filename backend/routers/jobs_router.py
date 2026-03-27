import os
import sys
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from file_utils import extract_pdf_text, save_upload_file
from models import Candidate, RecruiterAuth, RecruiterPerformance


CURRENT_DIR = os.path.dirname(__file__)
ATS_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if ATS_ROOT not in sys.path:
    sys.path.append(ATS_ROOT)

from agents.pipeline import run_pipeline  # noqa: E402


load_dotenv(dotenv_path=os.path.join(ATS_ROOT, ".env"))
load_dotenv()

router = APIRouter(tags=["jobs"])
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")


def _uploads_root() -> str:
    if os.path.isabs(UPLOAD_DIR):
        return UPLOAD_DIR
    return os.path.abspath(os.path.join(ATS_ROOT, UPLOAD_DIR))


def _get_performance(db: Session, auth_id: str) -> RecruiterPerformance:
    perf = db.query(RecruiterPerformance).filter(RecruiterPerformance.auth_id == auth_id).first()
    if not perf:
        raise HTTPException(status_code=404, detail="Recruiter profile not found")
    return perf


@router.post("/jobs/run")
async def run_job(
    file: UploadFile = File(...),
    current_user: RecruiterAuth = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    content = await file.read()
    jd_path = save_upload_file(content, os.path.join(_uploads_root(), "jds"))
    jd_text = extract_pdf_text(jd_path)

    recruiter_auth_id = str(current_user.id)
    ranked_profiles = run_pipeline(jd_text=jd_text, recruiter_id=recruiter_auth_id)

    performance = _get_performance(db, recruiter_auth_id)
    shortlisted = 0
    rejected = 0

    for profile in ranked_profiles:
        if profile.ats_score >= 60:
            shortlisted += 1
        else:
            rejected += 1
        candidate = Candidate(
            recruiter_id=performance.id,
            name=profile.name,
            email=profile.email,
            phone=profile.phone,
            location=profile.location,
            job_applied=profile.job_title,
            job_title=profile.job_title,
            ats_score=profile.ats_score,
            rank=profile.rank,
            skills_matched=profile.skills_matched,
            skills_not_matched=profile.skills_not_matched,
            main_summary=profile.main_summary,
            keyword_score=profile.keyword_score,
            semantic_score=profile.semantic_score,
            authenticity_score=profile.authenticity_score,
            authenticity_flag=profile.authenticity_flag,
            authenticity_notes=profile.authenticity_notes,
            linkedin_flag=profile.linkedin_flag,
            linkedin_summary=profile.linkedin_summary,
            pros=profile.pros,
            cons=profile.cons,
            resume_path=profile.resume_path,
            linkedin_path=profile.linkedin_path,
        )
        db.add(candidate)

    performance.total_jds_processed = (performance.total_jds_processed or 0) + 1
    performance.total_shortlisted = (performance.total_shortlisted or 0) + shortlisted
    performance.total_rejected = (performance.total_rejected or 0) + rejected
    performance.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "job_id": str(uuid.uuid4()),
        "ranked_profiles": [profile.model_dump() for profile in ranked_profiles],
    }


@router.get("/candidates")
def get_candidates(
    current_user: RecruiterAuth = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    performance = _get_performance(db, str(current_user.id))
    rows = (
        db.query(Candidate)
        .filter(Candidate.recruiter_id == performance.id)
        .order_by(Candidate.ats_score.desc())
        .all()
    )
    payload = []
    for c in rows:
        payload.append(
            {
                "id": str(c.id),
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "location": c.location,
                "job_title": c.job_title,
                "ats_score": c.ats_score,
                "rank": c.rank,
                "skills_matched": c.skills_matched or [],
                "skills_not_matched": c.skills_not_matched or [],
                "main_summary": c.main_summary,
                "keyword_score": float(c.keyword_score or 0),
                "semantic_score": float(c.semantic_score or 0),
                "authenticity_score": float(c.authenticity_score or 0),
                "authenticity_flag": c.authenticity_flag,
                "authenticity_notes": c.authenticity_notes,
                "linkedin_flag": c.linkedin_flag,
                "linkedin_summary": c.linkedin_summary,
                "pros": c.pros or [],
                "cons": c.cons or [],
                "resume_path": c.resume_path,
                "linkedin_path": c.linkedin_path,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
        )
    return payload
