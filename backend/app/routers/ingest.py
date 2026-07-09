from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.ingest import run_ingestion
from app.matching.runner import score_new_jobs
from app.models import IngestionRun
from app.schemas import IngestionRunOut

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.post("/run", response_model=list[IngestionRunOut])
def trigger_ingestion(
    source: list[str] | None = Query(default=None), db: Session = Depends(get_db)
) -> list[IngestionRun]:
    runs = run_ingestion(db, sources=source)
    score_new_jobs(db)
    return runs


@router.get("/runs", response_model=list[IngestionRunOut])
def list_runs(db: Session = Depends(get_db)) -> list[IngestionRun]:
    return list(db.scalars(select(IngestionRun).order_by(IngestionRun.id.desc()).limit(50)).all())
