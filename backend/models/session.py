"""
Session Model
Represents an interaction session between a student and virtual client
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, Float
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime
import uuid

from ..services.database import Base


# SQLAlchemy ORM Model
class SessionDB(Base):
    """Database model for interaction sessions"""
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, nullable=False)
    client_profile_id = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="active")  # 'active' or 'completed'
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    session_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Pydantic Models for API
class SessionBase(BaseModel):
    """Base session schema"""
    student_id: str
    client_profile_id: str
    session_notes: Optional[str] = None


class SessionCreate(SessionBase):
    """Schema for creating a new session"""
    pass


class SessionUpdate(BaseModel):
    """Schema for updating a session"""
    session_notes: Optional[str] = None
    status: Optional[Literal["active", "completed"]] = None


class Session(SessionBase):
    """Complete session schema with all details"""
    id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: Literal["active", "completed"] = "active"
    total_tokens: int = 0
    estimated_cost: float = 0.0
    
    class Config:
        from_attributes = True


class SessionSummary(BaseModel):
    """Summary view of a session for listings"""
    id: str
    student_id: str
    client_profile_id: str
    client_name: Optional[str] = None  # Populated from join
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: Literal["active", "completed"]
    message_count: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0


class SendMessageRequest(BaseModel):
    """Request schema for sending a message in a session"""
    content: str = Field(..., min_length=1)
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is not empty or just whitespace"""
        if not v or not v.strip():
            raise ValueError('Message content cannot be empty')
        return v


class EndSessionRequest(BaseModel):
    """Request schema for ending a session"""
    session_notes: Optional[str] = None
