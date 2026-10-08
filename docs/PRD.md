# PRD — Bulk Certificate Generator

## 1. Purpose
An organization wants to generate certificates for many participants after an event or course. This project is a **backend API** that accepts a bulk certificate request, generates one certificate per valid recipient from a single predefined template, tracks progress, and lets the client retrieve the results.

## 2. Source of truth
Everything in section 3 ("Given requirements") comes directly from the assignment brief. Section 5 lists **proposed decisions** that the brief leaves open. Proposed items are labelled as such and must be documented in the README.

## 3. Given requirements (from the brief)

### Technology
- Python
- One of: FastAPI, Django + DRF, or Flask → **FastAPI chosen**
- A relational database
- Any additional libraries are allowed
- AI tools are allowed, but the author must be able to understand, explain and modify the code

### Functional requirements
1. Accept a certificate generation request.
2. Validate the provided recipient data.
3. Generate a certificate for each valid recipient using a predefined template.
4. Track the generation status.
5. Allow the client to check progress/result of the request.
6. Allow generated certificates to be retrieved.

### Bulk behaviour
- One request carries many recipients (no one-request-per-certificate).
- Processing may be synchronous or background. **The choice and reasoning must be documented.**

### Certificate generation
- A single predefined template; no template editor, no multiple designs.
- Each certificate contains the recipient-specific information from the request.
- Format and library are up to the author.

### Validation and failure handling
- Invalid recipient data must be handled appropriately.
- One failed certificate must not unnecessarily stop other valid certificates in the same job.
- Job status must identify which generations succeeded and which failed.

### Testing (minimum)
- Creating a generation job
- Input validation
- Certificate generation
- Job status/progress
- Handling an individual certificate failure
- Retrieving generated certificates

### Documentation (README must cover)
- Project setup
- Running the application
- Running tests
- Submitting a certificate generation request
- Retrieving generated certificates
- Important implementation/design decisions

### Optional
- Small improvements are allowed but must not come at the cost of required functionality.

### Interview note
The author may be asked to explain the implementation, justify design decisions, debug or modify part of the app, or handle a changed requirement.

## 4. Not specified by the brief (do not assume)
The brief does **not** define:
- The exact fields of the request payload
- Which database to use
- The certificate output format
- Maximum request size
- Authentication/authorization
- Whether certificates must be downloadable individually, as an archive, or both

These are resolved in section 5 as proposals only.

## 5. Proposed decisions (author's choices, to be confirmed and documented)
| Area | Proposal | Reason |
|---|---|---|
| Framework | FastAPI | Stated by the author |
| Database | SQLite via SQLAlchemy | Zero-setup relational DB; swappable by changing the connection URL |
| Certificate format | PDF generated with ReportLab | Standard certificate format; pure Python, no external binaries |
| Processing model | Asynchronous background processing; request returns immediately with a job ID | A request may contain many recipients; avoids long-held HTTP requests |
| Request payload | Job-level certificate info (title, issue date, issuer) + list of recipients (name, optional email) | Minimal data needed to produce a meaningful certificate |
| Invalid recipients | Recorded as failed with a reason; valid ones still generated | Satisfies the failure-isolation requirement |
| Max recipients per request | Configurable limit | Protects the service; exact value is a configuration choice |
| Auth | Out of scope | Not required by the brief |

## 6. API scope (proposed)
**Required**
- Create a job (bulk request)
- Get job status/progress with per-certificate outcome
- Download an individual certificate

**Optional (only after required items are complete)**
- Download all certificates of a job as a ZIP

## 7. Success criteria
- A client can submit N recipients in one request and receive a job ID.
- The client can poll the job and see total / succeeded / failed counts and per-recipient outcome with error reasons.
- Valid recipients get a downloadable certificate even when others in the same job fail.
- All minimum test areas pass.
- README covers every listed item.
- The author can explain and modify every part of the code.

## 8. Out of scope
Template editor, multiple templates, user accounts, email delivery, frontend UI, distributed task queues (unless explicitly adopted later).
