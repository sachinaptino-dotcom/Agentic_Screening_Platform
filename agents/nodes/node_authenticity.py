import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field


load_dotenv()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


class AuthenticityOutput(BaseModel):
    match_percentage: float = 0.0
    mismatches: list[str] = Field(default_factory=list)
    linkedin_summary: str = ""


def run(state: dict) -> dict:
    resumes = state.get("retrieved_resumes", []) or []
    llm = ChatGroq(model=GROQ_MODEL, groq_api_key=os.getenv("GROQ_API_KEY"))
    structured = llm.with_structured_output(AuthenticityOutput)
    updates = []

    for resume in resumes:
        name = resume.get("candidate_name", "Unknown Candidate")
        linkedin_text = resume.get("linkedin_text", "")
        if not linkedin_text:
            updates.append(
                {
                    "name": name,
                    "authenticity_score": 0.0,
                    "authenticity_flag": "no_linkedin",
                    "authenticity_notes": "",
                    "linkedin_flag": "none",
                    "linkedin_summary": "",
                }
            )
            continue

        out = structured.invoke(
            "You are an HR authenticity checker. Compare this resume and LinkedIn profile. "
            "Identify any inconsistencies in job titles, company names, employment dates, "
            "years of experience, and skills claimed.\n\n"
            f"Resume:\n{resume.get('raw_text', '')}\n\n"
            f"LinkedIn:\n{linkedin_text}\n\n"
            "Return match_percentage, mismatches, linkedin_summary."
        )
        score = float(max(0.0, min(100.0, out.match_percentage)))
        passed = score >= 60.0
        updates.append(
            {
                "name": name,
                "authenticity_score": round(score, 2),
                "authenticity_flag": "pass" if passed else "fail",
                "authenticity_notes": "; ".join(out.mismatches),
                "linkedin_flag": "green" if passed else "red",
                "linkedin_summary": out.linkedin_summary,
            }
        )
    return {"authenticity_candidates": updates}
