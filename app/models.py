import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    status = Column(String, default="pending") # pending, processing, completed, completed_with_errors, failed
    title = Column(String, nullable=False)
    issue_date = Column(String, nullable=False)
    issuer = Column(String, nullable=False)
    total_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    certificates = relationship("Certificate", back_populates="job", cascade="all, delete-orphan")

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String, primary_key=True, default=generate_uuid)
    job_id = Column(String, ForeignKey("jobs.id"), index=True, nullable=False)
    position = Column(Integer, nullable=False)
    recipient_name = Column(String, nullable=False)
    recipient_email = Column(String, nullable=True)
    status = Column(String, default="pending") # pending, success, failed
    error_message = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    job = relationship("Job", back_populates="certificates")
