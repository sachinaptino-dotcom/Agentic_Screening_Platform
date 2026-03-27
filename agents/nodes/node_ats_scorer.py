import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel

from agents.state import CandidateResult


load_dotenv()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


class SummaryOutput(BaseModel):
    main_summary: str


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def run(state: dict) -> dict:
    jd_text = state.get("jd_text", "")
    jd_skills = state.get("jd_skills", []) or []
    resumes = state.get("retrieved_resumes", []) or []
    llm = ChatGroq(model=GROQ_MODEL, groq_api_key=os.getenv("GROQ_API_KEY"))
    structured = llm.with_structured_output(SummaryOutput)

    scored: list[CandidateResult] = []
    for resume in resumes:
        resume_text = resume.get("raw_text", "")
        matched = [skill for skill in jd_skills if skill.lower() in resume_text.lower()]
        missing = [skill for skill in jd_skills if skill not in matched]
        keyword_score = 0.0 if not jd_skills else (len(matched) / len(jd_skills)) * 100.0
        semantic_score = float(resume.get("semantic_similarity", 0.0)) * 100.0
        ats_score = round(_clamp(0.5 * keyword_score + 0.5 * semantic_score))
        summary = structured.invoke(
            "Given this JD and resume, write a 2-sentence recruiter summary of fit.\n\n"
            f"JD:\n{jd_text}\n\nResume:\n{resume_text}"
        )
        scored.append(
            CandidateResult(
                name=resume.get("candidate_name", "Unknown Candidate"),
                job_title=state.get("jd_requirements", {}).get("role_title", ""),
                resume_text=resume_text,
                linkedin_text=resume.get("linkedin_text", ""),
                keyword_score=round(_clamp(keyword_score), 2),
                semantic_score=round(_clamp(semantic_score), 2),
                ats_score=int(_clamp(ats_score)),
                skills_matched=matched,
                skills_not_matched=missing,
                main_summary=summary.main_summary,
                resume_path=resume.get("file_path", ""),
                linkedin_path=resume.get("linkedin_path", ""),
            )
        )

    return {"scored_candidates": scored}
