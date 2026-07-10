from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import engine, run_migrations
from app.models import Base
from app.routers import ingest, jobs, resume

Base.metadata.create_all(bind=engine)
run_migrations()

app = FastAPI(title="Job Search")

app.include_router(resume.router)
app.include_router(jobs.router)
app.include_router(ingest.router)

frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
