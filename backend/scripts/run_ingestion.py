"""Manual or scheduled (launchd) ingestion entry point.

Usage:
    python scripts/run_ingestion.py                       # all sources
    python scripts/run_ingestion.py --source greenhouse --source lever
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import SessionLocal, engine
from app.ingest import run_ingestion
from app.matching.runner import score_new_jobs
from app.models import Base


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", dest="sources", default=None)
    parser.add_argument("--skip-matching", action="store_true")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        runs = run_ingestion(db, sources=args.sources)
        for run in runs:
            status = f"error: {run.error}" if run.error else "ok"
            print(
                f"[{run.source}] added={run.jobs_added} updated={run.jobs_updated} "
                f"deactivated={run.jobs_deactivated} ({status})"
            )
        if not args.skip_matching:
            scored = score_new_jobs(db)
            print(f"Scored {scored} new jobs against current resume.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
