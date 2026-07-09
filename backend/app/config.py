from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent
DATA_DIR = PROJECT_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_DIR / ".env", extra="ignore")

    anthropic_api_key: str | None = None
    usajobs_api_key: str | None = None
    usajobs_user_agent: str | None = None

    db_path: Path = DATA_DIR / "jobsearch.db"
    resumes_dir: Path = DATA_DIR / "resumes"

    match_model: str = "claude-haiku-4-5-20251001"
    prefilter_top_n: int = 150


settings = Settings()
DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.resumes_dir.mkdir(parents=True, exist_ok=True)
