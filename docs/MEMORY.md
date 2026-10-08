# MEMORY — Bulk Certificate Generator

Running project memory: confirmed facts, decisions, and open questions. Update after each work session. Do not record anything unverified as fact.

## 1. Confirmed facts (from the brief)
- Backend API for bulk certificate generation from a single predefined template.
- Python + one of FastAPI / Django+DRF / Flask + a relational database.
- AI tools allowed; the author must understand, explain, and modify the code.
- Required: accept request, validate recipients, generate certificates, track status, check progress, retrieve certificates.
- Failure of one certificate must not unnecessarily block others; job status must show successes and failures.
- Processing may be synchronous or background; the choice and reasoning must be documented.
- Minimum tests: create job, input validation, certificate generation, job status/progress, individual failure, retrieval.
- README must cover: setup, run, tests, submit a request, retrieve certificates, design decisions.
- Interview may ask for explanation, debugging, modification, or handling a changed requirement.

## 2. Decisions made by the author
| Decision | Value | Date |
|---|---|---|
| Framework | FastAPI | 2026-10-07 |

## 3. Proposed, not yet confirmed
| Item | Proposal |
|---|---|
| Database | SQLite via SQLAlchemy |
| PDF library | ReportLab |
| Processing | FastAPI BackgroundTasks, job state in DB |
| Payload | `title`, `issue_date`, `issuer`, `recipients[{name, email?}]` |
| Invalid recipient | Stored as failed certificate with reason; job continues |
| Job statuses | `pending`, `processing`, `completed`, `completed_with_errors`, `failed` |
| Optional feature | ZIP download of a job |

## 4. Not specified by the brief
Payload fields, database choice, certificate format, request size limit, authentication, download style (single/zip). Anything chosen here is an author decision, not a requirement.

## 5. Known trade-offs (be ready to explain)
- BackgroundTasks run inside the app process: a restart mid-job leaves a job in `processing`; no horizontal scaling. A queue like Celery/RQ is the next step if durability is needed.
- SQLite is simple but limited for concurrent writes; switching DB means changing the connection URL and installing the driver.
- Recipient-level validation records failures rather than rejecting the whole request, so clients must inspect per-certificate results.

## 6. Open questions
See "Open decisions" in TASKS.md.

## 7. Session log
| Date | Work done | Next step |
|---|---|---|
| 2026-10-07 | Wrote PRD, ARCHITECTURE, RULES, DESIGN, TASKS, MEMORY. FastAPI chosen. | Start Phase 0 in TASKS.md |

## 8. Interview prep checklist
- [ ] Explain the request lifecycle end to end
- [ ] Justify background processing and its limits
- [ ] Show where failure isolation happens in code
- [ ] Explain how a changed requirement would be handled (e.g. a second template, retry of failed certificates, durable queue)
