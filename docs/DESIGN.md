# DESIGN — Bulk Certificate Generator

> API and certificate design. Field names, status codes, and limits are **proposed** unless the brief says otherwise. The brief does not define a payload format.

## 1. API endpoints

| Method | Path | Purpose | Priority |
|---|---|---|---|
| POST | `/jobs` | Submit a bulk generation request | Required |
| GET | `/jobs/{job_id}` | Job status, counts, per-certificate results | Required |
| GET | `/certificates/{certificate_id}/download` | Download one generated PDF | Required |
| GET | `/jobs/{job_id}/download` | All successful certificates as a ZIP | Optional |

FastAPI also provides interactive docs at `/docs`.

## 2. Create job

**Request** `POST /jobs`
```json
{
  "title": "Python Backend Workshop",
  "issue_date": "2026-10-01",
  "issuer": "Example Organization",
  "recipients": [
    { "name": "Asha Rao", "email": "asha@example.com" },
    { "name": "Ravi Menon" }
  ]
}
```

**Fields (proposed)**
| Field | Required | Rules |
|---|---|---|
| `title` | yes | non-empty string, length-limited |
| `issue_date` | yes | valid ISO date |
| `issuer` | yes | non-empty string, length-limited |
| `recipients` | yes | non-empty list, size ≤ configured max |
| `recipients[].name` | yes | non-empty after trimming, length-limited |
| `recipients[].email` | no | valid email format if present |

**Response** `202 Accepted`
```json
{
  "job_id": "<uuid>",
  "status": "pending",
  "total_count": 2,
  "status_url": "/jobs/<uuid>"
}
```

## 3. Validation design
Two levels:

| Level | Examples | Outcome |
|---|---|---|
| Request-level | missing `recipients`, empty list, list over limit, bad `issue_date`, missing `title` | `422`, no job created |
| Recipient-level | blank name, malformed email, name too long | Certificate row created with `failed` + `error_message`; other recipients still processed |

To allow recipient-level handling, the recipients list is accepted loosely at the schema level and each item is validated individually in the validation service.

## 4. Job status

**Request** `GET /jobs/{job_id}`

**Response** `200`
```json
{
  "job_id": "<uuid>",
  "status": "completed_with_errors",
  "title": "Python Backend Workshop",
  "total_count": 3,
  "success_count": 2,
  "failed_count": 1,
  "created_at": "2026-10-07T10:00:00Z",
  "completed_at": "2026-10-07T10:00:02Z",
  "certificates": [
    { "id": "<uuid>", "position": 0, "recipient_name": "Asha Rao", "status": "success", "error_message": null, "download_url": "/certificates/<uuid>/download" },
    { "id": "<uuid>", "position": 1, "recipient_name": "", "status": "failed", "error_message": "name must not be empty", "download_url": null },
    { "id": "<uuid>", "position": 2, "recipient_name": "Ravi Menon", "status": "success", "error_message": null, "download_url": "/certificates/<uuid>/download" }
  ]
}
```
Progress for a client = `success_count + failed_count` out of `total_count`.

For very large jobs, the certificate list may need pagination; decide during implementation and document it.

### Job status values
| Status | Meaning |
|---|---|
| `pending` | accepted, not started |
| `processing` | background work running |
| `completed` | all certificates succeeded |
| `completed_with_errors` | at least one succeeded and at least one failed |
| `failed` | all failed, or the processor crashed |

### Certificate status values
`pending`, `success`, `failed`

## 5. Download certificate
`GET /certificates/{certificate_id}/download`
- `200` with `application/pdf` and a filename header when status is `success`.
- `404` for unknown ID.
- Non-success certificate: return a clear error (`404` or `409`; choose one and keep it consistent).

## 6. Error response shape (proposed)
Use FastAPI's default `{"detail": ...}` for consistency unless a custom shape is adopted.

## 7. Certificate template (single, predefined)
- Format: PDF, landscape A4 (proposed).
- Static elements: heading ("Certificate of Completion" or similar), decorative border, "This is to certify that" line.
- Dynamic elements, taken from the request:
  - recipient name (prominent)
  - certificate title/course/event
  - issue date
  - issuer
- Layout is fixed in code; no template configuration.
- Long names must not overflow the page (shrink font or truncate; decide and document).
- File name: `<certificate_id>.pdf`.

## 8. Design decisions to be documented in README
1. Why background processing and its limitation (in-process, not durable).
2. Why recipient-level validation records a failure instead of rejecting the request.
3. Why SQLite and how to switch databases.
4. Why PDFs are named by server-generated IDs.
