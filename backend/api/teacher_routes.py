"""
Teacher API Routes
Endpoints for teacher operations on virtual clients
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from ..services import get_db
from ..services.client_service import client_service
from ..models.client_profile import ClientProfile, ClientProfileCreate, ClientProfileUpdate

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
