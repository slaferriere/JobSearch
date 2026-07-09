# Job Search

A personal job-search app: pulls listings from Greenhouse, Lever, and USAJobs, scores them against your resume with Claude, and lets you filter/browse in a local web UI. See `.env.example` for required config.

## Setup

```bash
# Backend
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp ../.env.example ../.env   # fill in ANTHROPIC_API_KEY (required), USAJOBS_API_KEY (optional)
.venv/bin/python scripts/init_db.py

# Frontend
cd ../frontend
npm install
```

## Run

```bash
# Terminal 1 — backend (http://localhost:8000)
cd backend && .venv/bin/uvicorn app.main:app --reload

# Terminal 2 — frontend (http://localhost:5173, proxies /api to :8000)
cd frontend && npm run dev
```

Open http://localhost:5173, upload your resume, then click "Refresh listings" (or run the ingestion script below) to pull jobs.

## Ingest jobs manually / on a schedule

```bash
cd backend
.venv/bin/python scripts/run_ingestion.py                       # all sources
.venv/bin/python scripts/run_ingestion.py --source greenhouse --source lever
```

For recurring ingestion without keeping the app open, schedule this script with `launchd` (macOS) or `cron`.

## Editing sources

Company lists live in `backend/app/connectors/registry.py`:
- Greenhouse: find a company's board token from `boards.greenhouse.io/{token}`
- Lever: find a company's slug from `jobs.lever.co/{slug}`
- USAJobs requires a free API key from `developer.usajobs.gov` — federal/govt-adjacent roles, useful if you need clearance-relevant listings (LinkedIn and ClearanceJobs have no public API, so they aren't sourced here).

## Known limits (MVP)

- No LinkedIn/ClearanceJobs sourcing (no public API for either — see above).
- No automated "apply for me" yet — each listing links to the original posting. A future phase adds Claude-drafted cover letters and a Playwright-based form-prefill (never auto-submits) for Greenhouse/Lever hosted apply pages.
- Matching runs synchronously per ingestion; fine at current volume, would move to the Batch API at larger scale.
