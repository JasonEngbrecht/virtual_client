"""
Course Section and Enrollment models for managing teacher-student relationships.

This module defines the database models and Pydantic schemas for course sections
and student enrollments. Course sections are owned by teachers and contain
students through enrollments.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from ..services.database import Base
from pydantic import BaseModel, Field, ConfigDict


# SQLAlchemy Models
class CourseSectionDB(Base):
    """Database model for course sections."""
    __tablename__ = "course_sections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    teacher_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)  # e.g., "SW 101 - Fall 2025"
    description = Column(Text, nullable=True)
    course_code = Column(String, nullable=True)  # e.g., "SW101"
    term = Column(String, nullable=True)  # e.g., "Fall 2025"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    settings = Column(JSON, default=dict)  # section-specific settings
    
    # Relationships
    enrollments = relationship("SectionEnrollmentDB", back_populates="section", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CourseSection(id={self.id}, name='{self.name}', teacher_id='{self.teacher_id}')>"


class SectionEnrollmentDB(Base):
    """Database model for student enrollments in course sections."""
    __tablename__ = "section_enrollments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    section_id = Column(String, ForeignKey("course_sections.id"), nullable=False, index=True)
    student_id = Column(String, nullable=False, index=True)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)  # soft delete for unenrollment
    role = Column(String, default="student")  # future: "ta" for teaching assistants
    
    # Relationships
    section = relationship("CourseSectionDB", back_populates="enrollments")
    
    def __repr__(self):
        return f"<SectionEnrollment(id={self.id}, section_id='{self.section_id}', student_id='{self.student_id}')>"


# Pydantic Schemas
class CourseSectionCreate(BaseModel):
    """Schema for creating a new course section."""
    name: str = Field(..., min_length=1, max_length=200, description="Section name (e.g., 'SW 101 - Fall 2025')")
    description: Optional[str] = Field(None, description="Detailed description of the course section")
    course_code: Optional[str] = Field(None, max_length=20, description="Course code (e.g., 'SW101')")
    term: Optional[str] = Field(None, max_length=50, description="Academic term (e.g., 'Fall 2025')")
    is_active: bool = Field(default=True, description="Whether the section is currently active")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Section-specific settings")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Social Work Practice I - Fall 2025",
            "description": "Introduction to social work practice with individuals and families",
            "course_code": "SW101",
            "term": "Fall 2025",
            "is_active": True,
            "settings": {
                "allow_late_submissions": True,
                "max_attempts_per_assignment": 3
            }
        }
    })


class CourseSectionUpdate(BaseModel):
    """Schema for updating a course section."""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Section name")
    description: Optional[str] = Field(None, description="Detailed description")
    course_code: Optional[str] = Field(None, max_length=20, description="Course code")
    term: Optional[str] = Field(None, max_length=50, description="Academic term")
    is_active: Optional[bool] = Field(None, description="Whether the section is active")
    settings: Optional[Dict[str, Any]] = Field(None, description="Section-specific settings")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "description": "Updated course description with new learning objectives",
            "settings": {
                "allow_late_submissions": False
            }
        }
    })


class CourseSection(BaseModel):
    """Schema for course section responses."""
    id: str = Field(..., description="Unique section identifier")
    teacher_id: str = Field(..., description="ID of the teacher who owns this section")
    name: str = Field(..., description="Section name")
    description: Optional[str] = Field(None, description="Detailed description")
    course_code: Optional[str] = Field(None, description="Course code")
    term: Optional[str] = Field(None, description="Academic term")
    is_active: bool = Field(..., description="Whether the section is active")
    created_at: datetime = Field(..., description="When the section was created")
    settings: Dict[str, Any] = Field(..., description="Section-specific settings")
    
    # These will be added in responses when needed
    enrollment_count: Optional[int] = Field(None, description="Number of enrolled students")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "teacher_id": "teacher-123",
                "name": "Social Work Practice I - Fall 2025",
                "description": "Introduction to social work practice",
                "course_code": "SW101",
                "term": "Fall 2025",
                "is_active": True,
                "created_at": "2025-01-15T10:00:00Z",
                "settings": {},
                "enrollment_count": 25
            }
        }
    )


class SectionEnrollmentCreate(BaseModel):
    """Schema for enrolling a student in a section."""
    student_id: str = Field(..., min_length=1, description="ID of the student to enroll")
    role: str = Field(default="student", pattern="^(student|ta)$", description="Role in the section")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "student_id": "student-456",
            "role": "student"
        }
    })


class SectionEnrollment(BaseModel):
    """Schema for enrollment responses."""
    id: str = Field(..., description="Unique enrollment identifier")
    section_id: str = Field(..., description="ID of the course section")
    student_id: str = Field(..., description="ID of the enrolled student")
    enrolled_at: datetime = Field(..., description="When the student was enrolled")
    is_active: bool = Field(..., description="Whether the enrollment is active")
    role: str = Field(..., description="Student's role in the section")
    
    # Optional fields for enhanced responses
    student_name: Optional[str] = Field(None, description="Name of the student (when available)")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "section_id": "550e8400-e29b-41d4-a716-446655440000",
                "student_id": "student-456",
                "enrolled_at": "2025-01-20T14:30:00Z",
                "is_active": True,
                "role": "student",
                "student_name": "Jane Smith"
            }
        }
    )
