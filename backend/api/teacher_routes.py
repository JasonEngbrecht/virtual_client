"""
Teacher API Routes
Endpoints for teacher operations on virtual clients
"""

from fastapi import APIRouter, Depends, HTTPException
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
async def list_clients(db: Session = Depends(get_db)):
    """
    Get all clients for the current teacher.
    
    For now, using hardcoded teacher_id until authentication is implemented.
    
    Returns:
        List of client profiles belonging to the teacher
    """
    # TODO: Replace with get_current_teacher() dependency in Part 5
    teacher_id = "teacher-123"
    
    # Get all clients for this teacher
    clients = client_service.get_teacher_clients(db, teacher_id)
    
    return clients


# POST /clients - Create a new client
@router.post("/clients", response_model=ClientProfile, status_code=201)
async def create_client(
    client_data: ClientProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new client for the current teacher.
    
    For now, using hardcoded teacher_id until authentication is implemented.
    
    Args:
        client_data: Client profile data from request body
        
    Returns:
        Created client profile
    """
    # TODO: Replace with get_current_teacher() dependency in Part 5
    teacher_id = "teacher-123"
    
    # Create the client
    client = client_service.create_client_for_teacher(
        db,
        client_data,
        teacher_id
    )
    
    return client


# GET /clients/{client_id} - Get a specific client
@router.get("/clients/{client_id}", response_model=ClientProfile)
async def get_client(
    client_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific client by ID.
    
    Only returns the client if it belongs to the current teacher.
    
    Args:
        client_id: The ID of the client to retrieve
        
    Returns:
        Client profile if found and belongs to teacher
        
    Raises:
        404: Client not found or doesn't belong to teacher
    """
    # TODO: Replace with get_current_teacher() dependency in Part 5
    teacher_id = "teacher-123"
    
    # Get the client
    client = client_service.get(db, client_id)
    
    # Check if client exists
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if client belongs to this teacher
    if client.created_by != teacher_id:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return client


# PUT /clients/{client_id} - Update a client
@router.put("/clients/{client_id}", response_model=ClientProfile)
async def update_client(
    client_id: str,
    client_data: ClientProfileUpdate,
    db: Session = Depends(get_db)
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
        404: Client not found or doesn't belong to teacher
    """
    # TODO: Replace with get_current_teacher() dependency in Part 5
    teacher_id = "teacher-123"
    
    # Check if teacher can update this client
    if not client_service.can_update(db, client_id, teacher_id):
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Update the client
    updated_client = client_service.update(
        db,
        client_id,
        **client_data.model_dump(exclude_unset=True)
    )
    
    if not updated_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return updated_client


# DELETE /clients/{client_id} - Delete a client
@router.delete("/clients/{client_id}", status_code=204)
async def delete_client(
    client_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a client.
    
    Only allows deletion if the client belongs to the current teacher.
    
    Args:
        client_id: The ID of the client to delete
        
    Returns:
        No content (204) on successful deletion
        
    Raises:
        404: Client not found or doesn't belong to teacher
    """
    # TODO: Replace with get_current_teacher() dependency in Part 5
    teacher_id = "teacher-123"
    
    # Check if teacher can delete this client
    if not client_service.can_delete(db, client_id, teacher_id):
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Delete the client
    success = client_service.delete(db, client_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Return 204 No Content on successful deletion
    return None
