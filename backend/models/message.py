"""
Message Model
Represents individual messages within a conversation session
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from datetime import datetime
import uuid

from ..services.database import Base


# SQLAlchemy ORM Model
class MessageDB(Base):
    """Database model for conversation messages"""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    token_count = Column(Integer, default=0)
    sequence_number = Column(Integer, nullable=False)
    
    # Indexes for performance with high message volume
    __table_args__ = (
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
        Index('idx_session_sequence', 'session_id', 'sequence_number'),
    )
    
    # Relationship to session (optional, for convenience)
    session = relationship("SessionDB", backref="messages")


# Pydantic Models for API
class MessageBase(BaseModel):
    """Base message schema"""
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is not empty or just whitespace"""
        if not v or not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()


class MessageCreate(MessageBase):
    """Schema for creating a new message"""
    token_count: int = Field(0, ge=0)


class Message(MessageBase):
    """Complete message schema with all details"""
    id: str
    session_id: str
    timestamp: datetime
    token_count: int = 0
    sequence_number: int
    
    class Config:
        from_attributes = True
