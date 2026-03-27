import os
import sys


CURRENT_DIR = os.path.dirname(__file__)
ATS_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
BACKEND_ROOT = os.path.join(ATS_ROOT, "backend")
for p in [ATS_ROOT, BACKEND_ROOT]:
    if p not in sys.path:
        sys.path.append(p)

from vector_store import search  # noqa: E402


def _norm_name(name: str) -> str:
    return " ".join((name or "").strip().lower().split())


def run(state: dict) -> dict:
    jd_text = state.get("jd_text", "")
    recruiter_id = state.get("recruiter_id", "")

    resumes = search(jd_text, top_k=20, doc_type="resume", recruiter_id=recruiter_id)
    linkedins = search(jd_text, top_k=20, doc_type="linkedin", recruiter_id=recruiter_id)

    linkedin_map = {_norm_name(item.get("candidate_name", "")): item for item in linkedins}
    enriched_resumes = []
    for resume in resumes:
        copy = dict(resume)
        match = linkedin_map.get(_norm_name(resume.get("candidate_name", "")))
        copy["linkedin_text"] = (match or {}).get("raw_text", "")
        copy["linkedin_path"] = (match or {}).get("file_path", "")
        enriched_resumes.append(copy)

    return {
        "retrieved_resumes": enriched_resumes,
        "retrieved_linkedins": linkedins,
    }
