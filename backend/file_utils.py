import os
import uuid
from typing import Iterable

import pdfplumber


SKILLS_VOCAB = [
    "Python",
    "Java",
    "SQL",
    "FastAPI",
    "Django",
    "React",
    "AWS",
    "Docker",
    "Kubernetes",
    "Node.js",
    "TypeScript",
    "JavaScript",
    "PostgreSQL",
    "LangChain",
    "Machine Learning",
]


def extract_pdf_text(path: str) -> str:
    pages: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()


def parse_candidate_name(text: str) -> str:
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned:
            return cleaned[:200]
    return "Unknown Candidate"


def extract_skills(text: str, vocabulary: Iterable[str] = SKILLS_VOCAB) -> list[str]:
    text_lower = text.lower()
    found = [skill for skill in vocabulary if skill.lower() in text_lower]
    return sorted(set(found))


def save_upload_file(content: bytes, target_dir: str) -> str:
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, f"{uuid.uuid4()}.pdf")
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path
