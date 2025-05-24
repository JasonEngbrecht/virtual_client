"""
Teacher API Routes
Endpoints for teacher operations on virtual clients
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..services import get_db

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
