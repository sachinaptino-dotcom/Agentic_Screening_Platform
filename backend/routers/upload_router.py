import os
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from file_utils import extract_pdf_text, extract_skills, parse_candidate_name, save_upload_file
from models import RecruiterAuth, RecruiterPerformance
from vector_store import add_document


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv()

router = APIRouter(prefix="/upload", tags=["upload"])
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")


def _uploads_root() -> str:
    if os.path.isabs(UPLOAD_DIR):
        return UPLOAD_DIR
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", UPLOAD_DIR))


def _get_performance(db: Session, auth_id: str) -> RecruiterPerformance:
    perf = db.query(RecruiterPerformance).filter(RecruiterPerformance.auth_id == auth_id).first()
    if not perf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recruiter profile not found")
    return perf


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: RecruiterAuth = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    content = await file.read()
    stored_path = save_upload_file(content, os.path.join(_uploads_root(), "resumes"))
    text = extract_pdf_text(stored_path)
    candidate_name = parse_candidate_name(text)
    skills = extract_skills(text)
    metadata = {
        "doc_id": str(uuid.uuid4()),
        "doc_type": "resume",
        "recruiter_id": str(current_user.id),
        "candidate_name": candidate_name,
        "file_path": stored_path,
        "raw_text": text,
        "skills": skills,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    saved = add_document(text, metadata)
    perf = _get_performance(db, str(current_user.id))
    perf.total_resumes_uploaded = (perf.total_resumes_uploaded or 0) + 1
    perf.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {
        "doc_id": saved["doc_id"],
        "candidate_name": candidate_name,
        "skills_found": skills,
        "message": "Resume uploaded successfully",
    }


@router.post("/linkedin")
async def upload_linkedin(
    file: UploadFile = File(...),
    current_user: RecruiterAuth = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    content = await file.read()
    stored_path = save_upload_file(content, os.path.join(_uploads_root(), "linkedin"))
    text = extract_pdf_text(stored_path)
    candidate_name = parse_candidate_name(text)
    metadata = {
        "doc_id": str(uuid.uuid4()),
        "doc_type": "linkedin",
        "recruiter_id": str(current_user.id),
        "candidate_name": candidate_name,
        "file_path": stored_path,
        "raw_text": text,
        "skills": extract_skills(text),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    saved = add_document(text, metadata)
    _ = _get_performance(db, str(current_user.id))
    return {
        "doc_id": saved["doc_id"],
        "candidate_name": candidate_name,
        "message": "LinkedIn uploaded successfully",
    }
