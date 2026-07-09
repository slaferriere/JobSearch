import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.matching.prefilter import rank_and_filter
from app.matching.score_llm import score_job
from app.models import Job, MatchScore, ResumeProfile, utcnow
from app.resume.parse_llm import ResumeProfile as ResumeProfileSchema


def get_current_resume(db: Session) -> ResumeProfile | None:
    return db.scalar(select(ResumeProfile).where(ResumeProfile.is_current.is_(True)))


def score_new_jobs(db: Session, top_n: int | None = None) -> int:
    """Score active jobs that haven't yet been scored against the current resume."""
    resume_row = get_current_resume(db)
    if resume_row is None:
        return 0

    resume_schema = ResumeProfileSchema.model_validate(json.loads(resume_row.parsed_json))

    already_scored_ids = set(
        db.scalars(
            select(MatchScore.job_id).where(MatchScore.resume_profile_id == resume_row.id)
        ).all()
    )
    stmt = select(Job).where(Job.is_active.is_(True))
    if already_scored_ids:
        stmt = stmt.where(Job.id.notin_(already_scored_ids))
    candidate_jobs = db.scalars(stmt).all()
    if not candidate_jobs:
        return 0

    ranked = rank_and_filter(resume_schema, list(candidate_jobs), top_n or settings.prefilter_top_n)

    scored_count = 0
    for job, prefilter_val in ranked:
        try:
            result = score_job(
                resume_row.profile_summary, job.title, job.company, job.description_text or ""
            )
        except Exception:  # noqa: BLE001 - skip jobs that fail scoring, continue the batch
            continue
        db.add(
            MatchScore(
                job_id=job.id,
                resume_profile_id=resume_row.id,
                prefilter_score=prefilter_val,
                llm_score=result.score,
                llm_rationale=result.rationale,
                matching_skills_json=json.dumps(result.matching_skills),
                missing_skills_json=json.dumps(result.missing_skills),
                model_used=settings.match_model,
                scored_at=utcnow(),
            )
        )
        scored_count += 1
    db.commit()
    return scored_count


def score_single_job(db: Session, job: Job) -> MatchScore | None:
    resume_row = get_current_resume(db)
    if resume_row is None:
        return None
    result = score_job(resume_row.profile_summary, job.title, job.company, job.description_text or "")

    existing = db.scalar(
        select(MatchScore).where(
            MatchScore.job_id == job.id, MatchScore.resume_profile_id == resume_row.id
        )
    )
    if existing is None:
        existing = MatchScore(job_id=job.id, resume_profile_id=resume_row.id)
        db.add(existing)

    existing.llm_score = result.score
    existing.llm_rationale = result.rationale
    existing.matching_skills_json = json.dumps(result.matching_skills)
    existing.missing_skills_json = json.dumps(result.missing_skills)
    existing.model_used = settings.match_model
    existing.scored_at = utcnow()
    db.commit()
    db.refresh(existing)
    return existing
