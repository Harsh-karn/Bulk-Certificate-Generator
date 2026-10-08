import traceback
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.job_repository import JobRepository
from app.services.generator import CertificateGenerator
from app.services.validation import ValidationService
from app.schemas.domain import JobCreateRequest

class JobService:
    """
    Business logic for processing Bulk Certificate Jobs.
    Abstracts orchestration of the Repository, Validation, and Generation away from the API routing layer.
    """
    
    def __init__(self, db: Session):
        self.repo = JobRepository(db)
        
    def create_and_persist_job(self, request: JobCreateRequest) -> str:
        """
        Takes the validated Pydantic request and persists the job and its pending certificates.
        Returns the generated Job ID.
        """
        # Create Job
        job = self.repo.create_job(
            title=request.title, 
            issue_date=request.issue_date, 
            issuer=request.issuer, 
            total_count=len(request.recipients)
        )
        
        # Insert all certificates as pending
        for idx, recipient in enumerate(request.recipients):
            self.repo.create_certificate(
                job_id=job.id, 
                position=idx, 
                recipient_name=recipient.name, 
                recipient_email=recipient.email
            )
            
        self.repo.commit()
        return job.id

    def process_job_background(self, job_id: str):
        """
        Executes the long-running generation process.
        Iterates over all pending certificates for the job, validates them, and generates PDFs.
        Exceptions thrown here are captured to avoid breaking the background thread.
        """
        try:
            job = self.repo.get_job_by_id(job_id)
            if not job:
                return # If job is not found, nothing to process
                
            job.status = "processing"
            self.repo.commit()
            
            certificates = self.repo.get_certificates_by_job(job_id)
            
            # Process each certificate individually to ensure one failure doesn't halt the rest
            for cert in certificates:
                try:
                    # 1. Semantic Validation
                    error = ValidationService.validate_recipient(cert.recipient_name, cert.recipient_email)
                    if error:
                        cert.status = "failed"
                        cert.error_message = error
                        job.failed_count += 1
                    else:
                        # 2. PDF Generation
                        filepath = CertificateGenerator.generate_pdf(
                            cert_id=cert.id,
                            recipient_name=cert.recipient_name,
                            title=job.title,
                            issue_date=job.issue_date,
                            issuer=job.issuer
                        )
                        cert.status = "success"
                        cert.file_path = filepath
                        job.success_count += 1
                        
                except Exception as e:
                    # Catch generation errors
                    cert.status = "failed"
                    cert.error_message = f"Generation failed: {str(e)}"
                    job.failed_count += 1
                
                # Commit progress after each certificate so clients can poll live progress
                self.repo.commit()
                
            # Compute final Job outcome
            job.completed_at = datetime.now(timezone.utc)
            if job.failed_count == 0:
                job.status = "completed"
            elif job.success_count == 0:
                job.status = "failed"
            else:
                job.status = "completed_with_errors"
                
            self.repo.commit()
            
        except Exception:
            # Fatal error inside the processor (e.g. DB connection dropped midway)
            self.repo.rollback()
            job = self.repo.get_job_by_id(job_id)
            if job:
                job.status = "failed"
                job.completed_at = datetime.now(timezone.utc)
                self.repo.commit()

# Utility to instantiate a new JobService for background tasks which require their own distinct DB session
def run_job_processor(job_id: str):
    """
    Isolated entrypoint for FastAPI BackgroundTasks.
    Creates a new DB session strictly for the background thread to avoid closing/sharing issues with the main request thread.
    """
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        service = JobService(db)
        service.process_job_background(job_id)
    finally:
        db.close()
