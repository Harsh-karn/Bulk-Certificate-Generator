import os
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.domain import JobCreateRequest, JobCreatedResponse, JobStatusResponse
from app.services.job_service import JobService, run_job_processor
from app.repositories.job_repository import JobRepository

router = APIRouter(tags=["jobs"])

def get_job_service(db: Session = Depends(get_db)) -> JobService:
    """Dependency injection to provide JobService to routes."""
    return JobService(db)

def get_job_repository(db: Session = Depends(get_db)) -> JobRepository:
    """Dependency injection to provide JobRepository to routes."""
    return JobRepository(db)

@router.post("/jobs", response_model=JobCreatedResponse, status_code=status.HTTP_202_ACCEPTED)
def create_job(
    request: JobCreateRequest, 
    background_tasks: BackgroundTasks, 
    service: JobService = Depends(get_job_service)
):
    """
    Accepts a bulk generation request.
    Responds immediately (HTTP 202) and queues a background task to process the generation.
    """
    job_id = service.create_and_persist_job(request)
    
    # Schedule the background worker with a dedicated DB session function
    background_tasks.add_task(run_job_processor, job_id)
    
    return {"job_id": job_id, "message": "Job accepted and is processing."}

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str, repo: JobRepository = Depends(get_job_repository)):
    """
    Retrieves the current status and metrics of a job, including all its certificates.
    """
    job = repo.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/certificates/{cert_id}/download")
def download_certificate(cert_id: str, repo: JobRepository = Depends(get_job_repository)):
    """
    Downloads the generated PDF for a specific certificate.
    Throws an error if the certificate failed or is still generating.
    """
    cert = repo.get_certificate_by_id(cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    if cert.status != "success" or not cert.file_path:
        raise HTTPException(status_code=409, detail="Certificate is not ready or failed to generate")
        
    if not os.path.exists(cert.file_path):
        raise HTTPException(status_code=404, detail="Certificate file not found on server")
        
    # Clean the file name for download by stripping special characters
    safe_name = "".join([c for c in cert.recipient_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    filename = f"certificate_{safe_name.replace(' ', '_')}.pdf"
    
    return FileResponse(cert.file_path, filename=filename, media_type='application/pdf')
