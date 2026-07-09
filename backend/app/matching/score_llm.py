import anthropic
from pydantic import BaseModel

from app.config import settings


class MatchResult(BaseModel):
    score: int
    rationale: str
    matching_skills: list[str]
    missing_skills: list[str]


SYSTEM_PROMPT = (
    "You score how well a candidate matches a single job posting. "
    "Score 0-100 based on skills overlap, seniority/title fit, and relevant experience. "
    "Be concrete: list the specific skills that match and the specific skills/qualifications "
    "the posting wants that the candidate's resume doesn't show."
)


def score_job(profile_summary: str, job_title: str, company: str, description_text: str) -> MatchResult:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.parse(
        model=settings.match_model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"CANDIDATE PROFILE:\n{profile_summary}\n\n"
                    f"JOB POSTING:\nTitle: {job_title}\nCompany: {company}\n"
                    f"Description: {description_text[:4000]}"
                ),
            }
        ],
        output_format=MatchResult,
    )
    return response.parsed_output
