import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from agents.state import CandidateResult


load_dotenv()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


class ProsConsOutput(BaseModel):
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)


def run(state: dict) -> dict:
    scored: list[CandidateResult] = state.get("scored_candidates", []) or []
    authenticity_updates = {item.get("name"): item for item in (state.get("authenticity_candidates", []) or [])}
    llm = ChatGroq(model=GROQ_MODEL, groq_api_key=os.getenv("GROQ_API_KEY"))
    structured = llm.with_structured_output(ProsConsOutput)
    combined: list[CandidateResult] = []
    jd_text = state.get("jd_text", "")

    for candidate in scored:
        update = authenticity_updates.get(candidate.name, {})
        profile = candidate.model_copy()
        profile.authenticity_score = float(update.get("authenticity_score", 0.0))
        profile.authenticity_flag = update.get("authenticity_flag", "no_linkedin")
        profile.authenticity_notes = update.get("authenticity_notes", "")
        profile.linkedin_flag = update.get("linkedin_flag", "none")
        profile.linkedin_summary = update.get("linkedin_summary", "")
        out = structured.invoke(
            "As a recruiter, list 2-3 pros and 1-2 cons for this candidate against this JD.\n\n"
            "IMPORTANT: Use the LinkedIn/CV authenticity result to shape your judgement:\n"
            "- If authenticity_flag is 'fail', include at least one cons item about potential inconsistency/risk.\n"
            "- If authenticity_flag is 'pass', you can be more confident.\n\n"
            f"JD:\n{jd_text}\n\n"
            f"Main Summary (CV vs JD):\n{profile.main_summary}\n\n"
            f"LinkedIn Summary (consistency flags):\n{profile.linkedin_summary}\n\n"
            f"Authenticity: {profile.authenticity_flag} ({profile.authenticity_score}%)\n"
            f"Authenticity notes: {profile.authenticity_notes}\n\n"
            f"Matched skills: {', '.join(profile.skills_matched)}\n"
            f"Missing skills: {', '.join(profile.skills_not_matched)}"
        )
        profile.pros = out.pros
        profile.cons = out.cons
        combined.append(profile)
    return {"candidates": combined}
