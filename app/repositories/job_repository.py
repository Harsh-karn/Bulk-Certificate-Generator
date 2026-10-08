from sqlalchemy.orm import Session
from app.models.domain import Job, Certificate
from typing import List, Optional

class JobRepository:
    """
    Repository class handling database interactions for Jobs and Certificates.
    This encapsulates the SQLAlchemy logic away from the business services.
    """
    def __init__(self, db: Session):
        self.db = db
        
    def create_job(self, title: str, issue_date: str, issuer: str, total_count: int) -> Job:
        """Creates a new job record."""
        job = Job(
            title=title,
            issue_date=issue_date,
            issuer=issuer,
            total_count=total_count
        )
        self.db.add(job)
        self.db.flush() # flush to generate the job ID needed for certificates
        return job
        
    def create_certificate(self, job_id: str, position: int, recipient_name: str, recipient_email: Optional[str]) -> Certificate:
        """Creates a new certificate record attached to a job."""
        cert = Certificate(
            job_id=job_id,
            position=position,
            recipient_name=recipient_name if recipient_name else "",
            recipient_email=recipient_email
        )
        self.db.add(cert)
        return cert
        
    def get_job_by_id(self, job_id: str) -> Optional[Job]:
        """Retrieves a job by its ID."""
        return self.db.query(Job).filter(Job.id == job_id).first()
        
    def get_certificates_by_job(self, job_id: str) -> List[Certificate]:
        """Retrieves all certificates for a given job ordered by their original position."""
        return self.db.query(Certificate).filter(Certificate.job_id == job_id).order_by(Certificate.position).all()
        
    def get_certificate_by_id(self, cert_id: str) -> Optional[Certificate]:
        """Retrieves a single certificate by its ID."""
        return self.db.query(Certificate).filter(Certificate.id == cert_id).first()
        
    def commit(self):
        """Commits the current transaction."""
        self.db.commit()
        
    def refresh(self, instance):
        """Refreshes a model instance with state from the database."""
        self.db.refresh(instance)
        
    def rollback(self):
        """Rolls back the current transaction in case of error."""
        self.db.rollback()
