from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Job, Certificate
from app.services.generator import generate_certificate_pdf
from app.services.validation import validate_recipient

def process_job(job_id: str):
    db: Session = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return
        
        job.status = "processing"
        db.commit()
        
        certificates = db.query(Certificate).filter(Certificate.job_id == job_id).order_by(Certificate.position).all()
        
        for cert in certificates:
            try:
                error = validate_recipient(cert.recipient_name, cert.recipient_email)
                if error:
                    cert.status = "failed"
                    cert.error_message = error
                    job.failed_count += 1
                else:
                    filepath = generate_certificate_pdf(
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
                cert.status = "failed"
                cert.error_message = f"Generation failed: {str(e)}"
                job.failed_count += 1
            
            db.commit() # commit per certificate to show progress
            
        job.completed_at = datetime.now(timezone.utc)
        if job.failed_count == 0:
            job.status = "completed"
        elif job.success_count == 0:
            job.status = "failed"
        else:
            job.status = "completed_with_errors"
            
        db.commit()
        
    except Exception as e:
        db.rollback()
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "failed"
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()
