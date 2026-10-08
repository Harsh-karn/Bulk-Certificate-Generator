from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job, Certificate
from app.schemas import JobCreateRequest, JobCreatedResponse, JobStatusResponse
from app.services.processor import process_job
import os

router = APIRouter(tags=["jobs"])

@router.post("/jobs", response_model=JobCreatedResponse, status_code=status.HTTP_202_ACCEPTED)
def create_job(request: JobCreateRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job = Job(
        title=request.title,
        issue_date=request.issue_date,
        issuer=request.issuer,
        total_count=len(request.recipients)
    )
    db.add(job)
    db.flush()

    for i, rec in enumerate(request.recipients):
        cert = Certificate(
            job_id=job.id,
            position=i,
            recipient_name=rec.name if rec.name else "",
            recipient_email=rec.email
        )
        db.add(cert)
        
    db.commit()
    db.refresh(job)

    background_tasks.add_task(process_job, job.id)

    return {"job_id": job.id, "message": "Job accepted and is processing."}

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/certificates/{cert_id}/download")
def download_certificate(cert_id: str, db: Session = Depends(get_db)):
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    if cert.status != "success" or not cert.file_path:
        raise HTTPException(status_code=409, detail="Certificate is not ready or failed to generate")
        
    if not os.path.exists(cert.file_path):
        raise HTTPException(status_code=404, detail="Certificate file not found on server")
        
    safe_name = "".join([c for c in cert.recipient_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    filename = f"certificate_{safe_name.replace(' ', '_')}.pdf"
    
    return FileResponse(cert.file_path, filename=filename, media_type='application/pdf')
