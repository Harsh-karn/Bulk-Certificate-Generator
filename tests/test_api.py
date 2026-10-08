from fastapi.testclient import TestClient
from app.services import processor

def test_create_job(client: TestClient, db, monkeypatch):
    monkeypatch.setattr(processor, "SessionLocal", lambda: db)
    
    payload = {
        "title": "Python Basics",
        "issue_date": "2023-10-01",
        "issuer": "Tech Academy",
        "recipients": [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob"}
        ]
    }
    
    response = client.post("/jobs", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    
    job_id = data["job_id"]
    
    # Check status
    res = client.get(f"/jobs/{job_id}")
    assert res.status_code == 200
    job_data = res.json()
    assert job_data["status"] == "completed"
    assert job_data["total_count"] == 2
    assert job_data["success_count"] == 2
    assert job_data["failed_count"] == 0
    assert len(job_data["certificates"]) == 2
    
    cert_id = job_data["certificates"][0]["id"]
    
    # Download
    download_res = client.get(f"/certificates/{cert_id}/download")
    assert download_res.status_code == 200
    assert download_res.headers["content-type"] == "application/pdf"

def test_input_validation(client: TestClient):
    payload = {
        "title": "",
        "issue_date": "2023-10-01",
        "issuer": "Tech Academy",
        "recipients": []
    }
    response = client.post("/jobs", json=payload)
    assert response.status_code == 422
    
def test_recipient_validation(client: TestClient, db, monkeypatch):
    monkeypatch.setattr(processor, "SessionLocal", lambda: db)
    payload = {
        "title": "Python Basics",
        "issue_date": "2023-10-01",
        "issuer": "Tech Academy",
        "recipients": [
            {"name": "   ", "email": "invalid-email"}, # both fail
            {"name": "Valid User"}
        ]
    }
    response = client.post("/jobs", json=payload)
    job_id = response.json()["job_id"]
    
    res = client.get(f"/jobs/{job_id}")
    job_data = res.json()
    assert job_data["status"] == "completed_with_errors"
    assert job_data["success_count"] == 1
    assert job_data["failed_count"] == 1

def test_individual_failure_on_generate(client: TestClient, db, monkeypatch):
    monkeypatch.setattr(processor, "SessionLocal", lambda: db)
    
    original_generate = processor.generate_certificate_pdf
    
    def mocked_generate(cert_id, recipient_name, title, issue_date, issuer):
        if recipient_name == "Fail User":
            raise Exception("Mock generation error")
        return original_generate(cert_id, recipient_name, title, issue_date, issuer)
        
    monkeypatch.setattr(processor, "generate_certificate_pdf", mocked_generate)
    
    payload = {
        "title": "Test",
        "issue_date": "2023",
        "issuer": "Org",
        "recipients": [
            {"name": "Good User"},
            {"name": "Fail User"}
        ]
    }
    response = client.post("/jobs", json=payload)
    job_id = response.json()["job_id"]
    
    res = client.get(f"/jobs/{job_id}")
    job_data = res.json()
    assert job_data["status"] == "completed_with_errors"
    assert job_data["success_count"] == 1
    assert job_data["failed_count"] == 1
    
    failed = next(c for c in job_data["certificates"] if c["recipient_name"] == "Fail User")
    assert "Mock generation error" in failed["error_message"]

def test_404_not_found(client: TestClient):
    res = client.get("/jobs/invalid_id")
    assert res.status_code == 404
    
    res = client.get("/certificates/invalid_id/download")
    assert res.status_code == 404
