import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

def generate_uuid() -> str:
    """Helper function to generate a unique string ID."""
    return str(uuid.uuid4())

class Job(Base):
    """
    Represents a bulk certificate generation job.
    Tracks the overall status and configuration for the batch.
    """
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    # Status can be: pending, processing, completed, completed_with_errors, failed
    status = Column(String, default="pending") 
    
    title = Column(String, nullable=False)
    issue_date = Column(String, nullable=False)
    issuer = Column(String, nullable=False)
    
    # Progress tracking counters
    total_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    # One-to-many relationship with certificates
    certificates = relationship("Certificate", back_populates="job", cascade="all, delete-orphan")

class Certificate(Base):
    """
    Represents an individual certificate within a bulk generation job.
    Tracks the recipient data and generation outcome.
    """
    __tablename__ = "certificates"

    id = Column(String, primary_key=True, default=generate_uuid)
    job_id = Column(String, ForeignKey("jobs.id"), index=True, nullable=False)
    position = Column(Integer, nullable=False) # Order in the original request
    
    # Recipient data
    recipient_name = Column(String, nullable=False)
    recipient_email = Column(String, nullable=True)
    
    # Generation status: pending, success, failed
    status = Column(String, default="pending") 
    error_message = Column(String, nullable=True) # Reason if generation/validation failed
    file_path = Column(String, nullable=True)     # Path to the generated PDF
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Back reference to the parent Job
    job = relationship("Job", back_populates="certificates")
