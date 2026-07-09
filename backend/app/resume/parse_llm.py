import anthropic
from pydantic import BaseModel

from app.config import settings


class WorkHistoryItem(BaseModel):
    title: str
    company: str
    duration: str
    highlights: list[str] = []


class EducationItem(BaseModel):
    degree: str
    institution: str
    year: str | None = None


class ResumeProfile(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    target_titles: list[str]
    years_experience: float
    seniority_level: str
    skills: list[str]
    clearance_status: str | None = None
    work_history: list[WorkHistoryItem]
    education: list[EducationItem]
    summary: str


def parse_resume(raw_text: str) -> ResumeProfile:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.parse(
        model=settings.match_model,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract a structured candidate profile from this resume. "
                    "The `summary` field should be a condensed 500-1500 character "
                    "block covering target titles, top skills, years of experience, "
                    "seniority, clearance status (if any), and the 2-3 most recent roles "
                    "— this will be reused as context for scoring job matches.\n\n"
                    f"{raw_text}"
                ),
            }
        ],
        output_format=ResumeProfile,
    )
    return response.parsed_output
