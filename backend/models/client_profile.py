"""
Client Profile Model
Represents a virtual client with demographics, issues, and personality traits
"""

from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

Base = declarative_base()


# SQLAlchemy ORM Model
class ClientProfileDB(Base):
    """Database model for client profiles"""
    __tablename__ = "client_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    race = Column(String(50))
    gender = Column(String(50))
    socioeconomic_status = Column(String(50))
    issues = Column(JSON)  # List of issues stored as JSON
    background_story = Column(Text)
    personality_traits = Column(JSON)  # List of traits stored as JSON
    communication_style = Column(String(100))
    created_by = Column(String, nullable=False)  # Teacher ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Pydantic Models for API
class ClientProfileBase(BaseModel):
    """Base client profile schema"""
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=1, le=120)
    race: Optional[str] = None
    gender: Optional[str] = None
    socioeconomic_status: Optional[str] = None
    issues: List[str] = Field(default_factory=list)
    background_story: Optional[str] = None
    personality_traits: List[str] = Field(default_factory=list)
    communication_style: Optional[str] = None


class ClientProfileCreate(ClientProfileBase):
    """Schema for creating a new client profile"""
    pass


class ClientProfileUpdate(BaseModel):
    """Schema for updating a client profile"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=1, le=120)
    race: Optional[str] = None
    gender: Optional[str] = None
    socioeconomic_status: Optional[str] = None
    issues: Optional[List[str]] = None
    background_story: Optional[str] = None
    personality_traits: Optional[List[str]] = None
    communication_style: Optional[str] = None


class ClientProfile(ClientProfileBase):
    """Complete client profile schema with metadata"""
    id: str
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Predefined options for client creation
PREDEFINED_ISSUES = [
    "housing_insecurity",
    "substance_abuse",
    "mental_health",
    "domestic_violence",
    "unemployment",
    "family_conflict",
    "grief_loss",
    "chronic_illness",
    "disability",
    "immigration_status",
    "food_insecurity",
    "childcare_needs",
    "elder_care",
    "trauma_history",
    "financial_crisis"
]

PERSONALITY_TRAITS = [
    "defensive",
    "anxious",
    "withdrawn",
    "aggressive",
    "cooperative",
    "suspicious",
    "optimistic",
    "pessimistic",
    "talkative",
    "reserved",
    "emotional",
    "stoic",
    "manipulative",
    "honest",
    "confused"
]

COMMUNICATION_STYLES = [
    "direct",
    "indirect",
    "formal",
    "casual",
    "verbose",
    "brief",
    "emotional",
    "logical",
    "confrontational",
    "avoidant"
]
