from rapidfuzz import fuzz

from app.models import Job
from app.resume.parse_llm import ResumeProfile


def prefilter_score(resume: ResumeProfile, job: Job) -> float:
    resume_text = " ".join([*resume.target_titles, *resume.skills])
    job_text = f"{job.title} {(job.description_text or '')[:500]}"
    return fuzz.token_set_ratio(resume_text, job_text)


def rank_and_filter(resume: ResumeProfile, jobs: list[Job], top_n: int) -> list[tuple[Job, float]]:
    scored = [(job, prefilter_score(resume, job)) for job in jobs]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:top_n]
