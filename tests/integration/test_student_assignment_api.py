"""
Integration tests for student assignment viewing API endpoints.
Tests enrollment-based access, date filtering, and security boundaries.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from unittest.mock import patch

from backend.models.assignment import (
    AssignmentDB, AssignmentClientDB, AssignmentType, AssignmentCreate
)
from backend.models.course_section import CourseSectionDB, SectionEnrollmentDB
from backend.models.client_profile import ClientProfileDB
from backend.models.rubric import EvaluationRubricDB
from backend.services.assignment_service import assignment_service
from backend.services.section_service import section_service
from backend.services.enrollment_service import enrollment_service
from backend.services.client_service import client_service
from backend.services.rubric_service import rubric_service


class TestStudentAssignmentViewing:
    """Test student assignment viewing endpoints."""
    
    @pytest.fixture
    def teacher_id(self):
        """Mock teacher ID for tests."""
        return "teacher-123"
    
    @pytest.fixture
    def student_id(self):
        """Mock student ID for tests."""
        return "student-123"
    
    @pytest.fixture
    def another_student_id(self):
        """Another student ID for negative tests."""
        return "student-456"
    
    @pytest.fixture
    def mock_student_auth(self, client, student_id):
        """Mock student authentication for tests."""
        from backend.app import app
        from backend.api.student_routes import get_current_student
        
        def override_get_current_student():
            return student_id
        
        app.dependency_overrides[get_current_student] = override_get_current_student
        yield
        # Cleanup is handled by client fixture clearing all overrides
    
    @pytest.fixture
    def mock_another_student_auth(self, client, another_student_id):
        """Mock another student authentication for tests."""
        from backend.app import app
        from backend.api.student_routes import get_current_student
        
        def override_get_current_student():
            return another_student_id
        
        app.dependency_overrides[get_current_student] = override_get_current_student
        yield
        # Cleanup is handled by client fixture clearing all overrides
    
    @pytest.fixture
    def section(self, db_session: Session, teacher_id: str) -> CourseSectionDB:
        """Create a test section."""
        from backend.models.course_section import CourseSectionCreate
        section_data = CourseSectionCreate(
            name="Test Section",
            course_code="TEST101",
            term="Spring 2025"
        )
        section = section_service.create_section_for_teacher(
            db_session,
            section_data,
            teacher_id
        )
        return section
    
    @pytest.fixture
    def another_section(self, db_session: Session, teacher_id: str) -> CourseSectionDB:
        """Create another test section."""
        section = section_service.create(
            db_session,
            name="Another Section",
            course_code="TEST102",
            teacher_id=teacher_id,
            term="Spring 2025"
        )
        return section
    
    @pytest.fixture
    def test_client(self, db_session: Session, teacher_id: str) -> ClientProfileDB:
        """Create a test client profile."""
        return client_service.create(
            db_session,
            name="Test Client",
            age=30,
            gender="Female",
            created_by=teacher_id
        )
    
    @pytest.fixture
    def rubric(self, db_session: Session, teacher_id: str) -> EvaluationRubricDB:
        """Create a test rubric."""
        return rubric_service.create(
            db_session,
            name="Test Rubric",
            description="Test rubric description",
            criteria={"test": "criteria"},
            created_by=teacher_id
        )
    
    @pytest.fixture
    def enrollment(self, db_session: Session, section: CourseSectionDB, student_id: str) -> SectionEnrollmentDB:
        """Enroll student in test section."""
        return enrollment_service.enroll_student(db_session, section.id, student_id)
    
    @pytest.fixture
    def published_assignment(
        self, 
        db_session: Session, 
        section: CourseSectionDB, 
        teacher_id: str,
        test_client: ClientProfileDB,
        rubric: EvaluationRubricDB
    ) -> AssignmentDB:
        """Create a published assignment with a client."""
        # Create assignment
        assignment_data = AssignmentCreate(
            title="Published Assignment",
            description="Test published assignment",
            type=AssignmentType.PRACTICE
        )
        assignment = assignment_service.create_assignment_for_teacher(
            db_session,
            assignment_data=assignment_data,
            section_id=section.id,
            teacher_id=teacher_id
        )
        
        # Add client
        assignment_service.add_client_to_assignment(
            db_session,
            assignment.id,
            test_client.id,
            rubric.id,
            teacher_id
        )
        
        # Publish it
        assignment = assignment_service.publish_assignment(
            db_session,
            assignment.id,
            teacher_id
        )
        
        return assignment
    
    @pytest.fixture
    def draft_assignment(
        self, 
        db_session: Session, 
        section: CourseSectionDB, 
        teacher_id: str
    ) -> AssignmentDB:
        """Create a draft (unpublished) assignment."""
        assignment_data = AssignmentCreate(
            title="Draft Assignment",
            description="Test draft assignment",
            type=AssignmentType.GRADED
        )
        return assignment_service.create_assignment_for_teacher(
            db_session,
            assignment_data=assignment_data,
            section_id=section.id,
            teacher_id=teacher_id
        )
    
    @pytest.fixture
    def future_assignment(
        self, 
        db_session: Session, 
        section: CourseSectionDB, 
        teacher_id: str,
        test_client: ClientProfileDB,
        rubric: EvaluationRubricDB
    ) -> AssignmentDB:
        """Create an assignment available in the future."""
        future_date = datetime.utcnow() + timedelta(days=7)
        assignment_data = AssignmentCreate(
            title="Future Assignment",
            description="Available next week",
            type=AssignmentType.PRACTICE,
            available_from=future_date
        )
        assignment = assignment_service.create_assignment_for_teacher(
            db_session,
            assignment_data=assignment_data,
            section_id=section.id,
            teacher_id=teacher_id
        )
        
        # Add client and publish
        assignment_service.add_client_to_assignment(
            db_session,
            assignment.id,
            test_client.id,
            rubric.id,
            teacher_id
        )
        assignment = assignment_service.publish_assignment(
            db_session,
            assignment.id,
            teacher_id
        )
        
        return assignment
    
    @pytest.fixture
    def past_due_assignment(
        self, 
        db_session: Session, 
        section: CourseSectionDB, 
        teacher_id: str,
        test_client: ClientProfileDB,
        rubric: EvaluationRubricDB
    ) -> AssignmentDB:
        """Create an assignment that's past due."""
        past_date = datetime.utcnow() - timedelta(days=7)
        assignment_data = AssignmentCreate(
            title="Past Due Assignment",
            description="Was due last week",
            type=AssignmentType.GRADED,
            due_date=past_date
        )
        assignment = assignment_service.create_assignment_for_teacher(
            db_session,
            assignment_data=assignment_data,
            section_id=section.id,
            teacher_id=teacher_id
        )
        
        # Add client and publish
        assignment_service.add_client_to_assignment(
            db_session,
            assignment.id,
            test_client.id,
            rubric.id,
            teacher_id
        )
        assignment = assignment_service.publish_assignment(
            db_session,
            assignment.id,
            teacher_id
        )
        
        return assignment
    
    def test_list_student_assignments_enrolled(
        self, 
        client, 
        mock_student_auth,
        enrollment: SectionEnrollmentDB,
        published_assignment: AssignmentDB
    ):
        """Test listing assignments for enrolled student."""
        response = client.get("/api/student/assignments")
        
        assert response.status_code == 200
        assignments = response.json()
        assert len(assignments) == 1
        assert assignments[0]["id"] == published_assignment.id
        assert assignments[0]["title"] == "Published Assignment"
        assert assignments[0]["section_name"] == enrollment.section.name
        assert assignments[0]["client_count"] == 1
    
    def test_list_student_assignments_not_enrolled(
        self, 
        client, 
        mock_another_student_auth,
        published_assignment: AssignmentDB
    ):
        """Test listing assignments returns empty for non-enrolled student."""
        response = client.get("/api/student/assignments")
        
        assert response.status_code == 200
        assignments = response.json()
        assert len(assignments) == 0
    
    def test_list_student_assignments_excludes_draft(
        self, 
        client, 
        mock_student_auth,
        enrollment: SectionEnrollmentDB,
        published_assignment: AssignmentDB,
        draft_assignment: AssignmentDB
    ):
        """Test draft assignments are not shown to students."""
        response = client.get("/api/student/assignments")
        
        assert response.status_code == 200
        assignments = response.json()
        assert len(assignments) == 1
        assert assignments[0]["id"] == published_assignment.id
        # Draft assignment should not be in the list
        assignment_ids = [a["id"] for a in assignments]
        assert draft_assignment.id not in assignment_ids
    
    def test_list_student_assignments_date_filtering(
        self, 
        client, 
        mock_student_auth,
        enrollment: SectionEnrollmentDB,
        published_assignment: AssignmentDB,
        future_assignment: AssignmentDB,
        past_due_assignment: AssignmentDB
    ):
        """Test assignments are filtered by available dates."""
        response = client.get("/api/student/assignments")
        
        assert response.status_code == 200
        assignments = response.json()
        assert len(assignments) == 1
        assert assignments[0]["id"] == published_assignment.id
        
        # Future and past due assignments should not be shown
        assignment_ids = [a["id"] for a in assignments]
        assert future_assignment.id not in assignment_ids
        assert past_due_assignment.id not in assignment_ids
    
    def test_list_student_assignments_multiple_sections(
        self, 
        client, 
        db_session: Session,
        mock_student_auth,
        student_id: str,
        teacher_id: str,
        section: CourseSectionDB,
        another_section: CourseSectionDB,
        enrollment: SectionEnrollmentDB,
        published_assignment: AssignmentDB,
        test_client: ClientProfileDB,
        rubric: EvaluationRubricDB
    ):
        """Test student sees assignments from all enrolled sections."""
        # Enroll in second section
        enrollment_service.enroll_student(db_session, another_section.id, student_id)
        
        # Create assignment in second section
        assignment_data = AssignmentCreate(
            title="Assignment in Section 2",
            type=AssignmentType.PRACTICE
        )
        assignment2 = assignment_service.create_assignment_for_teacher(
            db_session,
            assignment_data=assignment_data,
            section_id=another_section.id,
            teacher_id=teacher_id
        )
        assignment_service.add_client_to_assignment(
            db_session,
            assignment2.id,
            test_client.id,
            rubric.id,
            teacher_id
        )
        assignment_service.publish_assignment(db_session, assignment2.id, teacher_id)
        
        response = client.get("/api/student/assignments")
        
        assert response.status_code == 200
        assignments = response.json()
        assert len(assignments) == 2
        
        # Check both assignments are present
        assignment_ids = {a["id"] for a in assignments}
        assert published_assignment.id in assignment_ids
        assert assignment2.id in assignment_ids
    
    def test_get_student_assignment_success(
        self, 
        client, 
        mock_student_auth,
        enrollment: SectionEnrollmentDB,
        published_assignment: AssignmentDB
    ):
        """Test getting a specific assignment as enrolled student."""
        response = client.get(f"/api/student/assignments/{published_assignment.id}")
        
        assert response.status_code == 200
        assignment = response.json()
        assert assignment["id"] == published_assignment.id
        assert assignment["title"] == "Published Assignment"
        assert assignment["section_name"] == enrollment.section.name
        assert assignment["client_count"] == 1
    
    def test_get_student_assignment_not_enrolled(
        self, 
        client, 
        mock_another_student_auth,
        published_assignment: AssignmentDB
    ):
        """Test 404 when student not enrolled in assignment's section."""
        response = client.get(f"/api/student/assignments/{published_assignment.id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_get_student_assignment_draft(
        self, 
        client, 
        mock_student_auth,
        enrollment: SectionEnrollmentDB,
        draft_assignment: AssignmentDB
    ):
        """Test 404 for draft assignments even if enrolled."""
        response = client.get(f"/api/student/assignments/{draft_assignment.id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_get_student_assignment_future(
        self, 
        client, 
        mock_student_auth,
        enrollment: SectionEnrollmentDB,
        future_assignment: AssignmentDB
    ):
        """Test 404 for assignments not yet available."""
        response = client.get(f"/api/student/assignments/{future_assignment.id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_get_student_assignment_past_due(
        self, 
        client, 
        mock_student_auth,
        enrollment: SectionEnrollmentDB,
        past_due_assignment: AssignmentDB
    ):
        """Test 404 for past due assignments."""
        response = client.get(f"/api/student/assignments/{past_due_assignment.id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_get_student_assignment_nonexistent(
        self, 
        client, 
        mock_student_auth
    ):
        """Test 404 for non-existent assignment."""
        response = client.get("/api/student/assignments/nonexistent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_get_student_assignment_clients(
        self, 
        client, 
        db_session: Session,
        mock_student_auth,
        teacher_id: str,
        enrollment: SectionEnrollmentDB,
        published_assignment: AssignmentDB,
        rubric: EvaluationRubricDB
    ):
        """Test getting assignment clients as enrolled student."""
        # Add another client to the assignment
        client2 = client_service.create(
            db_session,
            name="Second Client",
            age=25,
            gender="Male",
            created_by=teacher_id
        )
        assignment_service.add_client_to_assignment(
            db_session,
            published_assignment.id,
            client2.id,
            rubric.id,
            teacher_id,
            display_order=1
        )
        
        response = client.get(f"/api/student/assignments/{published_assignment.id}/clients")
        
        assert response.status_code == 200
        clients = response.json()
        assert len(clients) == 2
        
        # Check client details
        assert clients[0]["display_order"] == 0
        assert clients[0]["client"]["name"] == "Test Client"
        assert clients[0]["rubric"]["name"] == "Test Rubric"
        
        assert clients[1]["display_order"] == 1
        assert clients[1]["client"]["name"] == "Second Client"
    
    def test_get_student_assignment_clients_not_enrolled(
        self, 
        client, 
        mock_another_student_auth,
        published_assignment: AssignmentDB
    ):
        """Test 404 when getting clients for assignment student can't access."""
        response = client.get(f"/api/student/assignments/{published_assignment.id}/clients")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_get_student_assignment_clients_only_active(
        self, 
        client, 
        db_session: Session,
        mock_student_auth,
        teacher_id: str,
        enrollment: SectionEnrollmentDB,
        published_assignment: AssignmentDB,
        rubric: EvaluationRubricDB
    ):
        """Test only active clients are returned to students."""
        # Add a client then remove it (soft delete)
        client2 = client_service.create(
            db_session,
            name="Removed Client",
            age=40,
            gender="Male",
            created_by=teacher_id
        )
        assignment_service.add_client_to_assignment(
            db_session,
            published_assignment.id,
            client2.id,
            rubric.id,
            teacher_id
        )
        assignment_service.remove_client_from_assignment(
            db_session,
            published_assignment.id,
            client2.id,
            teacher_id
        )
        
        response = client.get(f"/api/student/assignments/{published_assignment.id}/clients")
        
        assert response.status_code == 200
        clients = response.json()
        assert len(clients) == 1  # Only the active client
        assert clients[0]["client"]["name"] == "Test Client"
        
        # Removed client should not be in the list
        client_names = [c["client"]["name"] for c in clients]
        assert "Removed Client" not in client_names
    
    def test_assignment_date_boundary_available_from(
        self, 
        client, 
        db_session: Session,
        mock_student_auth,
        teacher_id: str,
        section: CourseSectionDB,
        enrollment: SectionEnrollmentDB,
        test_client: ClientProfileDB,
        rubric: EvaluationRubricDB
    ):
        """Test assignment becomes available exactly at available_from time."""
        # Create assignment available in 1 second
        available_time = datetime.utcnow() + timedelta(seconds=1)
        assignment_data = AssignmentCreate(
            title="Time Boundary Test",
            type=AssignmentType.PRACTICE,
            available_from=available_time
        )
        assignment = assignment_service.create_assignment_for_teacher(
            db_session,
            assignment_data=assignment_data,
            section_id=section.id,
            teacher_id=teacher_id
        )
        assignment_service.add_client_to_assignment(
            db_session,
            assignment.id,
            test_client.id,
            rubric.id,
            teacher_id
        )
        assignment_service.publish_assignment(db_session, assignment.id, teacher_id)
        
        # Should not be available yet
        response = client.get("/api/student/assignments")
        assert response.status_code == 200
        assert len(response.json()) == 0
        
        # Wait for it to become available
        import time
        time.sleep(2)
        
        # Now it should be available
        response = client.get("/api/student/assignments")
        assert response.status_code == 200
        assignments = response.json()
        assert len(assignments) == 1
        assert assignments[0]["id"] == assignment.id
