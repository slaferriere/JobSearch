from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.connectors.base import Connector, NormalizedJob
from app.connectors.dedupe import content_hash
from app.connectors.greenhouse import GreenhouseConnector
from app.connectors.lever import LeverConnector
from app.connectors.registry import GREENHOUSE_COMPANIES, LEVER_COMPANIES, USAJOBS_KEYWORDS
from app.connectors.usajobs import UsaJobsConnector
from app.models import IngestionRun, Job, utcnow


def build_connectors() -> dict[str, Connector]:
    connectors: dict[str, Connector] = {
        "greenhouse": GreenhouseConnector(GREENHOUSE_COMPANIES),
        "lever": LeverConnector(LEVER_COMPANIES),
    }
    if settings.usajobs_api_key and settings.usajobs_user_agent:
        connectors["usajobs"] = UsaJobsConnector(
            settings.usajobs_api_key, settings.usajobs_user_agent, USAJOBS_KEYWORDS
        )
    return connectors


def run_ingestion(db: Session, sources: list[str] | None = None) -> list[IngestionRun]:
    connectors = build_connectors()
    keys = sources or list(connectors.keys())
    runs: list[IngestionRun] = []

    for key in keys:
        connector = connectors.get(key)
        if connector is None:
            continue
        run = IngestionRun(started_at=utcnow(), source=key)
        db.add(run)
        db.flush()
        try:
            normalized_jobs = connector.fetch_normalized()
            added, updated = _upsert_jobs(db, key, normalized_jobs)
            deactivated = _mark_stale(db, key, {j.source_id for j in normalized_jobs})
            run.jobs_added = added
            run.jobs_updated = updated
            run.jobs_deactivated = deactivated
        except Exception as exc:  # noqa: BLE001 - record and continue other sources
            run.error = str(exc)
        run.finished_at = utcnow()
        db.commit()
        runs.append(run)

    return runs


def _upsert_jobs(db: Session, source: str, normalized_jobs: list[NormalizedJob]) -> tuple[int, int]:
    added = 0
    updated = 0
    for nj in normalized_jobs:
        existing = db.scalar(
            select(Job).where(Job.source == source, Job.source_id == nj.source_id)
        )
        chash = content_hash(nj.company, nj.title, nj.location_raw)
        duplicate_id = None
        dup = db.scalar(
            select(Job).where(
                Job.content_hash == chash, Job.source != source, Job.is_active.is_(True)
            )
        )
        if dup:
            duplicate_id = dup.id

        if existing:
            existing.title = nj.title
            existing.company = nj.company
            existing.location_raw = nj.location_raw
            existing.remote_type = nj.remote_type
            existing.salary_min = nj.salary_min
            existing.salary_max = nj.salary_max
            existing.description_html = nj.description_html
            existing.description_text = nj.description_text
            existing.apply_url = nj.apply_url
            existing.apply_url_is_redirect = nj.apply_url_is_redirect
            existing.posted_date = nj.posted_date
            existing.last_seen_at = utcnow()
            existing.is_active = True
            existing.miss_count = 0
            existing.content_hash = chash
            existing.likely_duplicate_of = duplicate_id
            updated += 1
        else:
            db.add(
                Job(
                    source=source,
                    source_id=nj.source_id,
                    title=nj.title,
                    company=nj.company,
                    location_raw=nj.location_raw,
                    remote_type=nj.remote_type,
                    salary_min=nj.salary_min,
                    salary_max=nj.salary_max,
                    salary_currency=nj.salary_currency,
                    description_html=nj.description_html,
                    description_text=nj.description_text,
                    apply_url=nj.apply_url,
                    apply_url_is_redirect=nj.apply_url_is_redirect,
                    posted_date=nj.posted_date,
                    content_hash=chash,
                    likely_duplicate_of=duplicate_id,
                )
            )
            added += 1
    db.flush()
    return added, updated


def _mark_stale(db: Session, source: str, seen_source_ids: set[str]) -> int:
    deactivated = 0
    active_jobs = db.scalars(
        select(Job).where(Job.source == source, Job.is_active.is_(True))
    ).all()
    for job in active_jobs:
        if job.source_id in seen_source_ids:
            continue
        job.miss_count += 1
        if job.miss_count >= 2:
            job.is_active = False
            deactivated += 1
    db.flush()
    return deactivated
