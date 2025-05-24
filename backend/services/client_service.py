"""
Client Service
Handles business logic for client profile operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.client_profile import ClientProfileDB, ClientProfileCreate
from .database import BaseCRUD


class ClientService(BaseCRUD[ClientProfileDB]):
    """
    Service class for client profile operations
    Inherits generic CRUD operations from BaseCRUD
    """
    
    def __init__(self):
        """Initialize client service with ClientProfileDB model"""
        super().__init__(ClientProfileDB)
    
    def get_teacher_clients(
        self,
        db: Session,
        teacher_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ClientProfileDB]:
        """
        Get all clients for a specific teacher
        
        Args:
            db: Database session
            teacher_id: ID of the teacher
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of client profiles created by the teacher
        """
        return self.get_multi(
            db,
            skip=skip,
            limit=limit,
            created_by=teacher_id
        )
    
    def create_client_for_teacher(
        self,
        db: Session,
        client_data: ClientProfileCreate,
        teacher_id: str
    ) -> ClientProfileDB:
        """
        Create a new client profile for a specific teacher
        
        Args:
            db: Database session
            client_data: Client profile data
            teacher_id: ID of the teacher creating the client
            
        Returns:
            Created client profile
        """
        # Convert Pydantic model to dict and add teacher_id
        client_dict = client_data.model_dump()
        client_dict['created_by'] = teacher_id
        
        return self.create(db, **client_dict)
    
    def can_update(
        self,
        db: Session,
        client_id: str,
        teacher_id: str
    ) -> bool:
        """
        Check if a teacher can update a specific client
        
        Args:
            db: Database session
            client_id: ID of the client
            teacher_id: ID of the teacher
            
        Returns:
            True if teacher can update the client, False otherwise
        """
        client = self.get(db, client_id)
        if not client:
            return False
        return client.created_by == teacher_id
    
    def can_delete(
        self,
        db: Session,
        client_id: str,
        teacher_id: str
    ) -> bool:
        """
        Check if a teacher can delete a specific client
        
        Args:
            db: Database session
            client_id: ID of the client
            teacher_id: ID of the teacher
            
        Returns:
            True if teacher can delete the client, False otherwise
        """
        # For now, using same logic as can_update
        # Could be different in the future (e.g., admin override)
        return self.can_update(db, client_id, teacher_id)


# Create global instance
client_service = ClientService()
