# ARCHITECTURE — Bulk Certificate Generator

> Items marked **(proposed)** are the author's design choices; the brief only requires FastAPI, Python, and a relational database.

## 1. Overview
A FastAPI service with a relational database and a local file store for generated PDFs.

```
Client
  │  POST /jobs (recipients + certificate info)
  ▼
FastAPI router ──► Validation ──► Job + Certificate rows (DB)
  │                                        │
  │  202 + job_id                          │ background task
  ▼                                        ▼
Client polls GET /jobs/{id}        Job processor ──► PDF renderer ──► File storage
  │                                        │
  └──────── GET /certificates/{id}/download ◄── DB status + file path
```

## 2. Technology stack
| Layer | Choice | Status |
|---|---|---|
| Language | Python | Given |
| Web framework | FastAPI | Given (author choice among allowed) |
| Database | SQLite (relational) | Proposed |
| ORM | SQLAlchemy | Proposed |
| PDF generation | ReportLab | Proposed |
| Validation | Pydantic (bundled with FastAPI) | Proposed |
| Tests | pytest + FastAPI TestClient | Proposed |
| Server | Uvicorn | Proposed |

## 3. Proposed project layout
```
app/
  main.py            # FastAPI app creation, router registration
  config.py          # settings (DB URL, storage dir, max recipients)
  database.py        # engine, session factory
  models.py          # SQLAlchemy models
  schemas.py         # Pydantic request/response schemas
  routers/
    jobs.py          # job + certificate endpoints
  services/
    validation.py    # per-recipient validation
    generator.py     # certificate PDF rendering (single template)
    processor.py     # runs a job: iterates recipients, isolates failures
  storage/           # generated PDFs (git-ignored)
tests/
README.md
requirements.txt
```

## 4. Data model (proposed)

### `jobs`
| Column | Notes |
|---|---|
| id | UUID primary key |
| status | `pending`, `processing`, `completed`, `completed_with_errors`, `failed` |
| title | certificate title/course/event name |
| issue_date | date printed on certificate |
| issuer | issuing organization name |
| total_count | recipients received |
| success_count | certificates generated |
| failed_count | recipients that failed |
| created_at / updated_at / completed_at | timestamps |

### `certificates`
| Column | Notes |
|---|---|
| id | UUID primary key |
| job_id | FK → jobs.id, indexed |
| position | index of the recipient in the submitted list |
| recipient_name | as submitted |
| recipient_email | optional |
| status | `pending`, `success`, `failed` |
| error_message | reason when failed (validation or generation) |
| file_path | path of generated PDF when success |
| created_at / updated_at | timestamps |

Relationship: one job → many certificates.

## 5. Request lifecycle

1. **Receive** — `POST /jobs`. Pydantic checks the overall shape (recipients list present, not empty, within the configured limit). Shape errors → `422`, nothing stored.
2. **Persist** — create one `jobs` row (`pending`) and one `certificates` row per recipient (`pending`) in a single transaction.
3. **Respond** — return `202 Accepted` with the job ID and a status URL.
4. **Process (background)** — job set to `processing`. For each certificate:
   - validate recipient fields → if invalid, mark `failed` with reason;
   - else render PDF → mark `success` with file path;
   - any exception during one certificate marks only that certificate `failed`; the loop continues.
   - counters are updated as work progresses so polling shows live progress.
5. **Finish** — job status computed from results:
   - all succeeded → `completed`
   - some failed → `completed_with_errors`
   - all failed → `failed`
   - unexpected processor-level crash → `failed`
6. **Retrieve** — client polls the job and downloads certificates by ID.

## 6. Processing model decision (proposed)
**Choice:** FastAPI `BackgroundTasks` with the job tracked in the database.

**Reasoning**
- A request may contain many recipients; generating inline would hold the HTTP request open.
- Requires no extra infrastructure, keeping setup simple for reviewers.
- Status is stored in the DB, so the client can poll without depending on the request.

**Known limitations (to state in README)**
- The task runs in the app process; a server restart mid-job leaves the job in `processing`.
- No horizontal scaling of workers.
- A dedicated queue (e.g. Celery/RQ) would be the next step if durability/scale were required. This is a stated trade-off, not an implemented feature.

## 7. Database sessions in background work
The background task must open its **own** DB session; it must not reuse the request-scoped session, which is closed after the response.

## 8. File storage
- PDFs written under a configurable storage directory.
- File name derived from the certificate ID (not from user input) to avoid path-injection issues.
- The download endpoint reads the path from the DB, never from client input.

## 9. Error handling
| Situation | Behaviour |
|---|---|
| Malformed/empty request | `422`, nothing stored |
| Recipient list over limit | `422` (or `413`; pick one and document it) |
| Invalid single recipient | certificate `failed` with reason; job continues |
| Renderer exception on one certificate | certificate `failed` with reason; job continues |
| Unknown job/certificate ID | `404` |
| Download requested for non-successful certificate | `404` or `409` with clear message (pick one and document it) |
