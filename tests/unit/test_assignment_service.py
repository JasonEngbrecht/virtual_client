"""
Unit tests for Assignment Service
Tests business logic for assignment operations
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from backend.services.assignment_service import assignment_service
from backend.services.section_service import section_service
from backend.models.assignment import (
    AssignmentDB, AssignmentClientDB, AssignmentCreate, AssignmentUpdate,
    AssignmentType
)
from backend.models.course_section import CourseSectionDB, CourseSectionCreate
from backend.models.client_profile import ClientProfileDB
from backend.models.rubric import EvaluationRubricDB


@pytest.fixture
def test_section(db_session):
    """Create a test course section"""
    section = CourseSectionDB(
        id=str(uuid4()),
        teacher_id="teacher-123",
        name="Test Section",
        is_active=True
    )
    db_session.add(section)
    db_session.commit()
    return section


@pytest.fixture
def test_assignment(db_session, test_section):
    """Create a test assignment"""
    assignment = AssignmentDB(
        id=str(uuid4()),
        section_id=test_section.id,
        title="Test Assignment",
        description="Test description",
        type=AssignmentType.PRACTICE,
        is_published=False
    )
    db_session.add(assignment)
    db_session.commit()
    return assignment


@pytest.fixture
def test_client_and_rubric(db_session):
    """Create test client and rubric for assignment-client relationships"""
    client = ClientProfileDB(
        id=str(uuid4()),
        name="Test Client",
        age=30,
        created_by="teacher-123"
    )
    db_session.add(client)
    
    rubric = EvaluationRubricDB(
        id=str(uuid4()),
        name="Test Rubric",
        criteria=[{
            "name": "Communication",
            "description": "Client communication skills",
            "weight": 1.0,
            "evaluation_points": ["Active listening"],
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
    
    return client, rubric


class TestAssignmentServiceCreate:
    """Test assignment creation functionality"""
    
    def test_create_assignment_for_teacher_success(self, db_session, test_section):
        """Test successful assignment creation"""
        assignment_data = AssignmentCreate(
            title="New Assignment",
            description="Test description",
            type=AssignmentType.GRADED,
            max_attempts=3
        )
        
        assignment = assignment_service.create_assignment_for_teacher(
            db_session,
            assignment_data,
            test_section.id,
            "teacher-123"
        )
        
        assert assignment is not None
        assert assignment.title == "New Assignment"
        assert assignment.section_id == test_section.id
        assert assignment.type == AssignmentType.GRADED
        assert assignment.max_attempts == 3
        assert assignment.is_published is False  # Default
    
    def test_create_assignment_unauthorized_teacher(self, db_session, test_section):
        """Test assignment creation by unauthorized teacher"""
        assignment_data = AssignmentCreate(
            title="Unauthorized Assignment"
        )
        
        assignment = assignment_service.create_assignment_for_teacher(
            db_session,
            assignment_data,
            test_section.id,
            "other-teacher"  # Wrong teacher
        )
        
        assert assignment is None
    
    def test_create_assignment_with_dates(self, db_session, test_section):
        """Test assignment creation with date validation"""
        now = datetime.utcnow()
        assignment_data = AssignmentCreate(
            title="Dated Assignment",
            available_from=now,
            due_date=now + timedelta(days=7)
        )
        
        assignment = assignment_service.create_assignment_for_teacher(
            db_session,
            assignment_data,
            test_section.id,
            "teacher-123"
        )
        
        assert assignment is not None
        assert assignment.available_from == now
        assert assignment.due_date == now + timedelta(days=7)
    
    def test_create_assignment_with_settings(self, db_session, test_section):
        """Test assignment creation with custom settings"""
        assignment_data = AssignmentCreate(
            title="Settings Assignment",
            settings={
                "time_limit": 60,
                "allow_notes": True,
                "show_rubric": False
            }
        )
        
        assignment = assignment_service.create_assignment_for_teacher(
            db_session,
            assignment_data,
            test_section.id,
            "teacher-123"
        )
        
        assert assignment is not None
        assert assignment.settings["time_limit"] == 60
        assert assignment.settings["allow_notes"] is True
        assert assignment.settings["show_rubric"] is False


class TestAssignmentServiceRead:
    """Test assignment retrieval functionality"""
    
    def test_get_assignment_by_id(self, db_session, test_assignment):
        """Test getting assignment by ID"""
        assignment = assignment_service.get(db_session, test_assignment.id)
        
        assert assignment is not None
        assert assignment.id == test_assignment.id
        assert assignment.title == test_assignment.title
    
    def test_get_assignment_with_teacher_check(self, db_session, test_assignment):
        """Test getting assignment with teacher permission check"""
        # Authorized teacher
        assignment = assignment_service.get(
            db_session,
            test_assignment.id,
            "teacher-123"
        )
        assert assignment is not None
        
        # Unauthorized teacher
        assignment = assignment_service.get(
            db_session,
            test_assignment.id,
            "other-teacher"
        )
        assert assignment is None
    
    def test_get_nonexistent_assignment(self, db_session):
        """Test getting non-existent assignment"""
        assignment = assignment_service.get(db_session, "fake-id")
        assert assignment is None


class TestAssignmentServiceUpdate:
    """Test assignment update functionality"""
    
    def test_update_draft_assignment(self, db_session, test_assignment):
        """Test updating a draft assignment"""
        update_data = AssignmentUpdate(
            title="Updated Title",
            description="Updated description",
            type=AssignmentType.GRADED,
            max_attempts=5
        )
        
        updated = assignment_service.update(
            db_session,
            test_assignment.id,
            update_data,
            "teacher-123"
        )
        
        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.description == "Updated description"
        assert updated.type == AssignmentType.GRADED
        assert updated.max_attempts == 5
    
    def test_update_published_assignment_restrictions(self, db_session, test_section):
        """Test update restrictions on published assignments"""
        # Create published assignment
        assignment = AssignmentDB(
            section_id=test_section.id,
            title="Published Assignment",
            type=AssignmentType.PRACTICE,
            is_published=True
        )
        db_session.add(assignment)
        db_session.commit()
        
        # Try to update restricted fields
        update_data = AssignmentUpdate(
            title="New Title",  # Restricted
            type=AssignmentType.GRADED,  # Restricted
            description="New description",  # Allowed
            due_date=datetime.utcnow() + timedelta(days=7)  # Allowed
        )
        
        updated = assignment_service.update(
            db_session,
            assignment.id,
            update_data,
            "teacher-123"
        )
        
        assert updated is not None
        assert updated.title == "Published Assignment"  # Not changed
        assert updated.type == AssignmentType.PRACTICE  # Not changed
        assert updated.description == "New description"  # Changed
        assert updated.due_date is not None  # Changed
    
    def test_update_assignment_unauthorized(self, db_session, test_assignment):
        """Test updating assignment by unauthorized teacher"""
        update_data = AssignmentUpdate(title="Hacked Title")
        
        updated = assignment_service.update(
            db_session,
            test_assignment.id,
            update_data,
            "other-teacher"
        )
        
        assert updated is None
    
    def test_update_nonexistent_assignment(self, db_session):
        """Test updating non-existent assignment"""
        update_data = AssignmentUpdate(title="Ghost Title")
        
        updated = assignment_service.update(
            db_session,
            "fake-id",
            update_data,
            "teacher-123"
        )
        
        assert updated is None


class TestAssignmentServiceDelete:
    """Test assignment deletion functionality"""
    
    def test_delete_draft_assignment(self, db_session, test_assignment):
        """Test deleting a draft assignment"""
        result = assignment_service.delete(
            db_session,
            test_assignment.id,
            "teacher-123"
        )
        
        assert result is True
        
        # Verify deletion
        deleted = assignment_service.get(db_session, test_assignment.id)
        assert deleted is None
    
    def test_delete_published_assignment_fails(self, db_session, test_section):
        """Test that published assignments cannot be deleted"""
        # Create published assignment
        assignment = AssignmentDB(
            section_id=test_section.id,
            title="Published Assignment",
            is_published=True
        )
        db_session.add(assignment)
        db_session.commit()
        
        result = assignment_service.delete(
            db_session,
            assignment.id,
            "teacher-123"
        )
        
        assert result is False
        
        # Verify not deleted
        still_exists = assignment_service.get(db_session, assignment.id)
        assert still_exists is not None
    
    def test_delete_assignment_unauthorized(self, db_session, test_assignment):
        """Test deleting assignment by unauthorized teacher"""
        result = assignment_service.delete(
            db_session,
            test_assignment.id,
            "other-teacher"
        )
        
        assert result is False
    
    def test_delete_assignment_cascades_clients(self, db_session, test_assignment, test_client_and_rubric):
        """Test that deleting assignment cascades to assignment-client relationships"""
        client, rubric = test_client_and_rubric
        
        # Add assignment-client relationship
        assignment_client = AssignmentClientDB(
            assignment_id=test_assignment.id,
            client_id=client.id,
            rubric_id=rubric.id
        )
        db_session.add(assignment_client)
        db_session.commit()
        
        # Delete assignment
        result = assignment_service.delete(
            db_session,
            test_assignment.id,
            "teacher-123"
        )
        
        assert result is True
        
        # Verify cascade
        orphaned = db_session.query(AssignmentClientDB).filter_by(
            assignment_id=test_assignment.id
        ).first()
        assert orphaned is None


class TestAssignmentServiceList:
    """Test assignment listing functionality"""
    
    def test_list_teacher_assignments(self, db_session, test_section):
        """Test listing assignments for a teacher"""
        # Create multiple assignments
        for i in range(3):
            assignment = AssignmentDB(
                section_id=test_section.id,
                title=f"Assignment {i}",
                is_published=(i % 2 == 0)  # Mix of published and draft
            )
            db_session.add(assignment)
        db_session.commit()
        
        # Get all assignments
        assignments = assignment_service.list_teacher_assignments(
            db_session,
            "teacher-123"
        )
        
        assert len(assignments) == 3  # 3 created in this test
    
    def test_list_teacher_assignments_filter_section(self, db_session, test_section):
        """Test filtering assignments by section"""
        # Create another section
        other_section = CourseSectionDB(
            teacher_id="teacher-123",
            name="Other Section"
        )
        db_session.add(other_section)
        db_session.commit()
        
        # Add assignment to other section
        other_assignment = AssignmentDB(
            section_id=other_section.id,
            title="Other Assignment"
        )
        db_session.add(other_assignment)
        db_session.commit()
        
        # Filter by specific section
        assignments = assignment_service.list_teacher_assignments(
            db_session,
            "teacher-123",
            section_id=test_section.id
        )
        
        assert all(a.section_id == test_section.id for a in assignments)
    
    def test_list_teacher_assignments_filter_published(self, db_session, test_section):
        """Test filtering assignments by published state"""
        # Create published assignment
        published = AssignmentDB(
            section_id=test_section.id,
            title="Published Assignment",
            is_published=True
        )
        db_session.add(published)
        db_session.commit()
        
        # Get only published
        assignments = assignment_service.list_teacher_assignments(
            db_session,
            "teacher-123",
            include_draft=False
        )
        
        assert all(a.is_published for a in assignments)
        assert len(assignments) == 1
    
    def test_list_section_assignments(self, db_session, test_section):
        """Test listing assignments for a specific section"""
        # Create assignments
        for i in range(2):
            assignment = AssignmentDB(
                section_id=test_section.id,
                title=f"Section Assignment {i}",
                is_published=True
            )
            db_session.add(assignment)
        db_session.commit()
        
        # Get section assignments
        assignments = assignment_service.list_section_assignments(
            db_session,
            test_section.id,
            published_only=False
        )
        
        assert len(assignments) == 2  # 2 created in this test
        assert all(a.section_id == test_section.id for a in assignments)
    
    def test_list_section_assignments_unauthorized(self, db_session, test_section):
        """Test listing section assignments with unauthorized teacher"""
        assignments = assignment_service.list_section_assignments(
            db_session,
            test_section.id,
            teacher_id="other-teacher"
        )
        
        assert assignments == []


class TestAssignmentServicePublishing:
    """Test assignment publishing functionality"""
    
    def test_publish_assignment_success(self, db_session, test_assignment, test_client_and_rubric):
        """Test successfully publishing an assignment"""
        client, rubric = test_client_and_rubric
        
        # Add active client
        assignment_client = AssignmentClientDB(
            assignment_id=test_assignment.id,
            client_id=client.id,
            rubric_id=rubric.id,
            is_active=True
        )
        db_session.add(assignment_client)
        db_session.commit()
        
        # Publish
        published = assignment_service.publish_assignment(
            db_session,
            test_assignment.id,
            "teacher-123"
        )
        
        assert published is not None
        assert published.is_published is True
    
    def test_publish_assignment_without_clients(self, db_session, test_assignment):
        """Test publishing fails without active clients"""
        published = assignment_service.publish_assignment(
            db_session,
            test_assignment.id,
            "teacher-123"
        )
        
        assert published is None
    
    def test_publish_assignment_already_published(self, db_session, test_assignment, test_client_and_rubric):
        """Test publishing already published assignment"""
        client, rubric = test_client_and_rubric
        
        # Setup and publish
        assignment_client = AssignmentClientDB(
            assignment_id=test_assignment.id,
            client_id=client.id,
            rubric_id=rubric.id
        )
        db_session.add(assignment_client)
        test_assignment.is_published = True
        db_session.commit()
        
        # Try to publish again
        published = assignment_service.publish_assignment(
            db_session,
            test_assignment.id,
            "teacher-123"
        )
        
        assert published is not None
        assert published.is_published is True
    
    def test_publish_assignment_invalid_dates(self, db_session, test_assignment, test_client_and_rubric):
        """Test publishing fails with invalid date range"""
        client, rubric = test_client_and_rubric
        
        # Add client
        assignment_client = AssignmentClientDB(
            assignment_id=test_assignment.id,
            client_id=client.id,
            rubric_id=rubric.id
        )
        db_session.add(assignment_client)
        
        # Set invalid dates
        now = datetime.utcnow()
        test_assignment.available_from = now + timedelta(days=7)
        test_assignment.due_date = now
        db_session.commit()
        
        # Try to publish
        published = assignment_service.publish_assignment(
            db_session,
            test_assignment.id,
            "teacher-123"
        )
        
        assert published is None
    
    def test_unpublish_assignment(self, db_session, test_assignment):
        """Test unpublishing an assignment"""
        test_assignment.is_published = True
        db_session.commit()
        
        unpublished = assignment_service.unpublish_assignment(
            db_session,
            test_assignment.id,
            "teacher-123"
        )
        
        assert unpublished is not None
        assert unpublished.is_published is False


class TestAssignmentServiceStats:
    """Test assignment statistics functionality"""
    
    def test_get_assignment_stats(self, db_session, test_assignment, test_client_and_rubric):
        """Test getting assignment statistics"""
        client, rubric = test_client_and_rubric
        
        # Add mix of active and inactive clients
        for i in range(3):
            assignment_client = AssignmentClientDB(
                assignment_id=test_assignment.id,
                client_id=client.id,
                rubric_id=rubric.id,
                is_active=(i < 2)  # 2 active, 1 inactive
            )
            db_session.add(assignment_client)
        db_session.commit()
        
        stats = assignment_service.get_assignment_stats(
            db_session,
            test_assignment.id
        )
        
        assert stats["assignment_id"] == test_assignment.id
        assert stats["active_clients"] == 2
        assert stats["inactive_clients"] == 1
        assert stats["total_clients"] == 3
    
    def test_get_assignment_stats_empty(self, db_session, test_assignment):
        """Test getting stats for assignment with no clients"""
        stats = assignment_service.get_assignment_stats(
            db_session,
            test_assignment.id
        )
        
        assert stats["active_clients"] == 0
        assert stats["inactive_clients"] == 0
        assert stats["total_clients"] == 0


class TestAssignmentServiceAvailability:
    """Test assignment availability functionality"""
    
    def test_list_available_assignments_by_date(self, db_session, test_section):
        """Test listing assignments based on availability dates"""
        now = datetime.utcnow()
        
        # Create assignments with different date scenarios
        assignments_data = [
            # Available now
            {
                "title": "Current Assignment",
                "available_from": now - timedelta(days=1),
                "due_date": now + timedelta(days=7),
                "is_published": True
            },
            # Not yet available
            {
                "title": "Future Assignment",
                "available_from": now + timedelta(days=1),
                "due_date": now + timedelta(days=7),
                "is_published": True
            },
            # Past due
            {
                "title": "Past Assignment",
                "available_from": now - timedelta(days=7),
                "due_date": now - timedelta(days=1),
                "is_published": True
            },
            # No dates (always available)
            {
                "title": "Undated Assignment",
                "is_published": True
            },
            # Draft (not available)
            {
                "title": "Draft Assignment",
                "is_published": False
            }
        ]
        
        for data in assignments_data:
            assignment = AssignmentDB(section_id=test_section.id, **data)
            db_session.add(assignment)
        db_session.commit()
        
        # Get available assignments
        available = assignment_service.list_available_assignments(
            db_session,
            [test_section.id],
            as_of=now
        )
        
        # Should get "Current" and "Undated" only
        assert len(available) == 2
        titles = [a.title for a in available]
        assert "Current Assignment" in titles
        assert "Undated Assignment" in titles
    
    def test_list_available_assignments_empty_sections(self, db_session):
        """Test listing available assignments with no sections"""
        available = assignment_service.list_available_assignments(
            db_session,
            []  # Empty section list
        )
        
        assert available == []
    
    def test_list_available_assignments_multiple_sections(self, db_session):
        """Test listing available assignments across multiple sections"""
        # Create two sections
        sections = []
        for i in range(2):
            section = CourseSectionDB(
                teacher_id="teacher-123",
                name=f"Section {i}"
            )
            db_session.add(section)
            db_session.commit()
            sections.append(section)
            
            # Add published assignment
            assignment = AssignmentDB(
                section_id=section.id,
                title=f"Assignment for Section {i}",
                is_published=True
            )
            db_session.add(assignment)
        db_session.commit()
        
        # Get assignments from both sections
        section_ids = [s.id for s in sections]
        available = assignment_service.list_available_assignments(
            db_session,
            section_ids
        )
        
        assert len(available) == 2
        assert all(a.section_id in section_ids for a in available)
