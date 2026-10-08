from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from app.config import settings

class RecipientInput(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class JobCreateRequest(BaseModel):
    title: str = Field(..., min_length=1)
    issue_date: str = Field(..., min_length=1)
    issuer: str = Field(..., min_length=1)
    recipients: List[RecipientInput] = Field(..., min_length=1)

    @field_validator('recipients')
    @classmethod
    def check_recipient_limit(cls, v):
        if len(v) > settings.max_recipients:
            raise ValueError(f"Too many recipients. Maximum allowed is {settings.max_recipients}.")
        return v

class JobCreatedResponse(BaseModel):
    job_id: str
    message: str

class CertificateResponse(BaseModel):
    id: str
    position: int
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    status: str
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class JobStatusResponse(BaseModel):
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
