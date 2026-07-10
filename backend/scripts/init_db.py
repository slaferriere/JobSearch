"""Create the SQLite schema. Safe to run repeatedly (create_all is idempotent)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import engine, run_migrations
from app.models import Base

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    run_migrations()
    print("Database schema ready.")
