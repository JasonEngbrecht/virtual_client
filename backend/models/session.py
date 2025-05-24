"""
Session Model
Represents an interaction session between a student and virtual client
"""

from sqlalchemy import Column, String, Text, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict
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
    rubric_id = Column(String, nullable=False)
    messages = Column(JSON, default=list)  # List of message objects
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    evaluation_result_id = Column(String, nullable=True)
    session_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Pydantic Models for API
class Message(BaseModel):
    """Individual message in a conversation"""
    role: Literal["student", "client", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict] = None  # For storing additional info like emotion state


class SessionBase(BaseModel):
    """Base session schema"""
    student_id: str
    client_profile_id: str
    rubric_id: str
    session_notes: Optional[str] = None


class SessionCreate(SessionBase):
    """Schema for creating a new session"""
    pass


class SessionUpdate(BaseModel):
    """Schema for updating a session"""
    session_notes: Optional[str] = None
    is_active: Optional[bool] = None


class Session(SessionBase):
    """Complete session schema with all details"""
    id: str
    messages: List[Message] = Field(default_factory=list)
    started_at: datetime
    ended_at: Optional[datetime] = None
    is_active: bool = True
    evaluation_result_id: Optional[str] = None
    
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
    is_active: bool
    message_count: int = 0
    has_evaluation: bool = False


class SendMessageRequest(BaseModel):
    """Request schema for sending a message in a session"""
    content: str = Field(..., min_length=1)
    
    
class SendMessageResponse(BaseModel):
    """Response schema after sending a message"""
    student_message: Message
    client_response: Message
    session_id: str


class EndSessionRequest(BaseModel):
    """Request schema for ending a session"""
    trigger_evaluation: bool = True
    session_notes: Optional[str] = None
