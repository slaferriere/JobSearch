# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal, single-user job search app. It ingests listings from Greenhouse, Lever, Workday, and USAJobs, scores them against the user's active resume using the Claude API, and serves a local web UI for filtering/browsing. FastAPI backend + React (Vite) frontend, backed by SQLite. Supports multiple resumes (e.g. targeting different role tracks) with a single "active" one used for scoring/display at a time.

Sourcing is intentionally limited to sources with legitimate public APIs — LinkedIn and ClearanceJobs are explicitly out of scope (no public API for either), as are several large companies confirmed to run proprietary/custom careers platforms with no public API (Lockheed Martin, L3Harris, BAE Systems, Goldman Sachs, Charles Schwab, JPMorgan, Google, Microsoft, Amazon, Apple, Meta, Oracle, IBM — see `connectors/registry.py` header). Do not add scrapers for any of these. Any "apply for me" automation must stop at autofill — never add code that programmatically submits an application.

## Commands

### Backend (`backend/`)
```bash
.venv/bin/pip install -r requirements.txt      # install deps (venv already created at backend/.venv)
.venv/bin/python scripts/init_db.py             # create/update SQLite schema (idempotent)
.venv/bin/uvicorn app.main:app --reload         # run API server on :8000
.venv/bin/python scripts/run_ingestion.py       # ingest all sources + score new jobs against current resume
.venv/bin/python scripts/run_ingestion.py --source greenhouse --source lever --skip-matching
```
No test suite exists yet.

### Frontend (`frontend/`)
```bash
npm install
npm run dev        # Vite dev server on :5173, proxies /api/* to :8000 (see vite.config.ts)
npm run build       # tsc -b && vite build -> dist/ (main.py serves this as static files if present)
npm run lint         # oxlint
npx tsc --noEmit -p tsconfig.app.json   # typecheck only
```

## Architecture

### Data flow
`connectors/*` fetch raw postings from each source's public API → normalize into a common `NormalizedJob` shape (`connectors/base.py`) → `ingest.py` upserts them into the `jobs` table (keyed by `source` + `source_id`), computing a `content_hash` for cross-source duplicate detection and tracking `miss_count`/`is_active` for staleness (a job is deactivated after 2 consecutive ingestion runs where it no longer appears). `matching/runner.py` then prefilters active unscored jobs with a cheap fuzzy-match heuristic (`matching/prefilter.py`, rapidfuzz) and sends only the top N to Claude (`matching/score_llm.py`) for a real fit score — this two-stage design exists to bound LLM cost when a single ingestion run can pull hundreds of jobs. `scripts/run_ingestion.py` and the `POST /api/ingest/run` endpoint both call the same `ingest.run_ingestion()` / `matching.runner.score_new_jobs()` functions, so there is one ingestion/scoring code path regardless of trigger.

### Connectors (`backend/app/connectors/`)
Each source implements the `Connector` ABC (`base.py`): `fetch_normalized() -> list[NormalizedJob]`. Greenhouse and Lever are per-company APIs (no global search), so `registry.py` holds the seed list of company board tokens/slugs — this is the file to edit when adding/removing companies. USAJobs is a real search API (keyword-based) but only activates if `USAJOBS_API_KEY`/`USAJOBS_USER_AGENT` are set in `.env`.

Workday (`workday.py`) covers large enterprises (defense contractors, big banks, big tech) that run their careers site on Workday's public, unauthenticated CXS JSON API. A company's `tenant`/`wd_host`/`site` are **not guessable** from its name — verify by curling `https://{tenant}.{wd_host}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs` (POST, body `{"appliedFacets":{},"limit":5,"offset":0,"searchText":""}`) before adding a `WorkdayCompany` to `registry.py`'s `WORKDAY_COMPANIES`. Unlike Greenhouse/Lever, a single Workday tenant can list thousands of postings, so the connector runs each entry in `WORKDAY_SEARCH_KEYWORDS` as a separate search query (deduped by `externalPath`) and caps results at `MAX_RESULTS_PER_COMPANY` (60) per company — keep that keyword list aligned with whatever role tracks the active/inactive resumes target. Each matched posting requires a second HTTP request (`/wday/cxs/{tenant}/{site}/job/{externalPath}`) to fetch the full description, so a full Workday ingestion pass takes several minutes.

### Resume + matching (`backend/app/resume/`, `backend/app/matching/`)
Resume upload → text extraction (`resume/extract.py`, pdfplumber/pypdf/python-docx) → `resume/parse_llm.py` calls `client.messages.parse()` with a Pydantic `ResumeProfile` schema to get structured fields plus a condensed `summary` string. That `summary` (not the full resume text) is what gets sent as context on every per-job scoring call in `matching/score_llm.py`, to keep scoring cheap.

Multiple resumes can be uploaded (`POST /api/resume` takes an optional `label`, e.g. "Architect"); exactly one is ever "current" (`ResumeProfile.is_current`) and that's the one used for scoring/display everywhere (`get_current_resume()` in `matching/runner.py`). `POST /api/resume/{id}/activate` switches which one is current without re-uploading — both it and a fresh upload trigger `score_new_jobs()` synchronously afterward so switching immediately backfills match scores for any active job not yet scored against that resume (cheap: `MatchScore` rows are keyed by `(job_id, resume_profile_id)`, so scores from a resume's previous stint as "current" are reused, not recomputed).

Model used for both resume parsing and job scoring is set once in `config.py` (`Settings.match_model`, currently `claude-haiku-4-5-20251001`).

### API surface (`backend/app/routers/`)
`resume.py` (upload, get/list/activate resumes), `jobs.py` (list with filters + detail + force-rescore one job), `ingest.py` (trigger ingestion, list ingestion run history). `app/main.py` wires these routers, runs `db.run_migrations()` (a hand-rolled idempotent `ALTER TABLE` for columns added after a database already existed — SQLAlchemy's `create_all` only adds missing *tables*, not columns on existing ones) and, if `frontend/dist/` exists (i.e. `npm run build` has been run), mounts it as static files so the whole app can run as a single `uvicorn` process without a separate frontend server.

### Frontend (`frontend/src/`)
Single-page app, no routing library — `App.tsx` just wraps `pages/HomePage.tsx` in a `QueryClientProvider`. All server state goes through TanStack Query (`api/client.ts` has the fetch wrappers, `api/types.ts` the shared types) — there is no separate global state store. `HomePage` owns the `JobFilters` and `selectedId` state and passes them down to `FilterSidebar`, `JobList`, and `JobDetailPanel`. `ResumeUpload` doubles as the resume switcher: it lists all uploaded resumes (`GET /api/resume/all`) in a dropdown and calls `activate` on selection.

## Known gaps (by design, not oversights)

- No LinkedIn/ClearanceJobs connector — neither has a public API.
- No automated application submission — `JobDetailPanel` links out to `apply_url`; a future Playwright-based autofill (Greenhouse/Lever hosted apply pages only) is scoped to fill fields and stop, never to locate/click a submit control.
- Matching is synchronous per-job today; would move to the Anthropic Batch API if ingestion volume grows enough to matter.
- No scheduled/recurring ingestion yet (manual trigger only) — the intended mechanism is macOS `launchd` calling `scripts/run_ingestion.py`, not an in-process scheduler, so ingestion keeps working even when the app isn't open.
