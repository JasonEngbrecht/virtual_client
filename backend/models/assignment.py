"""
Assignment models for managing practice and graded assignments within course sections.

This module defines the database models and Pydantic schemas for assignments
and the assignment-client junction table. Assignments belong to course sections
and can link multiple clients with different rubrics for evaluation.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Literal, TYPE_CHECKING
from uuid import uuid4
from enum import Enum

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator, computed_field

from ..services.database import Base


# Enums
class AssignmentType(str, Enum):
    """Types of assignments available."""
    PRACTICE = "practice"
    GRADED = "graded"


# SQLAlchemy Models
class AssignmentDB(Base):
    """Database model for assignments."""
    __tablename__ = "assignments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    section_id = Column(String, ForeignKey("course_sections.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(SQLEnum(AssignmentType), default=AssignmentType.PRACTICE, nullable=False)
    settings = Column(JSON, default=dict)  # Flexible settings (e.g., time_limit, allow_notes)
    available_from = Column(DateTime, nullable=True)  # When assignment becomes available
    due_date = Column(DateTime, nullable=True)  # When assignment is due
    is_published = Column(Boolean, default=False, nullable=False)
    max_attempts = Column(Integer, nullable=True)  # None = unlimited
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignment_clients = relationship(
        "AssignmentClientDB", 
        back_populates="assignment", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Assignment(id={self.id}, title='{self.title}', section_id='{self.section_id}', type='{self.type.value}')>"


class AssignmentClientDB(Base):
    """Database model for assignment-client junction with rubric."""
    __tablename__ = "assignment_clients"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    assignment_id = Column(String, ForeignKey("assignments.id"), nullable=False, index=True)
    client_id = Column(String, ForeignKey("client_profiles.id"), nullable=False, index=True)
    rubric_id = Column(String, ForeignKey("evaluation_rubrics.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)  # Soft delete support
    display_order = Column(Integer, default=0, nullable=False)  # Order clients appear to students
    
    # Relationships
    assignment = relationship("AssignmentDB", back_populates="assignment_clients")
    client = relationship("ClientProfileDB", foreign_keys=[client_id])
    rubric = relationship("EvaluationRubricDB", foreign_keys=[rubric_id])
    
    def __repr__(self):
        return f"<AssignmentClient(id={self.id}, assignment_id='{self.assignment_id}', client_id='{self.client_id}')>"


# Pydantic Schemas
class AssignmentCreate(BaseModel):
    """Schema for creating a new assignment."""
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=200, 
        description="Assignment title"
    )
    description: Optional[str] = Field(
        None, 
        description="Detailed description of the assignment"
    )
    type: AssignmentType = Field(
        default=AssignmentType.PRACTICE, 
        description="Assignment type: 'practice' or 'graded'"
    )
    settings: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Assignment-specific settings (e.g., time_limit, allow_notes)"
    )
    available_from: Optional[datetime] = Field(
        None, 
        description="When the assignment becomes available to students"
    )
    due_date: Optional[datetime] = Field(
        None, 
        description="Assignment due date"
    )
    is_published: bool = Field(
        default=False, 
        description="Whether the assignment is published and visible to students"
    )
    max_attempts: Optional[int] = Field(
        None, 
        ge=1, 
        description="Maximum number of attempts allowed (null = unlimited)"
    )
    
    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: Optional[datetime], info):
        """Ensure due date is after available_from if both are provided."""
        if v and 'available_from' in info.data:
            available_from = info.data['available_from']
            if available_from and v <= available_from:
                raise ValueError('Due date must be after available_from date')
        return v
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "title": "Client Interview Practice - Module 1",
            "description": "Practice conducting an initial assessment interview with a client experiencing housing insecurity",
            "type": "practice",
            "settings": {
                "time_limit": 30,
                "allow_notes": True,
                "show_rubric": True
            },
            "available_from": "2025-02-01T09:00:00Z",
            "due_date": "2025-02-15T23:59:59Z",
            "is_published": False,
            "max_attempts": 3
        }
    })


class AssignmentUpdate(BaseModel):
    """Schema for updating an assignment."""
    title: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=200, 
        description="Assignment title"
    )
    description: Optional[str] = Field(
        None, 
        description="Detailed description of the assignment"
    )
    type: Optional[AssignmentType] = Field(
        None, 
        description="Assignment type: 'practice' or 'graded'"
    )
    settings: Optional[Dict[str, Any]] = Field(
        None, 
        description="Assignment-specific settings"
    )
    available_from: Optional[datetime] = Field(
        None, 
        description="When the assignment becomes available"
    )
    due_date: Optional[datetime] = Field(
        None, 
        description="Assignment due date"
    )
    is_published: Optional[bool] = Field(
        None, 
        description="Whether the assignment is published"
    )
    max_attempts: Optional[int] = Field(
        None, 
        ge=1, 
        description="Maximum number of attempts allowed"
    )
    
    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: Optional[datetime], info):
        """Ensure due date is after available_from if both are provided."""
        if v and 'available_from' in info.data:
            available_from = info.data['available_from']
            if available_from and v <= available_from:
                raise ValueError('Due date must be after available_from date')
        return v
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "description": "Updated description with new learning objectives",
            "due_date": "2025-02-20T23:59:59Z",
            "is_published": True
        }
    })


class Assignment(BaseModel):
    """Schema for assignment responses."""
    id: str = Field(..., description="Unique assignment identifier")
    section_id: str = Field(..., description="ID of the course section")
    title: str = Field(..., description="Assignment title")
    description: Optional[str] = Field(None, description="Detailed description")
    type: AssignmentType = Field(..., description="Assignment type")
    settings: Dict[str, Any] = Field(..., description="Assignment-specific settings")
    available_from: Optional[datetime] = Field(None, description="When available to students")
    due_date: Optional[datetime] = Field(None, description="Due date")
    is_published: bool = Field(..., description="Whether published to students")
    max_attempts: Optional[int] = Field(None, description="Maximum attempts allowed")
    created_at: datetime = Field(..., description="When the assignment was created")
    updated_at: datetime = Field(..., description="When the assignment was last updated")
    
    # Optional fields for enhanced responses
    client_count: Optional[int] = Field(None, description="Number of clients in this assignment")
    section_name: Optional[str] = Field(None, description="Name of the course section")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "section_id": "660e8400-e29b-41d4-a716-446655440000",
                "title": "Client Interview Practice - Module 1",
                "description": "Practice conducting an initial assessment interview",
                "type": "practice",
                "settings": {"time_limit": 30, "allow_notes": True},
                "available_from": "2025-02-01T09:00:00Z",
                "due_date": "2025-02-15T23:59:59Z",
                "is_published": True,
                "max_attempts": 3,
                "created_at": "2025-01-20T10:00:00Z",
                "updated_at": "2025-01-20T10:00:00Z",
                "client_count": 2,
                "section_name": "SW 101 - Spring 2025"
            }
        }
    )


class AssignmentClientCreate(BaseModel):
    """Schema for adding a client to an assignment."""
    client_id: str = Field(..., description="ID of the client profile")
    rubric_id: str = Field(..., description="ID of the evaluation rubric")
    display_order: int = Field(
        default=0, 
        ge=0, 
        description="Order in which client appears to students"
    )
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "client_id": "client-123",
            "rubric_id": "rubric-456",
            "display_order": 1
        }
    })


class AssignmentClient(BaseModel):
    """Schema for assignment-client relationship responses."""
    id: str = Field(..., description="Unique relationship identifier")
    assignment_id: str = Field(..., description="ID of the assignment")
    client_id: str = Field(..., description="ID of the client profile")
    rubric_id: str = Field(..., description="ID of the evaluation rubric")
    is_active: bool = Field(..., description="Whether this relationship is active")
    display_order: int = Field(..., description="Display order for students")
    
    # Optional fields for enhanced responses - will be populated from relationships
    client: Optional[Dict[str, Any]] = Field(default=None, description="Client profile details")
    rubric: Optional[Dict[str, Any]] = Field(default=None, description="Rubric details")
    
    @computed_field
    @property
    def client_name(self) -> Optional[str]:
        """Get client name from nested client object for backwards compatibility"""
        return self.client.get('name') if self.client else None
    
    @computed_field
    @property
    def rubric_name(self) -> Optional[str]:
        """Get rubric name from nested rubric object for backwards compatibility"""
        return self.rubric.get('name') if self.rubric else None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "assignment_id": "550e8400-e29b-41d4-a716-446655440000",
                "client_id": "client-123",
                "rubric_id": "rubric-456",
                "is_active": True,
                "display_order": 1,
                "client": {
                    "id": "client-123",
                    "name": "Maria Rodriguez",
                    "age": 35,
                    "gender": "Female"
                },
                "rubric": {
                    "id": "rubric-456",
                    "name": "Initial Assessment Rubric",
                    "description": "Rubric for evaluating initial client assessments"
                }
            }
        }
    )


# Predefined settings suggestions
ASSIGNMENT_SETTINGS_SUGGESTIONS = {
    "time_limit": "Time limit in minutes (e.g., 30, 60)",
    "allow_notes": "Whether students can access their notes during the assignment",
    "show_rubric": "Whether to show the evaluation rubric to students before starting",
    "randomize_clients": "Whether to randomize the order of clients for each student",
    "allow_replay": "Whether students can replay their session recordings",
    "require_reflection": "Whether students must submit a reflection after completing",
    "min_interaction_time": "Minimum time in minutes students must spend with each client"
}
