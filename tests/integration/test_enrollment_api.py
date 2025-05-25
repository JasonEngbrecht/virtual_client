"""
Integration tests for enrollment management endpoints
"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


class TestEnrollmentAPI:
    """Test enrollment management endpoints"""
    
    def test_get_section_roster_empty(self, client: TestClient, mock_teacher_auth, test_section):
        """Test getting roster for section with no enrollments"""
        response = client.get(f"/api/teacher/sections/{test_section.id}/roster")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_section_roster_not_found(self, client: TestClient, mock_teacher_auth):
        """Test getting roster for non-existent section"""
        fake_id = str(uuid4())
        response = client.get(f"/api/teacher/sections/{fake_id}/roster")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_section_roster_wrong_teacher(self, client: TestClient, mock_teacher_auth, test_section_other_teacher):
        """Test getting roster for another teacher's section"""
        response = client.get(f"/api/teacher/sections/{test_section_other_teacher.id}/roster")
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_enroll_student_success(self, client: TestClient, mock_teacher_auth, test_section):
        """Test successfully enrolling a student"""
        enrollment_data = {
            "student_id": "student-123",
            "role": "student"
        }
        
        response = client.post(
            f"/api/teacher/sections/{test_section.id}/enroll",
            json=enrollment_data
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["student_id"] == "student-123"
        assert data["section_id"] == test_section.id
        assert data["role"] == "student"
        assert data["is_active"] is True
        assert "enrolled_at" in data
        assert "id" in data
    
    def test_enroll_student_duplicate(self, client: TestClient, mock_teacher_auth, test_section):
        """Test enrolling same student twice returns existing enrollment"""
        enrollment_data = {
            "student_id": "student-456",
            "role": "student"
        }
        
        # First enrollment
        response1 = client.post(
            f"/api/teacher/sections/{test_section.id}/enroll",
            json=enrollment_data
        )
        assert response1.status_code == 201
        enrollment1 = response1.json()
        
        # Second enrollment attempt
        response2 = client.post(
            f"/api/teacher/sections/{test_section.id}/enroll",
            json=enrollment_data
        )
        assert response2.status_code == 201
        enrollment2 = response2.json()
        
        # Should return the same enrollment
        assert enrollment1["id"] == enrollment2["id"]
        assert enrollment2["is_active"] is True
    
    def test_enroll_student_reactivate(self, client: TestClient, mock_teacher_auth, test_section, db_session):
        """Test re-enrolling a previously unenrolled student reactivates enrollment"""
        student_id = "student-789"
        enrollment_data = {
            "student_id": student_id,
            "role": "student"
        }
        
        # Enroll student
        response1 = client.post(
            f"/api/teacher/sections/{test_section.id}/enroll",
            json=enrollment_data
        )
        assert response1.status_code == 201
        enrollment_id = response1.json()["id"]
        
        # Unenroll student
        response2 = client.delete(
            f"/api/teacher/sections/{test_section.id}/enroll/{student_id}"
        )
        assert response2.status_code == 204
        
        # Re-enroll student
        response3 = client.post(
            f"/api/teacher/sections/{test_section.id}/enroll",
            json=enrollment_data
        )
        assert response3.status_code == 201
        
        data = response3.json()
        assert data["id"] == enrollment_id  # Same enrollment record
        assert data["is_active"] is True  # Reactivated
    
    def test_enroll_student_section_not_found(self, client: TestClient, mock_teacher_auth):
        """Test enrolling student in non-existent section"""
        fake_id = str(uuid4())
        enrollment_data = {
            "student_id": "student-123",
            "role": "student"
        }
        
        response = client.post(
            f"/api/teacher/sections/{fake_id}/enroll",
            json=enrollment_data
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_enroll_student_wrong_teacher(self, client: TestClient, mock_teacher_auth, test_section_other_teacher):
        """Test enrolling student in another teacher's section"""
        enrollment_data = {
            "student_id": "student-123",
            "role": "student"
        }
        
        response = client.post(
            f"/api/teacher/sections/{test_section_other_teacher.id}/enroll",
            json=enrollment_data
        )
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_enroll_student_invalid_role(self, client: TestClient, mock_teacher_auth, test_section):
        """Test enrolling student with invalid role"""
        enrollment_data = {
            "student_id": "student-123",
            "role": "invalid_role"
        }
        
        response = client.post(
            f"/api/teacher/sections/{test_section.id}/enroll",
            json=enrollment_data
        )
        assert response.status_code == 422  # Pydantic validation error
    
    def test_unenroll_student_success(self, client: TestClient, mock_teacher_auth, test_section):
        """Test successfully unenrolling a student"""
        # First enroll a student
        student_id = "student-999"
        enrollment_data = {
            "student_id": student_id,
            "role": "student"
        }
        
        response1 = client.post(
            f"/api/teacher/sections/{test_section.id}/enroll",
            json=enrollment_data
        )
        assert response1.status_code == 201
        
        # Then unenroll
        response2 = client.delete(
            f"/api/teacher/sections/{test_section.id}/enroll/{student_id}"
        )
        assert response2.status_code == 204
        
        # Verify student is no longer in active roster
        response3 = client.get(f"/api/teacher/sections/{test_section.id}/roster")
        assert response3.status_code == 200
        roster = response3.json()
        assert not any(e["student_id"] == student_id for e in roster)
    
    def test_unenroll_student_not_enrolled(self, client: TestClient, mock_teacher_auth, test_section):
        """Test unenrolling student who isn't enrolled"""
        response = client.delete(
            f"/api/teacher/sections/{test_section.id}/enroll/not-enrolled-student"
        )
        assert response.status_code == 404
        assert "not actively enrolled" in response.json()["detail"]
    
    def test_unenroll_student_section_not_found(self, client: TestClient, mock_teacher_auth):
        """Test unenrolling from non-existent section"""
        fake_id = str(uuid4())
        response = client.delete(
            f"/api/teacher/sections/{fake_id}/enroll/student-123"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unenroll_student_wrong_teacher(self, client: TestClient, mock_teacher_auth, test_section_other_teacher):
        """Test unenrolling from another teacher's section"""
        response = client.delete(
            f"/api/teacher/sections/{test_section_other_teacher.id}/enroll/student-123"
        )
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_get_roster_with_enrollments(self, client: TestClient, mock_teacher_auth, test_section):
        """Test getting roster with multiple enrollments"""
        # Enroll several students
        student_ids = ["student-101", "student-102", "student-103"]
        for student_id in student_ids:
            enrollment_data = {
                "student_id": student_id,
                "role": "student"
            }
            response = client.post(
                f"/api/teacher/sections/{test_section.id}/enroll",
                json=enrollment_data
            )
            assert response.status_code == 201
        
        # Get roster
        response = client.get(f"/api/teacher/sections/{test_section.id}/roster")
        assert response.status_code == 200
        
        roster = response.json()
        assert len(roster) == 3
        
        # Verify all students are in roster
        roster_student_ids = {e["student_id"] for e in roster}
        assert roster_student_ids == set(student_ids)
        
        # Verify all enrollments are active
        assert all(e["is_active"] for e in roster)
    
    def test_enrollment_soft_delete_history(self, client: TestClient, mock_teacher_auth, test_section, db_session):
        """Test that unenrollment preserves history (soft delete)"""
        from backend.services.enrollment_service import enrollment_service
        
        # Enroll and unenroll a student
        student_id = "student-history"
        enrollment_data = {
            "student_id": student_id,
            "role": "student"
        }
        
        # Enroll
        response1 = client.post(
            f"/api/teacher/sections/{test_section.id}/enroll",
            json=enrollment_data
        )
        assert response1.status_code == 201
        
        # Unenroll
        response2 = client.delete(
            f"/api/teacher/sections/{test_section.id}/enroll/{student_id}"
        )
        assert response2.status_code == 204
        
        # Check that enrollment still exists in database (inactive)
        enrollment = enrollment_service.get_enrollment(
            db_session,
            test_section.id,
            student_id
        )
        assert enrollment is not None
        assert enrollment.is_active is False
