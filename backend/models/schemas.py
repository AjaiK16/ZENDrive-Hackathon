from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Mail Digest Models
class EmailItem(BaseModel):
    id: str
    from_email: str = Field(..., description="Sender's email address")
    from_name: str = Field(..., description="Sender's display name")
    subject: str = Field(..., description="Email subject")
    received: str = Field(..., description="ISO timestamp when received")
    importance: str = Field(default="normal", description="Email priority: high, normal, low")
    preview: str = Field(..., description="Email preview text")
    has_attachments: bool = Field(default=False, description="Has file attachments")

class MailDigestResponse(BaseModel):
    feature: str = Field(default="mail_digest", description="Feature identifier")
    unread_count: int = Field(..., description="Total unread emails")
    high_priority_count: int = Field(..., description="High priority emails")
    emails: List[EmailItem] = Field(..., description="List of recent emails")
    summary: str = Field(..., description="AI-generated text summary")
    speech: str = Field(..., description="Voice-optimized summary")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Error Response Model
class ErrorResponse(BaseModel):
    feature: str
    error: str
    message: str
    success: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Health Check Model
class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    timestamp: str
    feature: str = "mail_digest"