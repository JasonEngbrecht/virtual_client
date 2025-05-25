"""
Integration tests for student section API endpoints

Tests the student-specific endpoints for viewing enrolled sections.
Students have read-only access to their enrolled sections.
"""

import pytest
from uuid import uuid4

from backend.models.course_section import CourseSectionDB, SectionEnrollmentDB
from backend.services.section_service import section_service
from backend.services.enrollment_service import enrollment_service


@pytest.fixture
def mock_student_auth(client):
    """Mock student authentication for tests"""
    from backend.app import app
    from backend.api.student_routes import get_current_student
    
    # Override the authentication dependency
    def override_get_current_student():
        return "student-123"
    
    app.dependency_overrides[get_current_student] = override_get_current_student
    yield
    # Cleanup is handled by client fixture clearing all overrides


@pytest.fixture
def sample_sections(db_session):
    """Create sample sections with enrollments for testing"""
    teacher_id = "teacher-456"  # Different from mock student
    student_id = "student-123"  # Matches mock auth
    other_student_id = "student-999"
    
    # Create three sections
    section1 = section_service.create(
        db_session,
        name="Computer Science 101 - Fall 2024",
        course_code="CS101",
        term="Fall 2024",
        teacher_id=teacher_id
    )
    
    section2 = section_service.create(
        db_session,
        name="Computer Science 102 - Fall 2024",
        course_code="CS102",
        term="Fall 2024",
        teacher_id=teacher_id
    )
    
    section3 = section_service.create(
        db_session,
        name="Computer Science 103 - Fall 2024",
        course_code="CS103",
        term="Fall 2024",
        teacher_id=teacher_id
    )
    
    # Enroll student in section1 and section2
    enrollment_service.enroll_student(db_session, section1.id, student_id)
    enrollment_service.enroll_student(db_session, section2.id, student_id)
    
    # Enroll other student in section3
    enrollment_service.enroll_student(db_session, section3.id, other_student_id)
    
    return {
        "enrolled_sections": [section1, section2],
        "not_enrolled_section": section3,
        "student_id": student_id,
        "other_student_id": other_student_id
    }


class TestStudentSectionList:
    """Test the GET /api/student/sections endpoint"""
    
    def test_list_enrolled_sections(self, client, mock_student_auth, sample_sections):
        """Test student can list their enrolled sections"""
        response = client.get("/api/student/sections")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return 2 sections
        assert len(data) == 2
        
        # Check that both enrolled sections are returned
        section_ids = {section["id"] for section in data}
        expected_ids = {s.id for s in sample_sections["enrolled_sections"]}
        assert section_ids == expected_ids
        
        # Verify section data structure
        for section in data:
            assert "id" in section
            assert "course_code" in section
            assert "name" in section
            assert "term" in section
            assert "teacher_id" in section
            assert "created_at" in section
            assert "is_active" in section
    
    def test_list_empty_when_no_enrollments(self, client, mock_student_auth, db_session):
        """Test empty list when student has no enrollments"""
        response = client.get("/api/student/sections")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_inactive_enrollments_not_shown(self, client, mock_student_auth, sample_sections, db_session):
        """Test that inactive enrollments are not returned"""
        # Unenroll student from one section
        section_to_unenroll = sample_sections["enrolled_sections"][0]
        enrollment_service.unenroll_student(
            db_session,
            section_to_unenroll.id,
            sample_sections["student_id"]
        )
        
        response = client.get("/api/student/sections")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only return 1 active enrollment
        assert len(data) == 1
        assert data[0]["id"] == sample_sections["enrolled_sections"][1].id


class TestStudentSectionDetail:
    """Test the GET /api/student/sections/{id} endpoint"""
    
    def test_get_enrolled_section(self, client, mock_student_auth, sample_sections):
        """Test student can get details of enrolled section"""
        section = sample_sections["enrolled_sections"][0]
        response = client.get(f"/api/student/sections/{section.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify section details
        assert data["id"] == section.id
        assert data["course_code"] == section.course_code
        assert data["name"] == section.name
        assert data["term"] == section.term
        assert data["teacher_id"] == section.teacher_id
    
    def test_404_for_non_enrolled_section(self, client, mock_student_auth, sample_sections):
        """Test 404 returned for sections student is not enrolled in"""
        section = sample_sections["not_enrolled_section"]
        response = client.get(f"/api/student/sections/{section.id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_404_for_nonexistent_section(self, client, mock_student_auth):
        """Test 404 returned for section that doesn't exist"""
        response = client.get("/api/student/sections/nonexistent-id")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_404_for_inactive_enrollment(self, client, mock_student_auth, sample_sections, db_session):
        """Test 404 returned for inactive enrollments"""
        # Unenroll student from section
        section = sample_sections["enrolled_sections"][0]
        enrollment_service.unenroll_student(
            db_session,
            section.id,
            sample_sections["student_id"]
        )
        
        response = client.get(f"/api/student/sections/{section.id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestStudentSecurityRestrictions:
    """Test security restrictions for student endpoints"""
    
    def test_no_update_operations(self, client, mock_student_auth):
        """Test that PUT endpoints are not available"""
        response = client.put("/api/student/sections/some-id", json={})
        # Should get 404 or 405, not a valid endpoint
        assert response.status_code in [404, 405]
    
    def test_no_delete_operations(self, client, mock_student_auth):
        """Test that DELETE endpoints are not available"""
        response = client.delete("/api/student/sections/some-id")
        # Should get 404 or 405, not a valid endpoint
        assert response.status_code in [404, 405]
    
    def test_no_create_operations(self, client, mock_student_auth):
        """Test that POST endpoints are not available"""
        response = client.post("/api/student/sections", json={})
        # Should get 404 or 405, not a valid endpoint
        assert response.status_code in [404, 405]
    
    def test_cannot_access_roster(self, client, mock_student_auth, sample_sections):
        """Test that students cannot access section rosters"""
        section = sample_sections["enrolled_sections"][0]
        # This endpoint should not exist for students
        response = client.get(f"/api/student/sections/{section.id}/roster")
        assert response.status_code in [404, 405]
