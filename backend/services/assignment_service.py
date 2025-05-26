"""
Assignment Service
Handles business logic for assignment operations within course sections
"""

from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case
from ..models.assignment import (
    AssignmentDB, AssignmentClientDB, AssignmentCreate, AssignmentUpdate,
    AssignmentType, AssignmentClientCreate
)
from ..models.course_section import CourseSectionDB
from ..models.client_profile import ClientProfileDB
from ..models.rubric import EvaluationRubricDB
from .database import BaseCRUD
from .section_service import section_service
from .client_service import client_service
from .rubric_service import rubric_service
import logging

logger = logging.getLogger(__name__)


class AssignmentService(BaseCRUD[AssignmentDB]):
    """
    Service class for assignment operations
    Manages assignments within course sections with teacher permissions
    """
    
    def __init__(self):
        """Initialize assignment service with AssignmentDB model"""
        super().__init__(AssignmentDB)
    
    def create_assignment_for_teacher(
        self,
        db: Session,
        assignment_data: AssignmentCreate,
        section_id: str,
        teacher_id: str
    ) -> Optional[AssignmentDB]:
        """
        Create a new assignment for a specific section
        
        Args:
            db: Database session
            assignment_data: Assignment data
            section_id: ID of the course section
            teacher_id: ID of the teacher creating the assignment
            
        Returns:
            Created assignment or None if unauthorized
            
        Business Rules:
            - Teacher must own the section
            - Validates date logic (due_date after available_from)
            - Defaults to draft state (is_published=False)
        """
        # Check if teacher owns the section
        if not section_service.can_update(db, section_id, teacher_id):
            logger.warning(f"Teacher {teacher_id} cannot create assignment for section {section_id}")
            return None
        
        # Convert Pydantic model to dict and add section_id
        assignment_dict = assignment_data.model_dump()
        assignment_dict['section_id'] = section_id
        
        # Create the assignment
        assignment = self.create(db, **assignment_dict)
        logger.info(f"Created assignment {assignment.id} for section {section_id}")
        return assignment
    
    def get(
        self,
        db: Session,
        assignment_id: str,
        teacher_id: Optional[str] = None
    ) -> Optional[AssignmentDB]:
        """
        Get an assignment by ID with optional permission check
        
        Args:
            db: Database session
            assignment_id: ID of the assignment
            teacher_id: If provided, checks if teacher owns the assignment's section
            
        Returns:
            Assignment or None if not found/unauthorized
        """
        assignment = super().get(db, assignment_id)
        if not assignment:
            return None
        
        # If teacher_id provided, check ownership
        if teacher_id and not section_service.can_update(db, assignment.section_id, teacher_id):
            logger.warning(f"Teacher {teacher_id} cannot access assignment {assignment_id}")
            return None
        
        return assignment
    
    def update(
        self,
        db: Session,
        assignment_id: str,
        update_data: AssignmentUpdate,
        teacher_id: str
    ) -> Optional[AssignmentDB]:
        """
        Update an assignment with permission check
        
        Args:
            db: Database session
            assignment_id: ID of the assignment to update
            update_data: Fields to update
            teacher_id: ID of the teacher making the update
            
        Returns:
            Updated assignment or None if unauthorized/not found
            
        Business Rules:
            - Teacher must own the section
            - Cannot change certain fields on published assignments
            - Validates date logic if dates are updated
        """
        assignment = self.get(db, assignment_id)
        if not assignment:
            return None
        
        # Check teacher owns the section
        if not section_service.can_update(db, assignment.section_id, teacher_id):
            logger.warning(f"Teacher {teacher_id} cannot update assignment {assignment_id}")
            return None
        
        # Business rule: Limited updates on published assignments
        if assignment.is_published:
            # Only allow certain updates on published assignments
            allowed_updates = {
                'description', 'due_date', 'max_attempts', 'is_published'
            }
            update_dict = update_data.model_dump(exclude_unset=True)
            
            # Check if trying to update restricted fields
            restricted_updates = set(update_dict.keys()) - allowed_updates
            if restricted_updates:
                logger.warning(
                    f"Cannot update fields {restricted_updates} on published assignment {assignment_id}"
                )
                # Remove restricted fields from update
                for field in restricted_updates:
                    update_dict.pop(field, None)
            
            # Apply filtered updates
            return super().update(db, assignment_id, **update_dict)
        
        # For draft assignments, allow all updates
        return super().update(db, assignment_id, **update_data.model_dump(exclude_unset=True))
    
    def delete(
        self,
        db: Session,
        assignment_id: str,
        teacher_id: str
    ) -> bool:
        """
        Delete an assignment with permission check
        
        Args:
            db: Database session
            assignment_id: ID of the assignment to delete
            teacher_id: ID of the teacher attempting deletion
            
        Returns:
            True if deleted, False if unauthorized/not found
            
        Business Rules:
            - Teacher must own the section
            - Cannot delete published assignments (must unpublish first)
            - Cascade deletes assignment-client relationships
        """
        assignment = self.get(db, assignment_id)
        if not assignment:
            return False
        
        # Check teacher owns the section
        if not section_service.can_delete(db, assignment.section_id, teacher_id):
            logger.warning(f"Teacher {teacher_id} cannot delete assignment {assignment_id}")
            return False
        
        # Cannot delete published assignments
        if assignment.is_published:
            logger.warning(f"Cannot delete published assignment {assignment_id}")
            return False
        
        # Delete will cascade to assignment_clients
        return super().delete(db, assignment_id)
    
    def list_teacher_assignments(
        self,
        db: Session,
        teacher_id: str,
        section_id: Optional[str] = None,
        include_draft: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[AssignmentDB]:
        """
        List assignments for a teacher's sections
        
        Args:
            db: Database session
            teacher_id: ID of the teacher
            section_id: Optional - filter to specific section
            include_draft: Whether to include unpublished assignments
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of assignments the teacher has access to
        """
        query = db.query(AssignmentDB).join(
            CourseSectionDB,
            AssignmentDB.section_id == CourseSectionDB.id
        ).filter(
            CourseSectionDB.teacher_id == teacher_id
        )
        
        # Filter by specific section if provided
        if section_id:
            query = query.filter(AssignmentDB.section_id == section_id)
        
        # Filter by published state
        if not include_draft:
            query = query.filter(AssignmentDB.is_published == True)
        
        # Order by created date (newest first)
        assignments = query.order_by(
            AssignmentDB.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        logger.debug(f"Retrieved {len(assignments)} assignments for teacher {teacher_id}")
        return assignments
    
    def get_assignment_clients(
        self,
        db: Session,
        assignment_id: str,
        teacher_id: str
    ) -> List[AssignmentClientDB]:
        """
        Get all clients assigned to an assignment
        
        Args:
            db: Database session
            assignment_id: ID of the assignment
            teacher_id: ID of the teacher
            
        Returns:
            List of assignment-client relationships with client and rubric details
            
        Business Rules:
            - Teacher must own the section
            - Returns both active and inactive clients
        """
        assignment = self.get(db, assignment_id, teacher_id)
        if not assignment:
            return []
        
        # Get assignment clients with joined client and rubric data
        clients = db.query(AssignmentClientDB).options(
            joinedload(AssignmentClientDB.client),
            joinedload(AssignmentClientDB.rubric)
        ).filter(
            AssignmentClientDB.assignment_id == assignment_id
        ).order_by(
            AssignmentClientDB.display_order.asc(),
            AssignmentClientDB.id.asc()
        ).all()
        
        logger.debug(f"Retrieved {len(clients)} clients for assignment {assignment_id}")
        return clients
    
    def add_client_to_assignment(
        self,
        db: Session,
        assignment_id: str,
        client_id: str,
        rubric_id: str,
        teacher_id: str,
        display_order: Optional[int] = None
    ) -> Optional[AssignmentClientDB]:
        """
        Add a client with rubric to an assignment
        
        Args:
            db: Database session
            assignment_id: ID of the assignment
            client_id: ID of the client to add
            rubric_id: ID of the rubric to use
            teacher_id: ID of the teacher
            display_order: Optional display order
            
        Returns:
            Created assignment-client relationship or None if unauthorized
            
        Business Rules:
            - Teacher must own the section
            - Client must belong to teacher
            - Rubric must belong to teacher
            - Reactivates if soft-deleted relationship exists
        """
        # Check assignment ownership
        assignment = self.get(db, assignment_id, teacher_id)
        if not assignment:
            logger.warning(f"Teacher {teacher_id} cannot access assignment {assignment_id}")
            return None
        
        # Validate client belongs to teacher
        client = client_service.get(db, client_id)
        if not client or client.created_by != teacher_id:
            logger.warning(f"Client {client_id} does not belong to teacher {teacher_id}")
            return None
        
        # Validate rubric belongs to teacher
        rubric = rubric_service.get(db, rubric_id)
        if not rubric or rubric.created_by != teacher_id:
            logger.warning(f"Rubric {rubric_id} does not belong to teacher {teacher_id}")
            return None
        
        # Check if relationship already exists
        existing = db.query(AssignmentClientDB).filter(
            AssignmentClientDB.assignment_id == assignment_id,
            AssignmentClientDB.client_id == client_id
        ).first()
        
        if existing:
            # Reactivate if soft-deleted
            if not existing.is_active:
                existing.is_active = True
                existing.rubric_id = rubric_id
                if display_order is not None:
                    existing.display_order = display_order
                db.commit()
                db.refresh(existing)
                logger.info(f"Reactivated client {client_id} for assignment {assignment_id}")
                return existing
            else:
                logger.warning(f"Client {client_id} already active for assignment {assignment_id}")
                return existing
        
        # Create new relationship
        assignment_client = AssignmentClientDB(
            assignment_id=assignment_id,
            client_id=client_id,
            rubric_id=rubric_id,
            display_order=display_order,
            is_active=True
        )
        db.add(assignment_client)
        db.commit()
        db.refresh(assignment_client)
        
        logger.info(f"Added client {client_id} to assignment {assignment_id}")
        return assignment_client
    
    def update_assignment_client(
        self,
        db: Session,
        assignment_id: str,
        client_id: str,
        rubric_id: str,
        teacher_id: str
    ) -> Optional[AssignmentClientDB]:
        """
        Update the rubric for an assignment-client relationship
        
        Args:
            db: Database session
            assignment_id: ID of the assignment
            client_id: ID of the client
            rubric_id: ID of the new rubric
            teacher_id: ID of the teacher
            
        Returns:
            Updated relationship or None if not found/unauthorized
            
        Business Rules:
            - Teacher must own the section
            - New rubric must belong to teacher
            - Only updates active relationships
        """
        # Check assignment ownership
        assignment = self.get(db, assignment_id, teacher_id)
        if not assignment:
            return None
        
        # Validate new rubric belongs to teacher
        rubric = rubric_service.get(db, rubric_id)
        if not rubric or rubric.created_by != teacher_id:
            logger.warning(f"Rubric {rubric_id} does not belong to teacher {teacher_id}")
            return None
        
        # Find the relationship
        assignment_client = db.query(AssignmentClientDB).filter(
            AssignmentClientDB.assignment_id == assignment_id,
            AssignmentClientDB.client_id == client_id,
            AssignmentClientDB.is_active == True
        ).first()
        
        if not assignment_client:
            logger.warning(f"No active relationship found for assignment {assignment_id} and client {client_id}")
            return None
        
        # Update the rubric
        assignment_client.rubric_id = rubric_id
        db.commit()
        db.refresh(assignment_client)
        
        logger.info(f"Updated rubric for client {client_id} in assignment {assignment_id}")
        return assignment_client
    
    def remove_client_from_assignment(
        self,
        db: Session,
        assignment_id: str,
        client_id: str,
        teacher_id: str
    ) -> bool:
        """
        Remove a client from an assignment (soft delete)
        
        Args:
            db: Database session
            assignment_id: ID of the assignment
            client_id: ID of the client to remove
            teacher_id: ID of the teacher
            
        Returns:
            True if removed, False if not found/unauthorized
            
        Business Rules:
            - Teacher must own the section
            - Soft deletes by setting is_active to False
        """
        # Check assignment ownership
        assignment = self.get(db, assignment_id, teacher_id)
        if not assignment:
            return False
        
        # Find the relationship
        assignment_client = db.query(AssignmentClientDB).filter(
            AssignmentClientDB.assignment_id == assignment_id,
            AssignmentClientDB.client_id == client_id,
            AssignmentClientDB.is_active == True
        ).first()
        
        if not assignment_client:
            logger.warning(f"No active relationship found for assignment {assignment_id} and client {client_id}")
            return False
        
        # Soft delete
        assignment_client.is_active = False
        db.commit()
        
        logger.info(f"Removed client {client_id} from assignment {assignment_id}")
        return True
    
    def bulk_add_clients(
        self,
        db: Session,
        assignment_id: str,
        clients_data: List[AssignmentClientCreate],
        teacher_id: str
    ) -> Dict[str, List[str]]:
        """
        Add multiple clients to an assignment in one operation
        
        Args:
            db: Database session
            assignment_id: ID of the assignment
            clients_data: List of client-rubric pairs to add
            teacher_id: ID of the teacher
            
        Returns:
            Dictionary with 'success' and 'failed' lists of client IDs
            
        Business Rules:
            - Teacher must own the section
            - All clients and rubrics must belong to teacher
            - Reactivates soft-deleted relationships
            - Continues on individual failures
        """
        # Check assignment ownership
        assignment = self.get(db, assignment_id, teacher_id)
        if not assignment:
            logger.warning(f"Teacher {teacher_id} cannot access assignment {assignment_id}")
            return {"success": [], "failed": [client.client_id for client in clients_data]}
        
        # Pre-validate all clients and rubrics belong to teacher
        client_ids = {client.client_id for client in clients_data}
        rubric_ids = {client.rubric_id for client in clients_data}
        
        # Fetch all clients
        valid_clients = db.query(ClientProfileDB).filter(
            ClientProfileDB.id.in_(client_ids),
            ClientProfileDB.created_by == teacher_id
        ).all()
        valid_client_ids = {client.id for client in valid_clients}
        
        # Fetch all rubrics
        valid_rubrics = db.query(EvaluationRubricDB).filter(
            EvaluationRubricDB.id.in_(rubric_ids),
            EvaluationRubricDB.created_by == teacher_id
        ).all()
        valid_rubric_ids = {rubric.id for rubric in valid_rubrics}
        
        # Process each client
        success = []
        failed = []
        
        for client_data in clients_data:
            # Validate client and rubric
            if (client_data.client_id not in valid_client_ids or 
                client_data.rubric_id not in valid_rubric_ids):
                failed.append(client_data.client_id)
                continue
            
            # Try to add the client
            try:
                result = self.add_client_to_assignment(
                    db=db,
                    assignment_id=assignment_id,
                    client_id=client_data.client_id,
                    rubric_id=client_data.rubric_id,
                    teacher_id=teacher_id,
                    display_order=client_data.display_order
                )
                
                if result:
                    success.append(client_data.client_id)
                else:
                    failed.append(client_data.client_id)
                    
            except Exception as e:
                logger.error(f"Error adding client {client_data.client_id}: {str(e)}")
                failed.append(client_data.client_id)
        
        logger.info(f"Bulk add to assignment {assignment_id}: {len(success)} success, {len(failed)} failed")
        return {"success": success, "failed": failed}
    
    def list_section_assignments(
        self,
        db: Session,
        section_id: str,
        teacher_id: Optional[str] = None,
        published_only: bool = True
    ) -> List[AssignmentDB]:
        """
        List assignments for a specific section
        
        Args:
            db: Database session
            section_id: ID of the course section
            teacher_id: If provided, checks teacher owns section
            published_only: Whether to only show published assignments
            
        Returns:
            List of assignments in the section
        """
        # If teacher_id provided, verify ownership
        if teacher_id and not section_service.can_update(db, section_id, teacher_id):
            logger.warning(f"Teacher {teacher_id} cannot access section {section_id} assignments")
            return []
        
        query = db.query(AssignmentDB).filter(
            AssignmentDB.section_id == section_id
        )
        
        if published_only:
            query = query.filter(AssignmentDB.is_published == True)
        
        assignments = query.order_by(
            AssignmentDB.created_at.desc()
        ).all()
        
        return assignments
    
    def publish_assignment(
        self,
        db: Session,
        assignment_id: str,
        teacher_id: str
    ) -> Optional[AssignmentDB]:
        """
        Publish an assignment (make visible to students)
        
        Args:
            db: Database session
            assignment_id: ID of the assignment
            teacher_id: ID of the teacher
            
        Returns:
            Updated assignment or None if unauthorized/invalid
            
        Business Rules:
            - Must have at least one active client-rubric pair
            - Validates dates if set
            - Sets is_published to True
        """
        assignment = self.get(db, assignment_id)
        if not assignment:
            return None
        
        # Check teacher owns the section
        if not section_service.can_update(db, assignment.section_id, teacher_id):
            logger.warning(f"Teacher {teacher_id} cannot publish assignment {assignment_id}")
            return None
        
        # Check if already published
        if assignment.is_published:
            logger.info(f"Assignment {assignment_id} is already published")
            return assignment
        
        # Validate has at least one active client
        active_clients = db.query(AssignmentClientDB).filter(
            AssignmentClientDB.assignment_id == assignment_id,
            AssignmentClientDB.is_active == True
        ).count()
        
        if active_clients == 0:
            logger.warning(f"Cannot publish assignment {assignment_id} without active clients")
            return None
        
        # Validate dates if set
        now = datetime.utcnow()
        if assignment.available_from and assignment.due_date:
            if assignment.available_from >= assignment.due_date:
                logger.warning(f"Cannot publish assignment {assignment_id}: invalid date range")
                return None
        
        # Publish the assignment
        assignment.is_published = True
        db.commit()
        db.refresh(assignment)
        logger.info(f"Published assignment {assignment_id}")
        return assignment
    
    def unpublish_assignment(
        self,
        db: Session,
        assignment_id: str,
        teacher_id: str
    ) -> Optional[AssignmentDB]:
        """
        Unpublish an assignment (hide from students)
        
        Args:
            db: Database session
            assignment_id: ID of the assignment
            teacher_id: ID of the teacher
            
        Returns:
            Updated assignment or None if unauthorized
        """
        assignment = self.get(db, assignment_id)
        if not assignment:
            return None
        
        # Check teacher owns the section
        if not section_service.can_update(db, assignment.section_id, teacher_id):
            logger.warning(f"Teacher {teacher_id} cannot unpublish assignment {assignment_id}")
            return None
        
        # Unpublish
        assignment.is_published = False
        db.commit()
        db.refresh(assignment)
        logger.info(f"Unpublished assignment {assignment_id}")
        return assignment
    
    def get_assignment_stats(
        self,
        db: Session,
        assignment_id: str
    ) -> Dict:
        """
        Get statistics for a single assignment
        
        Args:
            db: Database session
            assignment_id: ID of the assignment
            
        Returns:
            Dictionary with assignment statistics including:
            - assignment_id: str
            - active_clients: int
            - inactive_clients: int
            - total_clients: int
        """
        stats = db.query(
            func.count(case((AssignmentClientDB.is_active == True, 1))).label('active_clients'),
            func.count(case((AssignmentClientDB.is_active == False, 1))).label('inactive_clients'),
            func.count(AssignmentClientDB.id).label('total_clients')
        ).filter(
            AssignmentClientDB.assignment_id == assignment_id
        ).first()
        
        return {
            "assignment_id": assignment_id,
            "active_clients": stats.active_clients or 0,
            "inactive_clients": stats.inactive_clients or 0,
            "total_clients": stats.total_clients or 0
        }
    
    def list_available_assignments(
        self,
        db: Session,
        section_ids: List[str],
        as_of: Optional[datetime] = None
    ) -> List[AssignmentDB]:
        """
        List assignments available to students based on dates
        
        Args:
            db: Database session
            section_ids: List of section IDs to check
            as_of: Reference datetime (defaults to now)
            
        Returns:
            List of available published assignments
            
        Business Rules:
            - Must be published
            - Must be past available_from date (if set)
            - Must be before due_date (if set)
        """
        if not section_ids:
            return []
        
        if not as_of:
            as_of = datetime.utcnow()
        
        query = db.query(AssignmentDB).filter(
            AssignmentDB.section_id.in_(section_ids),
            AssignmentDB.is_published == True
        )
        
        # Add date filters
        # Filter by available_from (null or past date)
        query = query.filter(
            (AssignmentDB.available_from == None) | (AssignmentDB.available_from <= as_of)
        )
        # Filter by due_date (null or future date)
        query = query.filter(
            (AssignmentDB.due_date == None) | (AssignmentDB.due_date > as_of)
        )
        
        assignments = query.order_by(
            AssignmentDB.available_from.asc(),
            AssignmentDB.created_at.desc()
        ).all()
        
        return assignments


# Create global instance
assignment_service = AssignmentService()
