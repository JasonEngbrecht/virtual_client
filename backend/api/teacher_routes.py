"""
Teacher API Routes
Endpoints for teacher operations on virtual clients
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from ..services import get_db
from ..services.client_service import client_service
from ..services.rubric_service import rubric_service
from ..services.section_service import section_service
from ..services.enrollment_service import enrollment_service
from ..models.client_profile import ClientProfile, ClientProfileCreate, ClientProfileUpdate
from ..models.rubric import EvaluationRubric, EvaluationRubricCreate, EvaluationRubricUpdate
from ..models.course_section import CourseSection, CourseSectionCreate, CourseSectionUpdate, SectionEnrollment, SectionEnrollmentCreate
from ..models.assignment import Assignment, AssignmentCreate, AssignmentUpdate, AssignmentClient, AssignmentClientCreate
from ..services.assignment_service import assignment_service

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


# ==================== ASSIGNMENT ENDPOINTS ====================

# GET /sections/{section_id}/assignments - List assignments in a section
@router.get("/sections/{section_id}/assignments", response_model=List[Assignment])
async def list_section_assignments(
    section_id: str,
    include_draft: bool = True,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Get all assignments for a specific course section.
    
    Only returns assignments if the section belongs to the current teacher.
    
    Args:
        section_id: The ID of the section to get assignments for
        include_draft: Whether to include unpublished (draft) assignments (default: True)
        
    Returns:
        List of assignments in the section
        
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
            detail="You don't have permission to view assignments for this section"
        )
    
    # Get assignments for the section
    assignments = assignment_service.list_section_assignments(
        db, 
        section_id=section_id,
        teacher_id=teacher_id,
        published_only=not include_draft
    )
    
    return assignments


# POST /sections/{section_id}/assignments - Create a new assignment
@router.post("/sections/{section_id}/assignments", response_model=Assignment, status_code=201)
async def create_assignment(
    section_id: str,
    assignment_data: AssignmentCreate,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Create a new assignment for a course section.
    
    Only allows creation if the section belongs to the current teacher.
    The assignment will be created in draft state (unpublished) by default.
    
    Args:
        section_id: The ID of the section to create assignment in
        assignment_data: Assignment data from request body
        
    Returns:
        Created assignment
        
    Raises:
        404: Section not found
        403: Section exists but belongs to another teacher
        400: Invalid assignment data provided
        500: Server error during creation
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
            detail="You don't have permission to create assignments in this section"
        )
    
    try:
        # Create the assignment
        assignment = assignment_service.create_assignment_for_teacher(
            db,
            assignment_data,
            section_id,
            teacher_id
        )
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create assignment"
            )
        
        return assignment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid assignment data: {str(e)}"
        )
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the assignment"
        )


# GET /assignments - List all assignments for teacher
@router.get("/assignments", response_model=List[Assignment])
async def list_teacher_assignments(
    section_id: Optional[str] = None,
    include_draft: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Get all assignments across all sections for the current teacher.
    
    Can optionally filter by a specific section.
    
    Args:
        section_id: Optional - filter to specific section
        include_draft: Whether to include unpublished assignments (default: True)
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of assignments the teacher has created
    """
    
    # Get assignments for this teacher
    assignments = assignment_service.list_teacher_assignments(
        db,
        teacher_id=teacher_id,
        section_id=section_id,
        include_draft=include_draft,
        skip=skip,
        limit=limit
    )
    
    return assignments


# GET /assignments/{assignment_id} - Get a specific assignment
@router.get("/assignments/{assignment_id}", response_model=Assignment)
async def get_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Get a specific assignment by ID.
    
    Only returns the assignment if it belongs to a section owned by the current teacher.
    
    Args:
        assignment_id: The ID of the assignment to retrieve
        
    Returns:
        Assignment if found and teacher has access
        
    Raises:
        404: Assignment not found
        403: Assignment exists but belongs to another teacher's section
    """
    
    # Get the assignment with permission check
    assignment = assignment_service.get(db, assignment_id, teacher_id)
    
    # Check if assignment exists or teacher has access
    if not assignment:
        # Try to get without permission check to determine proper error
        assignment_unchecked = assignment_service.get(db, assignment_id)
        if assignment_unchecked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this assignment"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assignment with ID '{assignment_id}' not found"
            )
    
    return assignment


# PUT /assignments/{assignment_id} - Update an assignment
@router.put("/assignments/{assignment_id}", response_model=Assignment)
async def update_assignment(
    assignment_id: str,
    assignment_data: AssignmentUpdate,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Update an assignment's information.
    
    Only allows updates if the assignment belongs to a section owned by the current teacher.
    Published assignments have limited update capabilities.
    
    Args:
        assignment_id: The ID of the assignment to update
        assignment_data: Updated assignment data (only provided fields will be updated)
        
    Returns:
        Updated assignment
        
    Raises:
        404: Assignment not found
        403: Assignment exists but belongs to another teacher's section
        400: Invalid update data or restricted field update on published assignment
    """
    
    # First check if assignment exists
    assignment = assignment_service.get(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )
    
    # Validate update data
    update_dict = assignment_data.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update"
        )
    
    # Update the assignment with permission check
    try:
        updated_assignment = assignment_service.update(
            db,
            assignment_id,
            assignment_data,
            teacher_id
        )
        
        if not updated_assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this assignment"
            )
        
        return updated_assignment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# DELETE /assignments/{assignment_id} - Delete an assignment
@router.delete("/assignments/{assignment_id}", status_code=204)
async def delete_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Delete an assignment.
    
    Only allows deletion if the assignment belongs to a section owned by the current teacher.
    Cannot delete published assignments - they must be unpublished first.
    
    Args:
        assignment_id: The ID of the assignment to delete
        
    Returns:
        No content (204) on successful deletion
        
    Raises:
        404: Assignment not found
        403: Assignment exists but belongs to another teacher's section
        409: Assignment is published and cannot be deleted
    """
    
    # First check if assignment exists
    assignment = assignment_service.get(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )
    
    # Check if assignment is published
    if assignment.is_published:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a published assignment. Please unpublish it first."
        )
    
    # Delete the assignment with permission check
    try:
        success = assignment_service.delete(db, assignment_id, teacher_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this assignment"
            )
    except HTTPException:
        # Re-raise HTTP exceptions (like 403) without modification
        raise
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the assignment"
        )
    
    # Return 204 No Content on successful deletion
    return None


# POST /assignments/{assignment_id}/publish - Publish an assignment
@router.post("/assignments/{assignment_id}/publish", response_model=Assignment)
async def publish_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Publish an assignment (make it visible to students).
    
    Only allows publishing if the assignment belongs to a section owned by the current teacher.
    The assignment must have at least one active client-rubric pair to be published.
    If the assignment has date constraints, they will be validated.
    
    Args:
        assignment_id: The ID of the assignment to publish
        
    Returns:
        Updated assignment with is_published set to True
        
    Raises:
        404: Assignment not found
        403: Assignment exists but belongs to another teacher's section
        400: Assignment cannot be published (no active clients or invalid dates)
    """
    
    # First check if assignment exists
    assignment = assignment_service.get(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )
    
    # Publish the assignment with permission check
    try:
        published_assignment = assignment_service.publish_assignment(
            db,
            assignment_id,
            teacher_id
        )
        
        if not published_assignment:
            # This means either permission denied or no active clients
            # Check which one to provide appropriate error message
            if not assignment_service.get(db, assignment_id, teacher_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to publish this assignment"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot publish assignment without at least one active client-rubric pair"
                )
        
        return published_assignment
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while publishing the assignment"
        )


# POST /assignments/{assignment_id}/unpublish - Unpublish an assignment
@router.post("/assignments/{assignment_id}/unpublish", response_model=Assignment)
async def unpublish_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Unpublish an assignment (hide it from students).
    
    Only allows unpublishing if the assignment belongs to a section owned by the current teacher.
    This will make the assignment invisible to students but preserve all assignment data.
    
    Args:
        assignment_id: The ID of the assignment to unpublish
        
    Returns:
        Updated assignment with is_published set to False
        
    Raises:
        404: Assignment not found
        403: Assignment exists but belongs to another teacher's section
    """
    
    # First check if assignment exists
    assignment = assignment_service.get(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )
    
    # Unpublish the assignment with permission check
    try:
        unpublished_assignment = assignment_service.unpublish_assignment(
            db,
            assignment_id,
            teacher_id
        )
        
        if not unpublished_assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to unpublish this assignment"
            )
        
        return unpublished_assignment
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while unpublishing the assignment"
        )


# ==================== ASSIGNMENT-CLIENT MANAGEMENT ENDPOINTS ====================

# GET /assignments/{assignment_id}/clients - List clients assigned to an assignment
@router.get("/assignments/{assignment_id}/clients", response_model=List[AssignmentClient])
async def list_assignment_clients(
    assignment_id: str,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Get all clients assigned to an assignment.
    
    Returns both active and inactive client assignments to allow teachers
    to see the complete assignment history.
    
    Args:
        assignment_id: The ID of the assignment
        
    Returns:
        List of assignment-client relationships with client and rubric details
        
    Raises:
        404: Assignment not found
        403: Assignment exists but belongs to another teacher's section
    """
    
    # First check if assignment exists
    assignment = assignment_service.get(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )
    
    # Get assignment clients with permission check
    clients = assignment_service.get_assignment_clients(
        db,
        assignment_id,
        teacher_id
    )
    
    # If empty list returned, check if it's due to permissions
    if not clients and not assignment_service.get(db, assignment_id, teacher_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view clients for this assignment"
        )
    
    # Convert SQLAlchemy objects to dictionaries for proper serialization
    result = []
    for client in clients:
        client_dict = {
            "id": client.id,
            "assignment_id": client.assignment_id,
            "client_id": client.client_id,
            "rubric_id": client.rubric_id,
            "is_active": client.is_active,
            "display_order": client.display_order
        }
        
        # Add nested client data if available
        if hasattr(client, 'client') and client.client:
            client_dict["client"] = {
                "id": client.client.id,
                "name": client.client.name,
                "age": client.client.age,
                "gender": client.client.gender,
                "issues": client.client.issues
            }
        
        # Add nested rubric data if available
        if hasattr(client, 'rubric') and client.rubric:
            client_dict["rubric"] = {
                "id": client.rubric.id,
                "name": client.rubric.name,
                "description": client.rubric.description
            }
        
        result.append(client_dict)
    
    return result


# POST /assignments/{assignment_id}/clients - Add a client to an assignment
@router.post("/assignments/{assignment_id}/clients", response_model=AssignmentClient, status_code=201)
async def add_client_to_assignment(
    assignment_id: str,
    client_data: AssignmentClientCreate,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Add a client with a rubric to an assignment.
    
    If the client was previously assigned and removed (soft deleted),
    this will reactivate the assignment with the new rubric.
    
    Args:
        assignment_id: The ID of the assignment
        client_data: Client ID, rubric ID, and optional display order
        
    Returns:
        Created or reactivated assignment-client relationship
        
    Raises:
        404: Assignment not found
        403: Assignment exists but belongs to another teacher's section
        400: Client or rubric does not belong to teacher, or client already active
    """
    
    # First check if assignment exists
    assignment = assignment_service.get(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )
    
    # Add client to assignment with permission and validation checks
    try:
        assignment_client = assignment_service.add_client_to_assignment(
            db,
            assignment_id=assignment_id,
            client_id=client_data.client_id,
            rubric_id=client_data.rubric_id,
            teacher_id=teacher_id,
            display_order=client_data.display_order
        )
        
        if not assignment_client:
            # This means either permission denied or validation failed
            # Check which one to provide appropriate error message
            if not assignment_service.get(db, assignment_id, teacher_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to manage clients for this assignment"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid client or rubric. Please ensure both belong to you."
                )
        
        # Convert to dict for proper serialization
        result = {
            "id": assignment_client.id,
            "assignment_id": assignment_client.assignment_id,
            "client_id": assignment_client.client_id,
            "rubric_id": assignment_client.rubric_id,
            "is_active": assignment_client.is_active,
            "display_order": assignment_client.display_order
        }
        
        # Add nested client data if available
        if hasattr(assignment_client, 'client') and assignment_client.client:
            result["client"] = {
                "id": assignment_client.client.id,
                "name": assignment_client.client.name,
                "age": assignment_client.client.age,
                "gender": assignment_client.client.gender,
                "issues": assignment_client.client.issues
            }
        
        # Add nested rubric data if available
        if hasattr(assignment_client, 'rubric') and assignment_client.rubric:
            result["rubric"] = {
                "id": assignment_client.rubric.id,
                "name": assignment_client.rubric.name,
                "description": assignment_client.rubric.description
            }
        
        return result
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the client to the assignment"
        )


# PUT /assignments/{assignment_id}/clients/{client_id} - Update assignment client rubric
@router.put("/assignments/{assignment_id}/clients/{client_id}", response_model=AssignmentClient)
async def update_assignment_client(
    assignment_id: str,
    client_id: str,
    rubric_update: Dict[str, str],  # Expects {"rubric_id": "new-rubric-id"}
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Update the rubric for an assignment-client relationship.
    
    Only updates active relationships. If the relationship is soft-deleted,
    use the add endpoint to reactivate it.
    
    Args:
        assignment_id: The ID of the assignment
        client_id: The ID of the client
        rubric_update: Dictionary with new rubric_id
        
    Returns:
        Updated assignment-client relationship
        
    Raises:
        404: Assignment or client relationship not found
        403: Assignment exists but belongs to another teacher's section
        400: Invalid rubric ID or rubric does not belong to teacher
    """
    
    # Validate request body
    if "rubric_id" not in rubric_update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must include 'rubric_id'"
        )
    
    # First check if assignment exists
    assignment = assignment_service.get(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )
    
    # Update the assignment client with permission and validation checks
    try:
        updated_client = assignment_service.update_assignment_client(
            db,
            assignment_id=assignment_id,
            client_id=client_id,
            rubric_id=rubric_update["rubric_id"],
            teacher_id=teacher_id
        )
        
        if not updated_client:
            # This means either permission denied, relationship not found, or validation failed
            # Check which one to provide appropriate error message
            if not assignment_service.get(db, assignment_id, teacher_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to manage clients for this assignment"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No active assignment found for client '{client_id}' in this assignment"
                )
        
        # Convert to dict for proper serialization
        result = {
            "id": updated_client.id,
            "assignment_id": updated_client.assignment_id,
            "client_id": updated_client.client_id,
            "rubric_id": updated_client.rubric_id,
            "is_active": updated_client.is_active,
            "display_order": updated_client.display_order
        }
        
        # Add nested client data if available
        if hasattr(updated_client, 'client') and updated_client.client:
            result["client"] = {
                "id": updated_client.client.id,
                "name": updated_client.client.name,
                "age": updated_client.client.age,
                "gender": updated_client.client.gender,
                "issues": updated_client.client.issues
            }
        
        # Add nested rubric data if available
        if hasattr(updated_client, 'rubric') and updated_client.rubric:
            result["rubric"] = {
                "id": updated_client.rubric.id,
                "name": updated_client.rubric.name,
                "description": updated_client.rubric.description
            }
        
        return result
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the assignment client"
        )


# DELETE /assignments/{assignment_id}/clients/{client_id} - Remove client from assignment
@router.delete("/assignments/{assignment_id}/clients/{client_id}", status_code=204)
async def remove_client_from_assignment(
    assignment_id: str,
    client_id: str,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Remove a client from an assignment (soft delete).
    
    The relationship is soft-deleted to preserve history. The client
    can be re-added later if needed.
    
    Args:
        assignment_id: The ID of the assignment
        client_id: The ID of the client to remove
        
    Returns:
        No content (204) on successful removal
        
    Raises:
        404: Assignment or client relationship not found
        403: Assignment exists but belongs to another teacher's section
    """
    
    # First check if assignment exists
    assignment = assignment_service.get(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )
    
    # Remove the client with permission check
    try:
        success = assignment_service.remove_client_from_assignment(
            db,
            assignment_id=assignment_id,
            client_id=client_id,
            teacher_id=teacher_id
        )
        
        if not success:
            # This means either permission denied or relationship not found
            # Check which one to provide appropriate error message
            if not assignment_service.get(db, assignment_id, teacher_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to manage clients for this assignment"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No active assignment found for client '{client_id}' in this assignment"
                )
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while removing the client from the assignment"
        )
    
    # Return 204 No Content on successful removal
    return None


# POST /assignments/{assignment_id}/clients/bulk - Bulk add clients to assignment
@router.post("/assignments/{assignment_id}/clients/bulk")
async def bulk_add_clients_to_assignment(
    assignment_id: str,
    clients_data: List[AssignmentClientCreate],
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Add multiple clients to an assignment in one operation.
    
    This is more efficient than making multiple individual requests.
    The operation will attempt to add all clients and report which
    ones succeeded and which failed.
    
    Args:
        assignment_id: The ID of the assignment
        clients_data: List of client-rubric pairs to add
        
    Returns:
        Dictionary with 'success' and 'failed' lists of client IDs
        
    Raises:
        404: Assignment not found
        403: Assignment exists but belongs to another teacher's section
        400: Empty client list provided
    """
    
    # Validate request
    if not clients_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one client must be provided"
        )
    
    # First check if assignment exists
    assignment = assignment_service.get(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID '{assignment_id}' not found"
        )
    
    # Bulk add clients with permission and validation checks
    try:
        result = assignment_service.bulk_add_clients(
            db,
            assignment_id=assignment_id,
            clients_data=clients_data,
            teacher_id=teacher_id
        )
        
        # Check if all failed due to permissions
        if not result["success"] and len(result["failed"]) == len(clients_data):
            if not assignment_service.get(db, assignment_id, teacher_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to manage clients for this assignment"
                )
        
        return result
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during bulk client addition"
        )


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


# GET /sections/stats - Get stats for all teacher's sections
# NOTE: This must come before /sections/{section_id} to avoid route conflicts
@router.get("/sections/stats")
async def get_all_sections_stats(
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Get enrollment statistics for all teacher's sections.
    
    Returns statistics including active/inactive enrollment counts
    for each section owned by the teacher.
    
    Returns:
        List of sections with enrollment statistics
    """
    
    # Get statistics for all teacher's sections
    stats = section_service.get_all_sections_stats(db, teacher_id)
    
    return stats


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


# GET /sections/{section_id}/stats - Get stats for a specific section
@router.get("/sections/{section_id}/stats")
async def get_section_stats(
    section_id: str,
    db: Session = Depends(get_db),
    teacher_id: str = Depends(get_current_teacher)
):
    """
    Get enrollment statistics for a specific section.
    
    Only returns statistics if the section belongs to the current teacher.
    
    Args:
        section_id: The ID of the section to get statistics for
        
    Returns:
        Section statistics including active/inactive enrollment counts
        
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
            detail="You don't have permission to view statistics for this section"
        )
    
    # Get the statistics
    stats = section_service.get_section_stats(db, section_id)
    
    # Add section name to the response
    stats["name"] = section.name
    
    return stats


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
        409: Rubric is being used by one or more assignment-client relationships
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
    
    # Check if rubric is in use by any assignment-client relationships
    if rubric_service.is_rubric_in_use(db, rubric_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete rubric '{rubric.name}' because it is being used by one or more assignment-client relationships. Please remove the rubric from those assignments first."
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
