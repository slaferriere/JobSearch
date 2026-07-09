import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import literal, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.matching.runner import get_current_resume, score_single_job
from app.models import Job, MatchScore
from app.schemas import JobDetailOut, JobOut

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("", response_model=list[JobOut])
def list_jobs(
    remote_type: list[str] | None = Query(default=None),
    salary_min: int | None = None,
    salary_max: int | None = None,
    location: str | None = None,
    keyword: str | None = None,
    source: list[str] | None = Query(default=None),
    posted_after: str | None = None,
    min_match_score: int | None = None,
    sort_by: str = "match_score",
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
) -> list[JobOut]:
    resume = get_current_resume(db)

    if resume:
        stmt = (
            select(Job, MatchScore.llm_score)
            .outerjoin(
                MatchScore,
                (MatchScore.job_id == Job.id) & (MatchScore.resume_profile_id == resume.id),
            )
            .where(Job.is_active.is_(True))
        )
    else:
        stmt = select(Job, literal(None)).where(Job.is_active.is_(True))

    if remote_type:
        stmt = stmt.where(Job.remote_type.in_(remote_type))
    if salary_min is not None:
        stmt = stmt.where(Job.salary_max.is_(None) | (Job.salary_max >= salary_min))
    if salary_max is not None:
        stmt = stmt.where(Job.salary_min.is_(None) | (Job.salary_min <= salary_max))
    if location:
        stmt = stmt.where(Job.location_raw.ilike(f"%{location}%"))
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(or_(Job.title.ilike(like), Job.description_text.ilike(like)))
    if source:
        stmt = stmt.where(Job.source.in_(source))
    if posted_after:
        stmt = stmt.where(Job.posted_date >= posted_after)
    if min_match_score is not None and resume:
        stmt = stmt.where(MatchScore.llm_score >= min_match_score)

    if sort_by == "match_score" and resume:
        stmt = stmt.order_by(MatchScore.llm_score.desc().nullslast())
    elif sort_by == "posted_date":
        stmt = stmt.order_by(Job.posted_date.desc())
    elif sort_by == "salary":
        stmt = stmt.order_by(Job.salary_max.desc().nullslast())

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    results = db.execute(stmt).all()
    out = []
    for row in results:
        job, llm_score = row
        job_out = JobOut.model_validate(job)
        job_out.llm_score = llm_score
        out.append(job_out)
    return out


@router.get("/{job_id}", response_model=JobDetailOut)
def get_job(job_id: int, db: Session = Depends(get_db)) -> JobDetailOut:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(404, "Job not found")

    resume = get_current_resume(db)
    match = None
    if resume:
        match = db.scalar(
            select(MatchScore).where(
                MatchScore.job_id == job_id, MatchScore.resume_profile_id == resume.id
            )
        )

    detail = JobDetailOut.model_validate(job)
    if match:
        detail.llm_score = match.llm_score
        detail.llm_rationale = match.llm_rationale
        detail.matching_skills = json.loads(match.matching_skills_json or "[]")
        detail.missing_skills = json.loads(match.missing_skills_json or "[]")
    return detail


@router.post("/{job_id}/match", response_model=JobDetailOut)
def match_job(job_id: int, db: Session = Depends(get_db)) -> JobDetailOut:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(404, "Job not found")
    match = score_single_job(db, job)
    if match is None:
        raise HTTPException(400, "Upload a resume before scoring jobs")

    detail = JobDetailOut.model_validate(job)
    detail.llm_score = match.llm_score
    detail.llm_rationale = match.llm_rationale
    detail.matching_skills = json.loads(match.matching_skills_json or "[]")
    detail.missing_skills = json.loads(match.missing_skills_json or "[]")
    return detail
