from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from app.core.config import settings

# ----------------- Request Schemas -----------------

class RecipientInput(BaseModel):
    """
    Data required for a single recipient in the bulk request.
    We allow optional fields here to prevent request-level 422 errors for minor semantic issues.
    Instead, invalid semantic data is caught during background validation to isolate failures.
    """
    name: Optional[str] = None
    email: Optional[str] = None

class JobCreateRequest(BaseModel):
    """
    Payload for creating a new bulk certificate job.
    """
    title: str = Field(..., min_length=1, description="Title of the event or course")
    issue_date: str = Field(..., min_length=1, description="Date of issue")
    issuer: str = Field(..., min_length=1, description="Name of the issuing organization")
    recipients: List[RecipientInput] = Field(..., min_length=1, description="List of recipients")

    @field_validator('recipients')
    @classmethod
    def check_recipient_limit(cls, v):
        """Validates that the bulk request does not exceed the configured maximum size."""
        if len(v) > settings.max_recipients:
            raise ValueError(f"Too many recipients. Maximum allowed is {settings.max_recipients}.")
        return v

# ----------------- Response Schemas -----------------

class JobCreatedResponse(BaseModel):
    """Response returned when a job is successfully accepted."""
    job_id: str
    message: str

class CertificateResponse(BaseModel):
    """Data representation of a single certificate status."""
    id: str
    position: int
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    status: str
    error_message: Optional[str] = None

    class Config:
        from_attributes = True # Allow Pydantic to read from SQLAlchemy ORM models

class JobStatusResponse(BaseModel):
    """Data representation of a job's overall status, including its certificates."""
    id: str
    status: str
    title: str
    issue_date: str
    issuer: str
    total_count: int
    success_count: int
    failed_count: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    certificates: List[CertificateResponse] = []

    class Config:
        from_attributes = True
