"""
Unit tests for Assignment models
Tests model instantiation, database operations, and schema validation
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from backend.models.assignment import (
    AssignmentDB, AssignmentClientDB, AssignmentType,
    AssignmentCreate, AssignmentUpdate, Assignment,
    AssignmentClientCreate, AssignmentClient
)
from backend.models.course_section import CourseSectionDB
from backend.models.client_profile import ClientProfileDB
from backend.models.rubric import EvaluationRubricDB


class TestAssignmentModels:
    """Test assignment database models"""
    
    def test_assignment_db_instantiation(self):
        """Test creating an AssignmentDB instance"""
        assignment = AssignmentDB(
            id=str(uuid4()),
            section_id=str(uuid4()),
            title="Client Interview Practice",
            description="Practice initial assessment interviews",
            type=AssignmentType.PRACTICE,
            settings={"time_limit": 30, "allow_notes": True},
            available_from=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=7),
            is_published=False,
            max_attempts=3
        )
        
        assert assignment.title == "Client Interview Practice"
        assert assignment.type == AssignmentType.PRACTICE
        assert assignment.settings["time_limit"] == 30
        assert assignment.is_published is False
        assert assignment.max_attempts == 3
    
    def test_assignment_client_db_instantiation(self):
        """Test creating an AssignmentClientDB instance"""
        assignment_client = AssignmentClientDB(
            id=str(uuid4()),
            assignment_id=str(uuid4()),
            client_id=str(uuid4()),
            rubric_id=str(uuid4()),
            is_active=True,
            display_order=1
        )
        
        assert assignment_client.is_active is True
        assert assignment_client.display_order == 1
    
    def test_assignment_db_in_database(self, db_session):
        """Test saving and retrieving an assignment from database"""
        # First create a section
        section = CourseSectionDB(
            id=str(uuid4()),
            teacher_id="teacher-123",
            name="Test Section",
            is_active=True
        )
        db_session.add(section)
        db_session.commit()
        
        # Create assignment
        assignment_id = str(uuid4())
        assignment = AssignmentDB(
            id=assignment_id,
            section_id=section.id,
            title="Database Test Assignment",
            description="Test description",
            type=AssignmentType.GRADED,
            settings={"show_rubric": True},
            is_published=True,
            max_attempts=2
        )
        
        db_session.add(assignment)
        db_session.commit()
        
        # Retrieve from database
        retrieved = db_session.query(AssignmentDB).filter_by(id=assignment_id).first()
        assert retrieved is not None
        assert retrieved.title == "Database Test Assignment"
        assert retrieved.type == AssignmentType.GRADED
        assert retrieved.settings["show_rubric"] is True
        assert retrieved.max_attempts == 2
    
    def test_assignment_client_db_in_database(self, db_session):
        """Test saving and retrieving an assignment-client relationship"""
        # Create prerequisites
        section = CourseSectionDB(
            teacher_id="teacher-123",
            name="Test Section",
            is_active=True
        )
        db_session.add(section)
        db_session.commit()  # Commit section first to get ID
        
        assignment = AssignmentDB(
            section_id=section.id,
            title="Test Assignment",
            type=AssignmentType.PRACTICE
        )
        db_session.add(assignment)
        
        client = ClientProfileDB(
            name="Test Client",
            age=30,
            created_by="teacher-123"
        )
        db_session.add(client)
        
        rubric = EvaluationRubricDB(
            name="Test Rubric",
            criteria=[{
                "name": "Test Criterion",
                "description": "Test description",
                "weight": 1.0,
                "evaluation_points": ["Test point"],
                "scoring_levels": {
                    "excellent": 4,
                    "good": 3,
                    "satisfactory": 2,
                    "needs_improvement": 1
                }
            }],
            created_by="teacher-123"
        )
        db_session.add(rubric)
        db_session.commit()
        
        # Create assignment-client relationship
        ac_id = str(uuid4())
        assignment_client = AssignmentClientDB(
            id=ac_id,
            assignment_id=assignment.id,
            client_id=client.id,
            rubric_id=rubric.id,
            is_active=True,
            display_order=1
        )
        
        db_session.add(assignment_client)
        db_session.commit()
        
        # Retrieve and verify
        retrieved = db_session.query(AssignmentClientDB).filter_by(id=ac_id).first()
        assert retrieved is not None
        assert retrieved.assignment_id == assignment.id
        assert retrieved.client_id == client.id
        assert retrieved.rubric_id == rubric.id
        assert retrieved.display_order == 1
    
    def test_assignment_relationships(self, db_session):
        """Test the relationship between assignments and assignment-clients"""
        # Create assignment
        section = CourseSectionDB(
            teacher_id="teacher-123",
            name="Test Section",
            is_active=True
        )
        db_session.add(section)
        db_session.commit()  # Commit section first to get ID
        
        assignment = AssignmentDB(
            section_id=section.id,
            title="Test Assignment with Clients",
            type=AssignmentType.PRACTICE
        )
        db_session.add(assignment)
        db_session.commit()
        
        # Add multiple clients
        for i in range(3):
            client = ClientProfileDB(
                name=f"Client {i}",
                age=25 + i,
                created_by="teacher-123"
            )
            db_session.add(client)
            
            rubric = EvaluationRubricDB(
                name=f"Rubric {i}",
                criteria=[{
                    "name": f"Criterion {i}",
                    "description": f"Test description {i}",
                    "weight": 1.0,
                    "evaluation_points": [f"Test point {i}"],
                    "scoring_levels": {
                        "excellent": 4,
                        "good": 3,
                        "satisfactory": 2,
                        "needs_improvement": 1
                    }
                }],
                created_by="teacher-123"
            )
            db_session.add(rubric)
            db_session.commit()
            
            assignment_client = AssignmentClientDB(
                assignment_id=assignment.id,
                client_id=client.id,
                rubric_id=rubric.id,
                display_order=i
            )
            db_session.add(assignment_client)
        
        db_session.commit()
        db_session.refresh(assignment)
        
        # Check relationship
        assert len(assignment.assignment_clients) == 3
        assert all(ac.assignment_id == assignment.id for ac in assignment.assignment_clients)
        assert assignment.assignment_clients[0].assignment == assignment


class TestAssignmentSchemas:
    """Test Pydantic schemas for assignments"""
    
    def test_assignment_create_schema(self):
        """Test AssignmentCreate schema validation"""
        data = {
            "title": "Interview Practice Assignment",
            "description": "Practice conducting initial assessments",
            "type": "practice",
            "settings": {"time_limit": 45},
            "available_from": datetime.utcnow(),
            "due_date": datetime.utcnow() + timedelta(days=14),
            "is_published": False,
            "max_attempts": 3
        }
        
        schema = AssignmentCreate(**data)
        assert schema.title == "Interview Practice Assignment"
        assert schema.type == AssignmentType.PRACTICE
        assert schema.settings["time_limit"] == 45
        assert schema.max_attempts == 3
    
    def test_assignment_create_minimal(self):
        """Test AssignmentCreate with minimal data"""
        data = {"title": "Basic Assignment"}
        schema = AssignmentCreate(**data)
        
        assert schema.title == "Basic Assignment"
        assert schema.description is None
        assert schema.type == AssignmentType.PRACTICE  # default
        assert schema.is_published is False  # default
        assert schema.settings == {}  # default empty dict
        assert schema.max_attempts is None  # unlimited by default
    
    def test_assignment_update_schema(self):
        """Test AssignmentUpdate schema for partial updates"""
        data = {
            "description": "Updated description",
            "is_published": True,
            "max_attempts": 5
        }
        
        schema = AssignmentUpdate(**data)
        assert schema.description == "Updated description"
        assert schema.is_published is True
        assert schema.max_attempts == 5
        assert schema.title is None  # not provided
        assert schema.type is None  # not provided
    
    def test_assignment_response_schema(self):
        """Test Assignment response schema"""
        data = {
            "id": str(uuid4()),
            "section_id": str(uuid4()),
            "title": "Test Assignment",
            "description": "Test description",
            "type": AssignmentType.GRADED,
            "settings": {"allow_notes": False},
            "available_from": datetime.utcnow(),
            "due_date": datetime.utcnow() + timedelta(days=7),
            "is_published": True,
            "max_attempts": 2,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "client_count": 3,
            "section_name": "SW 101 - Spring 2025"
        }
        
        schema = Assignment(**data)
        assert schema.title == "Test Assignment"
        assert schema.type == AssignmentType.GRADED
        assert schema.client_count == 3
        assert schema.section_name == "SW 101 - Spring 2025"
    
    def test_assignment_client_create_schema(self):
        """Test AssignmentClientCreate schema"""
        data = {
            "client_id": str(uuid4()),
            "rubric_id": str(uuid4()),
            "display_order": 2
        }
        
        schema = AssignmentClientCreate(**data)
        assert schema.display_order == 2
    
    def test_assignment_client_create_default_order(self):
        """Test AssignmentClientCreate with default display order"""
        data = {
            "client_id": str(uuid4()),
            "rubric_id": str(uuid4())
        }
        schema = AssignmentClientCreate(**data)
        
        assert schema.display_order == 0  # default value
    
    def test_assignment_client_response_schema(self):
        """Test AssignmentClient response schema"""
        data = {
            "id": str(uuid4()),
            "assignment_id": str(uuid4()),
            "client_id": str(uuid4()),
            "rubric_id": str(uuid4()),
            "is_active": True,
            "display_order": 1,
            "client": {
                "id": str(uuid4()),
                "name": "Maria Rodriguez",
                "age": 35,
                "gender": "Female"
            },
            "rubric": {
                "id": str(uuid4()),
                "name": "Initial Assessment Rubric",
                "description": "Rubric for evaluating initial client assessments"
            }
        }
        
        schema = AssignmentClient(**data)
        assert schema.is_active is True
        assert schema.client_name == "Maria Rodriguez"  # Computed from client.name
        assert schema.rubric_name == "Initial Assessment Rubric"  # Computed from rubric.name


class TestSchemaValidation:
    """Test schema validation rules"""
    
    def test_assignment_title_validation(self):
        """Test title field validation"""
        # Empty title should fail
        with pytest.raises(ValueError):
            AssignmentCreate(title="")
        
        # Very long title should fail (>200 chars)
        with pytest.raises(ValueError):
            AssignmentCreate(title="x" * 201)
        
        # Valid title should pass
        schema = AssignmentCreate(title="Valid Assignment Title")
        assert schema.title == "Valid Assignment Title"
    
    def test_assignment_type_validation(self):
        """Test assignment type enum validation"""
        # Valid types
        for type_value in ["practice", "graded"]:
            schema = AssignmentCreate(title="Test", type=type_value)
            assert schema.type.value == type_value
        
        # Invalid type should fail
        with pytest.raises(ValueError):
            AssignmentCreate(title="Test", type="invalid_type")
    
    def test_max_attempts_validation(self):
        """Test max_attempts validation"""
        # Zero or negative attempts should fail
        with pytest.raises(ValueError):
            AssignmentCreate(title="Test", max_attempts=0)
        
        with pytest.raises(ValueError):
            AssignmentCreate(title="Test", max_attempts=-1)
        
        # Positive attempts should pass
        schema = AssignmentCreate(title="Test", max_attempts=5)
        assert schema.max_attempts == 5
        
        # None (unlimited) should pass
        schema = AssignmentCreate(title="Test", max_attempts=None)
        assert schema.max_attempts is None
    
    def test_date_validation(self):
        """Test date validation rules"""
        now = datetime.utcnow()
        
        # Valid dates (due_date after available_from)
        schema = AssignmentCreate(
            title="Test",
            available_from=now,
            due_date=now + timedelta(days=7)
        )
        assert schema.due_date > schema.available_from
        
        # Invalid dates (due_date before available_from)
        with pytest.raises(ValueError, match="Due date must be after available_from"):
            AssignmentCreate(
                title="Test",
                available_from=now + timedelta(days=7),
                due_date=now
            )
        
        # Same date should also fail
        with pytest.raises(ValueError, match="Due date must be after available_from"):
            AssignmentCreate(
                title="Test",
                available_from=now,
                due_date=now
            )
        
        # Only due_date provided should pass
        schema = AssignmentCreate(title="Test", due_date=now)
        assert schema.due_date == now
        
        # Only available_from provided should pass
        schema = AssignmentCreate(title="Test", available_from=now)
        assert schema.available_from == now
    
    def test_display_order_validation(self):
        """Test display_order validation in AssignmentClientCreate"""
        # Negative display order should fail
        with pytest.raises(ValueError):
            AssignmentClientCreate(
                client_id=str(uuid4()),
                rubric_id=str(uuid4()),
                display_order=-1
            )
        
        # Zero and positive values should pass
        schema = AssignmentClientCreate(
            client_id=str(uuid4()),
            rubric_id=str(uuid4()),
            display_order=0
        )
        assert schema.display_order == 0
        
        schema = AssignmentClientCreate(
            client_id=str(uuid4()),
            rubric_id=str(uuid4()),
            display_order=10
        )
        assert schema.display_order == 10
    
    def test_update_date_validation(self):
        """Test date validation in AssignmentUpdate"""
        now = datetime.utcnow()
        
        # Valid update with both dates
        schema = AssignmentUpdate(
            available_from=now,
            due_date=now + timedelta(days=7)
        )
        assert schema.due_date > schema.available_from
        
        # Invalid update (due_date before available_from)
        with pytest.raises(ValueError, match="Due date must be after available_from"):
            AssignmentUpdate(
                available_from=now + timedelta(days=7),
                due_date=now
            )
        
        # Update with only one date should pass
        schema = AssignmentUpdate(due_date=now + timedelta(days=14))
        assert schema.due_date is not None
        assert schema.available_from is None
