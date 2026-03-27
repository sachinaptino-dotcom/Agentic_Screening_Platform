from typing import TypedDict

from pydantic import BaseModel, Field


class CandidateResult(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    job_title: str = ""
    resume_text: str = ""
    linkedin_text: str = ""
    keyword_score: float = 0
    semantic_score: float = 0
    ats_score: int = 0
    skills_matched: list[str] = Field(default_factory=list)
    skills_not_matched: list[str] = Field(default_factory=list)
    main_summary: str = ""
    authenticity_score: float = 0
    authenticity_flag: str = "no_linkedin"
    authenticity_notes: str = ""
    linkedin_flag: str = "none"
    linkedin_summary: str = ""
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    resume_path: str = ""
    linkedin_path: str = ""
    rank: int = 0


class GraphState(TypedDict, total=False):
    jd_text: str
    jd_skills: list[str]
    jd_requirements: dict
    recruiter_id: str
    retrieved_resumes: list[dict]
    retrieved_linkedins: list[dict]
    candidates: list[CandidateResult]
    scored_candidates: list[CandidateResult]
    authenticity_candidates: list[dict]
    ranked_profiles: list[CandidateResult]
