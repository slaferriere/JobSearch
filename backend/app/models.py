from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("source", "source_id", name="uq_source_job"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String, index=True)
    source_id: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    company: Mapped[str] = mapped_column(String, index=True)
    location_raw: Mapped[str | None] = mapped_column(String, nullable=True)
    remote_type: Mapped[str] = mapped_column(String, default="unknown", index=True)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str] = mapped_column(String, default="USD")
    description_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    apply_url: Mapped[str] = mapped_column(String)
    apply_url_is_redirect: Mapped[bool] = mapped_column(Boolean, default=False)
    posted_date: Mapped[str | None] = mapped_column(String, nullable=True)
    first_seen_at: Mapped[str] = mapped_column(String, default=utcnow)
    last_seen_at: Mapped[str] = mapped_column(String, default=utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    miss_count: Mapped[int] = mapped_column(Integer, default=0)
    content_hash: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    likely_duplicate_of: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_json: Mapped[str] = mapped_column(Text, default="{}")


class ResumeProfile(Base):
    __tablename__ = "resume_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uploaded_at: Mapped[str] = mapped_column(String, default=utcnow)
    original_filename: Mapped[str | None] = mapped_column(String, nullable=True)
    file_path: Mapped[str] = mapped_column(String)
    raw_text: Mapped[str] = mapped_column(Text)
    parsed_json: Mapped[str] = mapped_column(Text)
    profile_summary: Mapped[str] = mapped_column(Text)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)


class MatchScore(Base):
    __tablename__ = "match_scores"
    __table_args__ = (UniqueConstraint("job_id", "resume_profile_id", name="uq_job_resume"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), index=True)
    resume_profile_id: Mapped[int] = mapped_column(ForeignKey("resume_profile.id"))
    prefilter_score: Mapped[float | None] = mapped_column(Integer, nullable=True)
    llm_score: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    llm_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    matching_skills_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    missing_skills_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String, nullable=True)
    scored_at: Mapped[str] = mapped_column(String, default=utcnow)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    started_at: Mapped[str] = mapped_column(String, default=utcnow)
    finished_at: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    jobs_added: Mapped[int] = mapped_column(Integer, default=0)
    jobs_updated: Mapped[int] = mapped_column(Integer, default=0)
    jobs_deactivated: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
