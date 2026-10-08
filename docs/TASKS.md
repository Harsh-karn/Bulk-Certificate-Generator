# TASKS — Bulk Certificate Generator

Legend: `[ ]` not started · `[x]` done. Update this file as work progresses. Tasks marked *(optional)* are not required by the brief.

## Phase 0 — Setup
- [ ] Create repo and virtual environment
- [ ] `requirements.txt` (fastapi, uvicorn, sqlalchemy, reportlab, pytest, httpx, email-validator)
- [ ] `.gitignore` (venv, `.env`, DB file, storage dir, `__pycache__`)
- [ ] Project skeleton (`app/`, `tests/`)
- [ ] `config.py` with DB URL, storage dir, max recipients

## Phase 1 — Data layer
- [ ] `database.py` (engine, session factory, `get_db` dependency)
- [ ] `models.py` — `Job` and `Certificate`
- [ ] Create tables on startup

## Phase 2 — Schemas and validation
- [ ] Pydantic request schema (job-level fields + loose recipients list)
- [ ] Response schemas (job created, job status, certificate item)
- [ ] `validation.py` — per-recipient validation returning an error message or OK

## Phase 3 — Certificate generation
- [ ] `generator.py` — render one PDF from the fixed template
- [ ] Handle long names safely
- [ ] Write PDF to storage using certificate ID as filename

## Phase 4 — Job processing
- [ ] `processor.py` — own DB session, iterate certificates
- [ ] Per-certificate try/except; record failure and continue
- [ ] Update counters as work progresses
- [ ] Compute final job status
- [ ] Handle processor-level crash (mark job `failed`)

## Phase 5 — API
- [ ] `POST /jobs` → 202, persist rows, schedule background task
- [ ] `GET /jobs/{id}` with counts and per-certificate results
- [ ] `GET /certificates/{id}/download`
- [ ] 404 handling; non-success download handling
- [ ] *(optional)* `GET /jobs/{id}/download` ZIP

## Phase 6 — Tests (isolated DB + temp storage)
- [ ] Create job (returns 202 + job ID, rows persisted)
- [ ] Input validation: request-level (422) and recipient-level (failed with reason)
- [ ] Certificate generation: file exists and is a valid PDF
- [ ] Job status/progress: counts and final status values
- [ ] Individual failure: patched renderer fails one recipient, others succeed
- [ ] Retrieval: download returns PDF; unknown ID → 404; failed certificate handled

## Phase 7 — Documentation
- [ ] README: setup
- [ ] README: run the application
- [ ] README: run tests
- [ ] README: submit a request (real `curl` example that was run)
- [ ] README: retrieve certificates (real `curl` example that was run)
- [ ] README: design decisions (processing model + limitations, validation approach, DB choice)

## Phase 8 — Final checks
- [ ] Fresh clone → install → run → test works with README commands only
- [ ] Manually submit a mixed valid/invalid request and inspect results
- [ ] Open generated PDFs and check content
- [ ] Re-read all code; can explain each part
- [ ] Review MEMORY.md for decisions to be ready to justify

## Open decisions (resolve and record in MEMORY.md)
- [ ] Exact max recipients value
- [ ] Status code for over-limit request (`422` vs `413`)
- [ ] Status code for downloading a non-success certificate (`404` vs `409`)
- [ ] Pagination of certificate list in job status
- [ ] Long-name handling (shrink vs truncate)
