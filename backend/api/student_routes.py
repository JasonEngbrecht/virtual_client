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
from ..services.assignment_service import assignment_service
from ..models.course_section import CourseSection
from ..models.assignment import Assignment, AssignmentClient


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


# GET /assignments - List all assignments for a student
@router.get("/assignments", response_model=List[Assignment])
async def list_student_assignments(
    db: Session = Depends(get_db),
    student_id: str = Depends(get_current_student)
):
    """
    Get all assignments available to the current student.
    
    Only returns published assignments from enrolled sections
    that are within their available date range.
    
    Returns:
        List of assignments with section information
    """
    
    # Get all sections the student is enrolled in
    enrolled_sections = enrollment_service.get_student_sections(
        db, student_id, include_inactive=False
    )
    
    if not enrolled_sections:
        return []
    
    # Get section IDs
    section_ids = [section.id for section in enrolled_sections]
    
    # Create a map of section ID to section name for enrichment
    section_map = {section.id: section.name for section in enrolled_sections}
    
    # Get available assignments for these sections
    # This method already filters by:
    # - Published status
    # - available_from date
    # - due_date
    assignments = assignment_service.list_available_assignments(db, section_ids)
    
    # Convert to response models with section names
    response_assignments = []
    for assignment in assignments:
        # Convert to dict and add section name
        assignment_dict = Assignment.model_validate(assignment).model_dump()
        assignment_dict['section_name'] = section_map.get(assignment.section_id)
        
        # Get client count for the assignment
        stats = assignment_service.get_assignment_stats(db, assignment.id)
        assignment_dict['client_count'] = stats['active_clients']
        
        response_assignments.append(Assignment(**assignment_dict))
    
    return response_assignments


# GET /assignments/{assignment_id} - Get a specific assignment
@router.get("/assignments/{assignment_id}", 
           response_model=Assignment,
           responses={
               404: {"description": "Assignment not found or student not enrolled"}
           })
async def get_student_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
    student_id: str = Depends(get_current_student)
):
    """
    Get details of a specific assignment.
    
    Only returns the assignment if:
    - Student is enrolled in the assignment's section
    - Assignment is published
    - Current date is within the assignment's availability window
    
    Args:
        assignment_id: The ID of the assignment to retrieve
        
    Returns:
        Assignment details with section name and client count
        
    Raises:
        404: Assignment not found, student not enrolled, or assignment not available
    """
    
    # First get the assignment
    assignment = assignment_service.get(db, assignment_id)
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )
    
    # Check if student is enrolled in the assignment's section
    if not enrollment_service.is_student_enrolled(db, assignment.section_id, student_id):
        # Return 404 for security - don't reveal assignment exists
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )
    
    # Check if assignment is published
    if not assignment.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )
    
    # Check if assignment is within available date range
    from datetime import datetime
    now = datetime.utcnow()
    
    if assignment.available_from and now < assignment.available_from:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )
    
    if assignment.due_date and now > assignment.due_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )
    
    # Get section details for the name
    section = section_service.get(db, assignment.section_id)
    
    # Convert to response model with enriched data
    assignment_dict = Assignment.model_validate(assignment).model_dump()
    assignment_dict['section_name'] = section.name if section else None
    
    # Get client count
    stats = assignment_service.get_assignment_stats(db, assignment.id)
    assignment_dict['client_count'] = stats['active_clients']
    
    return Assignment(**assignment_dict)


# GET /assignments/{assignment_id}/clients - Get assignment clients
@router.get("/assignments/{assignment_id}/clients", 
           response_model=List[AssignmentClient],
           responses={
               404: {"description": "Assignment not found or student not enrolled"}
           })
async def get_student_assignment_clients(
    assignment_id: str,
    db: Session = Depends(get_db),
    student_id: str = Depends(get_current_student)
):
    """
    Get all clients for a specific assignment.
    
    Only returns clients if:
    - Student is enrolled in the assignment's section
    - Assignment is published
    - Current date is within the assignment's availability window
    
    Args:
        assignment_id: The ID of the assignment
        
    Returns:
        List of assignment clients with client and rubric details
        
    Raises:
        404: Assignment not found, student not enrolled, or assignment not available
    """
    
    # First validate the student can access this assignment
    # This will raise 404 if not authorized
    assignment = await get_student_assignment(assignment_id, db, student_id)
    
    # Get assignment clients (only active ones)
    clients = assignment_service.get_assignment_clients(db, assignment_id, teacher_id=None)
    
    # Filter to only active clients
    active_clients = [client for client in clients if client.is_active]
    
    # Convert to response models with nested data
    response_clients = []
    for client in active_clients:
        client_dict = {
            'id': client.id,
            'assignment_id': client.assignment_id,
            'client_id': client.client_id,
            'rubric_id': client.rubric_id,
            'is_active': client.is_active,
            'display_order': client.display_order
        }
        
        # Add nested client data if available
        if hasattr(client, 'client') and client.client:
            client_dict['client'] = {
                'id': client.client.id,
                'name': client.client.name,
                'age': client.client.age,
                'gender': client.client.gender
            }
        
        # Add nested rubric data if available
        if hasattr(client, 'rubric') and client.rubric:
            client_dict['rubric'] = {
                'id': client.rubric.id,
                'name': client.rubric.name,
                'description': client.rubric.description
            }
        
        response_clients.append(AssignmentClient(**client_dict))
    
    return response_clients


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
