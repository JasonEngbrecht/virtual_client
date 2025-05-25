"""
Student API Routes
Endpoints for student operations on course sections
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..services import get_db
from ..services.section_service import section_service
from ..services.enrollment_service import enrollment_service
from ..models.course_section import CourseSection


# Create router instance
router = APIRouter(
    prefix="/student",
    tags=["student"],
    responses={404: {"description": "Not found"}},
)


# Authentication dependency placeholder
async def get_current_student() -> str:
    """
    Get the current authenticated student's ID.
    
    This is a placeholder that returns a mock student ID.
    In production, this would:
    - Validate JWT token or session
    - Extract student ID from the token/session
    - Verify the student exists in the database
    - Return the authenticated student's ID
    
    Returns:
        str: The authenticated student's ID
        
    Raises:
        HTTPException: If authentication fails (not implemented in mock)
    """
    # TODO: Implement real authentication
    # For now, return a mock student ID for testing
    return "student-123"


# GET /sections - List all sections for a student
@router.get("/sections", response_model=List[CourseSection])
async def list_enrolled_sections(
    db: Session = Depends(get_db),
    student_id: str = Depends(get_current_student)
):
    """
    Get all course sections the current student is enrolled in.
    
    Returns:
        List of course sections where the student has active enrollment
    """
    
    # Get all sections for this student (only active enrollments)
    sections = enrollment_service.get_student_sections(db, student_id, include_inactive=False)
    
    return sections


# GET /sections/{section_id} - Get a specific section
@router.get("/sections/{section_id}", response_model=CourseSection)
async def get_enrolled_section(
    section_id: str,
    db: Session = Depends(get_db),
    student_id: str = Depends(get_current_student)
):
    """
    Get details of a specific course section.
    
    Only returns the section if the student is actively enrolled.
    Returns 404 for security if student is not enrolled.
    
    Args:
        section_id: The ID of the section to retrieve
        
    Returns:
        Course section if student is enrolled
        
    Raises:
        404: Section not found or student not enrolled
    """
    
    # First check if student is enrolled
    if not enrollment_service.is_student_enrolled(db, section_id, student_id):
        # Return 404 for security - don't reveal if section exists
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section with ID '{section_id}' not found"
        )
    
    # Get the section details
    section = section_service.get(db, section_id)
    
    # This should not happen if enrollment exists, but check anyway
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section with ID '{section_id}' not found"
        )
    
    return section
