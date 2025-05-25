"""
Teacher API Routes
Endpoints for teacher operations on virtual clients
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from ..services import get_db
from ..services.client_service import client_service
from ..services.rubric_service import rubric_service
from ..services.section_service import section_service
from ..services.enrollment_service import enrollment_service
from ..models.client_profile import ClientProfile, ClientProfileCreate, ClientProfileUpdate
from ..models.rubric import EvaluationRubric, EvaluationRubricCreate, EvaluationRubricUpdate
from ..models.course_section import CourseSection, CourseSectionCreate, CourseSectionUpdate, SectionEnrollment, SectionEnrollmentCreate

# Create router instance
router = APIRouter(
    prefix="/teacher",
    tags=["teacher"],
    responses={404: {"description": "Not found"}},
)


# Authentication dependency placeholder
async def get_current_teacher() -> str:
    """
    Get the current authenticated teacher's ID.
    
    This is a placeholder that returns a mock teacher ID.
    In production, this would:
    - Validate JWT token or session
    - Extract teacher ID from the token/session
    - Verify the teacher exists in the database
    - Return the authenticated teacher's ID
    
    Returns:
        str: The authenticated teacher's ID
        
    Raises:
        HTTPException: If authentication fails (not implemented in mock)
    """
    # TODO: Implement real authentication
    # For now, return a mock teacher ID for testing
    return "teacher-123"


# Test endpoint to verify router is working
@router.get("/test")
async def test_endpoint() -> Dict[str, str]:
    """
    Test endpoint to verify the teacher router is working
    
    Returns:
        Simple message confirming the endpoint is accessible
    """
    return {
        "message": "Teacher router is working!",
        "status": "ok"
    }


# Database test endpoint
@router.get("/test-db")
async def test_database(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Test endpoint to verify database dependency injection is working
    
    Returns:
        Message confirming database session is available
    """
    # Just verify we can get a database session
    return {
        "message": "Database connection is working!",
        "status": "ok",
        "db_connected": db is not None
    }


# GET /clients - List all clients for a teacher
@router.get("/clients", response_model=List[ClientProfile])
async def list_clients(
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Get all clients for the current teacher.
    
    Returns:
        List of client profiles belonging to the teacher
    """
    
    # Get all clients for this teacher
    clients = client_service.get_teacher_clients(db, teacher_id)
    
    return clients


# POST /clients - Create a new client
@router.post("/clients", response_model=ClientProfile, status_code=201)
async def create_client(
    client_data: ClientProfileCreate,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Create a new client for the current teacher.
    
    Args:
        client_data: Client profile data from request body
        
    Returns:
        Created client profile
        
    Raises:
        400: Invalid client data provided
        500: Server error during creation
    """
    
    try:
        # Create the client
        client = client_service.create_client_for_teacher(
            db,
            client_data,
            teacher_id
        )
        return client
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid client data: {str(e)}"
        )
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the client"
        )


# GET /clients/{client_id} - Get a specific client
@router.get("/clients/{client_id}", response_model=ClientProfile)
async def get_client(
    client_id: str,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Get a specific client by ID.
    
    Only returns the client if it belongs to the current teacher.
    
    Args:
        client_id: The ID of the client to retrieve
        
    Returns:
        Client profile if found and belongs to teacher
        
    Raises:
        404: Client not found
        403: Client exists but belongs to another teacher
    """
    
    # Get the client
    client = client_service.get(db, client_id)
    
    # Check if client exists
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID '{client_id}' not found"
        )
    
    # Check if client belongs to this teacher
    if client.created_by != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this client"
        )
    
    return client


# PUT /clients/{client_id} - Update a client
@router.put("/clients/{client_id}", response_model=ClientProfile)
async def update_client(
    client_id: str,
    client_data: ClientProfileUpdate,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Update a client's information.
    
    Only allows updates if the client belongs to the current teacher.
    
    Args:
        client_id: The ID of the client to update
        client_data: Updated client data (only provided fields will be updated)
        
    Returns:
        Updated client profile
        
    Raises:
        404: Client not found
        403: Client exists but belongs to another teacher
        400: Invalid update data
    """
    
    # First check if client exists
    client = client_service.get(db, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID '{client_id}' not found"
        )
    
    # Then check permissions
    if client.created_by != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this client"
        )
    
    # Validate update data
    update_data = client_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update"
        )
    
    # Update the client
    try:
        updated_client = client_service.update(
            db,
            client_id,
            **update_data
        )
        return updated_client
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# DELETE /clients/{client_id} - Delete a client
@router.delete("/clients/{client_id}", status_code=204)
async def delete_client(
    client_id: str,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Delete a client.
    
    Only allows deletion if the client belongs to the current teacher.
    
    Args:
        client_id: The ID of the client to delete
        
    Returns:
        No content (204) on successful deletion
        
    Raises:
        404: Client not found
        403: Client exists but belongs to another teacher
    """
    
    # First check if client exists
    client = client_service.get(db, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID '{client_id}' not found"
        )
    
    # Then check permissions
    if client.created_by != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this client"
        )
    
    # Delete the client
    try:
        success = client_service.delete(db, client_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete client"
            )
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the client"
        )
    
    # Return 204 No Content on successful deletion
    return None


# ==================== RUBRIC ENDPOINTS ====================

# GET /rubrics - List all rubrics for a teacher
@router.get("/rubrics", response_model=List[EvaluationRubric])
async def list_rubrics(
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Get all evaluation rubrics for the current teacher.
    
    Returns:
        List of evaluation rubrics belonging to the teacher
    """
    
    # Get all rubrics for this teacher
    rubrics = rubric_service.get_teacher_rubrics(db, teacher_id)
    
    return rubrics


# ==================== ENROLLMENT ENDPOINTS ====================

# GET /sections/{section_id}/roster - View enrolled students
@router.get("/sections/{section_id}/roster", response_model=List[SectionEnrollment])
async def get_section_roster(
    section_id: str,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Get the roster of enrolled students for a course section.
    
    Only returns the roster if the section belongs to the current teacher.
    
    Args:
        section_id: The ID of the section to get roster for
        
    Returns:
        List of active enrollments in the section
        
    Raises:
        404: Section not found
        403: Section exists but belongs to another teacher
    """
    
    # First check if section exists
    section = section_service.get(db, section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section with ID '{section_id}' not found"
        )
    
    # Check if section belongs to this teacher
    if section.teacher_id != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this section's roster"
        )
    
    # Get the roster (active enrollments only)
    enrollments = enrollment_service.get_section_roster(db, section_id, include_inactive=False)
    
    return enrollments


# POST /sections/{section_id}/enroll - Enroll a student
@router.post("/sections/{section_id}/enroll", response_model=SectionEnrollment, status_code=201)
async def enroll_student(
    section_id: str,
    enrollment_data: SectionEnrollmentCreate,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Enroll a student in a course section.
    
    Only allows enrollment if the section belongs to the current teacher.
    If the student was previously enrolled and unenrolled, this will reactivate
    their enrollment.
    
    Args:
        section_id: The ID of the section to enroll student in
        enrollment_data: Student ID and role information
        
    Returns:
        Created or reactivated enrollment record
        
    Raises:
        404: Section not found
        403: Section exists but belongs to another teacher
        400: Invalid enrollment data or section doesn't exist
    """
    
    # First check if section exists
    section = section_service.get(db, section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section with ID '{section_id}' not found"
        )
    
    # Check if section belongs to this teacher
    if section.teacher_id != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to manage enrollments for this section"
        )
    
    # Enroll the student
    enrollment = enrollment_service.enroll_student(
        db,
        section_id=section_id,
        student_id=enrollment_data.student_id,
        role=enrollment_data.role
    )
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to enroll student. Please verify the student ID and try again."
        )
    
    return enrollment


# DELETE /sections/{section_id}/enroll/{student_id} - Unenroll a student
@router.delete("/sections/{section_id}/enroll/{student_id}", status_code=204)
async def unenroll_student(
    section_id: str,
    student_id: str,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Unenroll a student from a course section.
    
    Only allows unenrollment if the section belongs to the current teacher.
    Uses soft delete to preserve enrollment history.
    
    Args:
        section_id: The ID of the section
        student_id: The ID of the student to unenroll
        
    Returns:
        No content (204) on successful unenrollment
        
    Raises:
        404: Section not found or student not enrolled
        403: Section exists but belongs to another teacher
    """
    
    # First check if section exists
    section = section_service.get(db, section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section with ID '{section_id}' not found"
        )
    
    # Check if section belongs to this teacher
    if section.teacher_id != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to manage enrollments for this section"
        )
    
    # Unenroll the student
    success = enrollment_service.unenroll_student(db, section_id, student_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student '{student_id}' is not actively enrolled in this section"
        )
    
    # Return 204 No Content on successful unenrollment
    return None


# ==================== SECTION ENDPOINTS ====================

# GET /sections - List all sections for a teacher
@router.get("/sections", response_model=List[CourseSection])
async def list_sections(
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Get all course sections for the current teacher.
    
    Returns:
        List of course sections created by the teacher
    """
    
    # Get all sections for this teacher
    sections = section_service.get_teacher_sections(db, teacher_id)
    
    return sections


# POST /sections - Create a new section
@router.post("/sections", response_model=CourseSection, status_code=201)
async def create_section(
    section_data: CourseSectionCreate,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Create a new course section for the current teacher.
    
    Args:
        section_data: Course section data from request body
        
    Returns:
        Created course section
        
    Raises:
        400: Invalid section data provided
        500: Server error during creation
    """
    
    try:
        # Create the section
        section = section_service.create_section_for_teacher(
            db,
            section_data,
            teacher_id
        )
        return section
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid section data: {str(e)}"
        )
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the section"
        )


# GET /sections/{section_id} - Get a specific section
@router.get("/sections/{section_id}", response_model=CourseSection)
async def get_section(
    section_id: str,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Get a specific course section by ID.
    
    Only returns the section if it belongs to the current teacher.
    
    Args:
        section_id: The ID of the section to retrieve
        
    Returns:
        Course section if found and belongs to teacher
        
    Raises:
        404: Section not found
        403: Section exists but belongs to another teacher
    """
    
    # Get the section
    section = section_service.get(db, section_id)
    
    # Check if section exists
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section with ID '{section_id}' not found"
        )
    
    # Check if section belongs to this teacher
    if section.teacher_id != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this section"
        )
    
    return section


# PUT /sections/{section_id} - Update a section
@router.put("/sections/{section_id}", response_model=CourseSection)
async def update_section(
    section_id: str,
    section_data: CourseSectionUpdate,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Update a course section's information.
    
    Only allows updates if the section belongs to the current teacher.
    Supports partial updates - only provided fields will be updated.
    
    Args:
        section_id: The ID of the section to update
        section_data: Updated section data (only provided fields will be updated)
        
    Returns:
        Updated course section
        
    Raises:
        404: Section not found
        403: Section exists but belongs to another teacher
        400: Invalid update data
    """
    
    # First check if section exists
    section = section_service.get(db, section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section with ID '{section_id}' not found"
        )
    
    # Then check permissions using the service method
    if not section_service.can_update(db, section_id, teacher_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this section"
        )
    
    # Validate update data
    update_data = section_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update"
        )
    
    # Update the section
    try:
        updated_section = section_service.update(
            db,
            section_id,
            **update_data
        )
        return updated_section
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# DELETE /sections/{section_id} - Delete a section
@router.delete("/sections/{section_id}", status_code=204)
async def delete_section(
    section_id: str,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Delete a course section.
    
    Only allows deletion if the section belongs to the current teacher.
    Note: This will cascade delete all enrollments in the section.
    
    Args:
        section_id: The ID of the section to delete
        
    Returns:
        No content (204) on successful deletion
        
    Raises:
        404: Section not found
        403: Section exists but belongs to another teacher
    """
    
    # First check if section exists
    section = section_service.get(db, section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section with ID '{section_id}' not found"
        )
    
    # Then check permissions using the service method
    if not section_service.can_delete(db, section_id, teacher_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this section"
        )
    
    # Delete the section
    try:
        success = section_service.delete(db, section_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete section"
            )
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the section"
        )
    
    # Return 204 No Content on successful deletion
    return None


# DELETE /rubrics/{rubric_id} - Delete a rubric
@router.delete("/rubrics/{rubric_id}", status_code=204)
async def delete_rubric(
    rubric_id: str,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Delete an evaluation rubric.
    
    Only allows deletion if the rubric belongs to the current teacher
    and is not being used by any sessions.
    
    Args:
        rubric_id: The ID of the rubric to delete
        
    Returns:
        No content (204) on successful deletion
        
    Raises:
        404: Rubric not found
        403: Rubric exists but belongs to another teacher
        409: Rubric is being used by one or more sessions
        500: Server error during deletion
    """
    
    # First check if rubric exists
    rubric = rubric_service.get(db, rubric_id)
    if not rubric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rubric with ID '{rubric_id}' not found"
        )
    
    # Then check permissions
    if rubric.created_by != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this rubric"
        )
    
    # Check if rubric is in use by any sessions
    if rubric_service.is_rubric_in_use(db, rubric_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete rubric '{rubric.name}' because it is being used by one or more sessions. Please end or reassign those sessions first."
        )
    
    # Delete the rubric
    try:
        success = rubric_service.delete(db, rubric_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete rubric"
            )
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the rubric"
        )
    
    # Return 204 No Content on successful deletion
    return None


# PUT /rubrics/{rubric_id} - Update a rubric
@router.put("/rubrics/{rubric_id}", response_model=EvaluationRubric)
async def update_rubric(
    rubric_id: str,
    rubric_data: EvaluationRubricUpdate,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Update an evaluation rubric's information.
    
    Only allows updates if the rubric belongs to the current teacher.
    Supports partial updates - only provided fields will be updated.
    
    Args:
        rubric_id: The ID of the rubric to update
        rubric_data: Updated rubric data (only provided fields will be updated)
        
    Returns:
        Updated evaluation rubric
        
    Raises:
        404: Rubric not found
        403: Rubric exists but belongs to another teacher
        400: Invalid update data (e.g., criteria weights don't sum to 1.0)
        422: Validation error from Pydantic
    """
    
    # First check if rubric exists
    rubric = rubric_service.get(db, rubric_id)
    if not rubric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rubric with ID '{rubric_id}' not found"
        )
    
    # Then check permissions
    if rubric.created_by != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this rubric"
        )
    
    # Validate update data
    update_data = rubric_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update"
        )
    
    # Update the rubric
    try:
        # Note: Pydantic validation in EvaluationRubricUpdate handles
        # criteria weight sum validation if criteria are provided
        updated_rubric = rubric_service.update(
            db,
            rubric_id,
            **update_data
        )
        return updated_rubric
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# POST /rubrics - Create a new rubric
@router.post("/rubrics", response_model=EvaluationRubric, status_code=201)
async def create_rubric(
    rubric_data: EvaluationRubricCreate,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Create a new evaluation rubric for the current teacher.
    
    The rubric must include criteria with weights that sum to 1.0.
    
    Args:
        rubric_data: Evaluation rubric data from request body
        
    Returns:
        Created evaluation rubric
        
    Raises:
        400: Invalid rubric data (e.g., criteria weights don't sum to 1.0)
        422: Validation error from Pydantic
        500: Server error during creation
    """
    
    try:
        # Create the rubric
        # Note: Pydantic validation handles criteria weight sum validation
        rubric = rubric_service.create_rubric_for_teacher(
            db,
            rubric_data,
            teacher_id
        )
        return rubric
    except ValueError as e:
        # This could come from service-level validation
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid rubric data: {str(e)}"
        )
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the rubric"
        )


# GET /rubrics/{rubric_id} - Get a specific rubric
@router.get("/rubrics/{rubric_id}", response_model=EvaluationRubric)
async def get_rubric(
    rubric_id: str,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Get a specific evaluation rubric by ID.
    
    Only returns the rubric if it belongs to the current teacher.
    
    Args:
        rubric_id: The ID of the rubric to retrieve
        
    Returns:
        Evaluation rubric if found and belongs to teacher
        
    Raises:
        404: Rubric not found
        403: Rubric exists but belongs to another teacher
    """
    
    # Get the rubric
    rubric = rubric_service.get(db, rubric_id)
    
    # Check if rubric exists
    if not rubric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rubric with ID '{rubric_id}' not found"
        )
    
    # Check if rubric belongs to this teacher
    if rubric.created_by != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this rubric"
        )
    
    return rubric
