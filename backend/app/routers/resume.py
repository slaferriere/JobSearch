import json
import shutil
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import ResumeProfile, utcnow
from app.resume.extract import extract_text
from app.resume.parse_llm import parse_resume
from app.schemas import ResumeProfileOut

router = APIRouter(prefix="/api/resume", tags=["resume"])


@router.post("", response_model=ResumeProfileOut)
def upload_resume(file: UploadFile, db: Session = Depends(get_db)) -> ResumeProfile:
    suffix = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if suffix not in (".pdf", ".docx"):
        raise HTTPException(400, "Only .pdf and .docx resumes are supported")

    dest_path = settings.resumes_dir / f"{uuid.uuid4().hex}{suffix}"
    with dest_path.open("wb") as dest:
        shutil.copyfileobj(file.file, dest)

    raw_text = extract_text(dest_path)
    if not raw_text.strip():
        raise HTTPException(422, "Could not extract any text from this resume file")

    parsed = parse_resume(raw_text)

    db.execute(ResumeProfile.__table__.update().values(is_current=False))
    profile = ResumeProfile(
        uploaded_at=utcnow(),
        original_filename=file.filename,
        file_path=str(dest_path),
        raw_text=raw_text,
        parsed_json=parsed.model_dump_json(),
        profile_summary=parsed.summary,
        is_current=True,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return ResumeProfileOut(
        id=profile.id,
        uploaded_at=profile.uploaded_at,
        original_filename=profile.original_filename,
        parsed=json.loads(profile.parsed_json),
    )


@router.get("", response_model=ResumeProfileOut)
def get_current_resume(db: Session = Depends(get_db)) -> ResumeProfileOut:
    profile = db.scalar(select(ResumeProfile).where(ResumeProfile.is_current.is_(True)))
    if profile is None:
        raise HTTPException(404, "No resume uploaded yet")
    return ResumeProfileOut(
        id=profile.id,
        uploaded_at=profile.uploaded_at,
        original_filename=profile.original_filename,
        parsed=json.loads(profile.parsed_json),
    )
