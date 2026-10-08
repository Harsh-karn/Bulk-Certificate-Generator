# Bulk Certificate Generator

A backend API for generating bulk certificates using FastAPI and a relational database.

## Important Implementation/Design Decisions

- **Framework**: FastAPI is chosen for its high performance, built-in Pydantic validation, and modern async support.
- **Database**: SQLite via SQLAlchemy. It's a zero-setup relational database that can easily be swapped out by changing the connection URL in configuration.
- **Processing Model**: Background processing using FastAPI's `BackgroundTasks`. A request may contain many recipients; returning a job ID immediately avoids long-held HTTP requests. Wait-free processing ensures API robustness.
- **Validation Approach**: Top-level malformed requests are rejected immediately with `422 Unprocessable Entity` via Pydantic. Per-recipient semantic validation (e.g., email format, missing name) occurs during processing so that one failed certificate does not stop other valid certificates in the same job.
- **File Storage**: PDFs are written to a local `storage/` directory using ReportLab. The file name is derived from the certificate ID to avoid path-injection issues.

## Setup

1. Clone the repository.
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the FastAPI server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. You can also explore the automatic API documentation at `http://127.0.0.1:8000/docs`.

## Running Tests

Run the test suite using pytest:

```bash
pytest
```

## Submitting a Certificate Generation Request

You can submit a job request with a list of recipients. 

**For Mac/Linux / Git Bash:**
```bash
curl -X POST "http://127.0.0.1:8000/jobs" \
     -H "Content-Type: application/json" \
     -d '{
           "title": "Python Basics Course",
           "issue_date": "2026-10-08",
           "issuer": "Tech Academy",
           "recipients": [
             {"name": "Alice Smith", "email": "alice@example.com"},
             {"name": "Bob Jones"}
           ]
         }'
```

**For Windows PowerShell:**
*(Use `curl.exe` and escape internal quotes)*
```powershell
curl.exe -X POST "http://127.0.0.1:8000/jobs" -H "Content-Type: application/json" -d '{\"title\": \"Python Basics Course\", \"issue_date\": \"2026-10-08\", \"issuer\": \"Tech Academy\", \"recipients\": [{\"name\": \"Alice Smith\", \"email\": \"alice@example.com\"}, {\"name\": \"Bob Jones\"}]}'
```

The response will return a 202 status code and the `job_id`:
```json
{
  "job_id": "uuid-of-the-job",
  "message": "Job accepted and is processing."
}
```

## Checking Job Status

Poll the job status using the `job_id`:

**Mac/Linux:**
```bash
curl "http://127.0.0.1:8000/jobs/<job_id>"
```

**Windows PowerShell:**
```powershell
curl.exe "http://127.0.0.1:8000/jobs/<job_id>"
```

The response will detail the overall progress and the status of each certificate:
```json
{
  "id": "<job_id>",
  "status": "completed",
  ...
  "certificates": [
    {
      "id": "<cert_id>",
      "recipient_name": "Alice Smith",
      "status": "success",
      ...
    }
  ]
}
```

## Retrieving Generated Certificates

Once a certificate's status is `success`, you can download its PDF using its `cert_id`:

**Mac/Linux:**
```bash
curl -O -J "http://127.0.0.1:8000/certificates/<cert_id>/download"
```

**Windows PowerShell:**
```powershell
curl.exe -O -J "http://127.0.0.1:8000/certificates/<cert_id>/download"
```
