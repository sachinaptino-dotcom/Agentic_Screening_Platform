import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field


load_dotenv()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


class JDParseOutput(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)
    min_experience_years: int = 0
    role_title: str = ""
    role_summary: str = ""


def run(state: dict) -> dict:
    llm = ChatGroq(model=GROQ_MODEL, groq_api_key=os.getenv("GROQ_API_KEY"))
    structured = llm.with_structured_output(JDParseOutput)
    result = structured.invoke(
        "Extract required_skills, nice_to_have_skills, min_experience_years, role_title, role_summary "
        "from this job description:\n\n"
        f"{state.get('jd_text', '')}"
    )
    return {
        "jd_skills": result.required_skills,
        "jd_requirements": result.model_dump(),
    }
