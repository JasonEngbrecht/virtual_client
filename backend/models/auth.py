"""
Auth models for the Virtual Client application.

These are minimal authentication models used for type checking and
representing the current user in the system. In production, these
would integrate with a full authentication system.
"""

from pydantic import BaseModel


class BaseUser(BaseModel):
    """Base user model with common fields."""
    id: str


class StudentAuth(BaseUser):
    """Student authentication model."""
    student_id: str


class TeacherAuth(BaseUser):
    """Teacher authentication model."""
    teacher_id: str
