"""
Session Service
Handles business logic for conversation session operations
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.session import SessionDB, SessionCreate, SessionUpdate
from .database import BaseCRUD


class SessionService(BaseCRUD[SessionDB]):
    """
    Service class for session operations
    Inherits generic CRUD operations from BaseCRUD
    """
    
    def __init__(self):
        """Initialize session service with SessionDB model"""
        super().__init__(SessionDB)
    
    def create_session(
        self,
        db: Session,
        session_data: SessionCreate,
        student_id: str
    ) -> SessionDB:
        """
        Create a new conversation session
        
        Args:
            db: Database session
            session_data: Session creation data
            student_id: ID of the student creating the session
            
        Returns:
            Created session instance
        """
        # Ensure the student_id in the data matches the authenticated student
        session_dict = session_data.model_dump()
        session_dict['student_id'] = student_id
        session_dict['status'] = 'active'
        session_dict['total_tokens'] = 0
        session_dict['estimated_cost'] = 0.0
        
        return self.create(db, **session_dict)
    
    def get_session(
        self,
        db: Session,
        session_id: str,
        student_id: Optional[str] = None
    ) -> Optional[SessionDB]:
        """
        Get a session by ID with optional student validation
        
        Args:
            db: Database session
            session_id: ID of the session
            student_id: Optional student ID for access validation
            
        Returns:
            Session instance if found and accessible, None otherwise
        """
        session = self.get(db, session_id)
        
        if not session:
            return None
        
        # If student_id provided, validate access
        if student_id and session.student_id != student_id:
            return None
        
        return session
    
    def end_session(
        self,
        db: Session,
        session_id: str,
        student_id: str,
        session_notes: Optional[str] = None
    ) -> Optional[SessionDB]:
        """
        End an active session
        
        Args:
            db: Database session
            session_id: ID of the session to end
            student_id: ID of the student ending the session
            session_notes: Optional notes about the session
            
        Returns:
            Updated session if successful, None otherwise
        """
        # Get session with student validation
        session = self.get_session(db, session_id, student_id)
        
        if not session:
            return None
        
        # Check if session is already completed
        if session.status == 'completed':
            return None
        
        # Update session
        update_data = {
            'status': 'completed',
            'ended_at': datetime.utcnow()
        }
        
        if session_notes:
            update_data['session_notes'] = session_notes
        
        return self.update(db, session_id, **update_data)
    
    def get_student_sessions(
        self,
        db: Session,
        student_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[SessionDB]:
        """
        Get all sessions for a specific student
        
        Args:
            db: Database session
            student_id: ID of the student
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional filter for session status ('active' or 'completed')
            
        Returns:
            List of sessions for the student
        """
        filters = {'student_id': student_id}
        if status:
            filters['status'] = status
        
        return self.get_multi(
            db,
            skip=skip,
            limit=limit,
            **filters
        )
    
    def get_active_session(
        self,
        db: Session,
        student_id: str,
        client_profile_id: str
    ) -> Optional[SessionDB]:
        """
        Get an active session for a student with a specific client
        
        Args:
            db: Database session
            student_id: ID of the student
            client_profile_id: ID of the client profile
            
        Returns:
            Active session if exists, None otherwise
        """
        sessions = self.get_multi(
            db,
            student_id=student_id,
            client_profile_id=client_profile_id,
            status='active',
            limit=1
        )
        
        return sessions[0] if sessions else None
    
    def update_token_count(
        self,
        db: Session,
        session_id: str,
        tokens_used: int,
        cost_incurred: float
    ) -> Optional[SessionDB]:
        """
        Update token count and cost for a session
        
        Args:
            db: Database session
            session_id: ID of the session
            tokens_used: Number of tokens to add
            cost_incurred: Cost to add
            
        Returns:
            Updated session if successful
        """
        session = self.get(db, session_id)
        if not session:
            return None
        
        update_data = {
            'total_tokens': session.total_tokens + tokens_used,
            'estimated_cost': session.estimated_cost + cost_incurred
        }
        
        return self.update(db, session_id, **update_data)


# Create global instance
session_service = SessionService()
