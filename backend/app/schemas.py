from pydantic import BaseModel


class JobOut(BaseModel):
    id: int
    source: str
    title: str
    company: str
    location_raw: str | None
    remote_type: str
    salary_min: int | None
    salary_max: int | None
    salary_currency: str
    apply_url: str
    apply_url_is_redirect: bool
    posted_date: str | None
    is_active: bool
    likely_duplicate_of: int | None
    llm_score: int | None = None

    model_config = {"from_attributes": True}


class JobDetailOut(JobOut):
    description_html: str | None
    description_text: str | None
    llm_rationale: str | None = None
    matching_skills: list[str] = []
    missing_skills: list[str] = []


class ResumeProfileOut(BaseModel):
    id: int
    uploaded_at: str
    original_filename: str | None
    label: str | None
    is_current: bool
    parsed: dict

    model_config = {"from_attributes": True}


class IngestionRunOut(BaseModel):
    id: int
    started_at: str
    finished_at: str | None
    source: str | None
    jobs_added: int
    jobs_updated: int
    jobs_deactivated: int
    error: str | None

    model_config = {"from_attributes": True}
