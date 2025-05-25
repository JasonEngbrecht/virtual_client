"""
Integration tests for section statistics API endpoints
"""

import pytest
from uuid import uuid4

from backend.models.course_section import CourseSectionDB, SectionEnrollmentDB
from backend.services.section_service import section_service
from backend.services.enrollment_service import enrollment_service


class TestSectionStatsAPI:
    """Test section statistics endpoints"""
    
    def test_get_section_stats_with_enrollments(self, client, mock_teacher_auth):
        """Test getting statistics for a section with enrollments"""
        # Create a section via API
        section_data = {
            "name": "Stats Test Section",
            "description": "Section with enrollments for stats testing",
            "course_code": "STAT101",
            "term": "Fall 2025"
        }
        create_response = client.post("/api/teacher/sections", json=section_data)
        assert create_response.status_code == 201
        section_id = create_response.json()["id"]
        
        # Enroll students via API
        student_ids = ["student-001", "student-002", "student-003", "student-004"]
        
        # Create 3 active enrollments
        for student_id in student_ids[:3]:
            enrollment_data = {"student_id": student_id, "role": "student"}
            response = client.post(f"/api/teacher/sections/{section_id}/enroll", json=enrollment_data)
            assert response.status_code == 201
        
        # Create 1 inactive enrollment (enroll then unenroll)
        enrollment_data = {"student_id": student_ids[3], "role": "student"}
        response = client.post(f"/api/teacher/sections/{section_id}/enroll", json=enrollment_data)
        assert response.status_code == 201
        response = client.delete(f"/api/teacher/sections/{section_id}/enroll/{student_ids[3]}")
        assert response.status_code == 204
        
        # Get statistics
        response = client.get(f"/api/teacher/sections/{section_id}/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["section_id"] == section_id
        assert data["name"] == "Stats Test Section"
        assert data["active_enrollments"] == 3
        assert data["inactive_enrollments"] == 1
        assert data["total_enrollments"] == 4
    
    def test_get_section_stats_no_enrollments(self, client, mock_teacher_auth):
        """Test getting statistics for a section with no enrollments"""
        # Create a section via API
        section_data = {
            "name": "Empty Test Section",
            "description": "Section with no enrollments",
            "course_code": "EMPTY101",
            "term": "Fall 2025"
        }
        create_response = client.post("/api/teacher/sections", json=section_data)
        assert create_response.status_code == 201
        section_id = create_response.json()["id"]
        
        # Get statistics
        response = client.get(f"/api/teacher/sections/{section_id}/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["section_id"] == section_id
        assert data["name"] == "Empty Test Section"
        assert data["active_enrollments"] == 0
        assert data["inactive_enrollments"] == 0
        assert data["total_enrollments"] == 0
    
    def test_get_all_sections_stats(self, client, mock_teacher_auth):
        """Test getting statistics for all teacher's sections"""
        # Create two sections
        section1_data = {
            "name": "Stats Section 1",
            "description": "First section",
            "course_code": "STAT201"
        }
        response1 = client.post("/api/teacher/sections", json=section1_data)
        assert response1.status_code == 201
        section1_id = response1.json()["id"]
        
        section2_data = {
            "name": "Stats Section 2",
            "description": "Second section",
            "course_code": "STAT202"
        }
        response2 = client.post("/api/teacher/sections", json=section2_data)
        assert response2.status_code == 201
        section2_id = response2.json()["id"]
        
        # Add enrollments to section1
        for i in range(3):
            enrollment_data = {"student_id": f"student-{i}", "role": "student"}
            response = client.post(f"/api/teacher/sections/{section1_id}/enroll", json=enrollment_data)
            assert response.status_code == 201
        
        # Get all stats
        response = client.get("/api/teacher/sections/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have at least our 2 sections
        assert len(data) >= 2
        
        # Find our sections
        section1_stats = next((s for s in data if s["section_id"] == section1_id), None)
        section2_stats = next((s for s in data if s["section_id"] == section2_id), None)
        
        assert section1_stats is not None
        assert section1_stats["name"] == "Stats Section 1"
        assert section1_stats["active_enrollments"] == 3
        assert section1_stats["inactive_enrollments"] == 0
        assert section1_stats["total_enrollments"] == 3
        
        assert section2_stats is not None
        assert section2_stats["name"] == "Stats Section 2"
        assert section2_stats["active_enrollments"] == 0
        assert section2_stats["inactive_enrollments"] == 0
        assert section2_stats["total_enrollments"] == 0
    
    def test_get_section_stats_not_found(self, client, mock_teacher_auth):
        """Test getting statistics for non-existent section"""
        response = client.get("/api/teacher/sections/nonexistent-id/stats")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_section_stats_forbidden(self, client, mock_teacher_auth, db_session):
        """Test getting statistics for another teacher's section"""
        # Create a section for a different teacher
        section = CourseSectionDB(
            id=str(uuid4()),
            teacher_id="teacher-456",  # Different teacher
            name="Another Teacher Section",
            description="Belongs to another teacher",
            course_code="FORBIDDEN101",
            term="Fall 2025",
            is_active=True,
            settings={}
        )
        db_session.add(section)
        db_session.commit()
        
        # Try to get stats as teacher-123
        response = client.get(f"/api/teacher/sections/{section.id}/stats")
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_inactive_enrollment_counting(self, client, mock_teacher_auth):
        """Test that inactive enrollments are counted correctly"""
        # Create a section
        section_data = {"name": "Inactive Enrollment Test"}
        create_response = client.post("/api/teacher/sections", json=section_data)
        assert create_response.status_code == 201
        section_id = create_response.json()["id"]
        
        # Enroll and unenroll students
        student_ids = ["student-005", "student-006", "student-007"]
        
        for student_id in student_ids:
            # Enroll
            enrollment_data = {"student_id": student_id, "role": "student"}
            response = client.post(f"/api/teacher/sections/{section_id}/enroll", json=enrollment_data)
            assert response.status_code == 201
            
            # Unenroll first two students
            if student_id != "student-007":
                response = client.delete(f"/api/teacher/sections/{section_id}/enroll/{student_id}")
                assert response.status_code == 204
        
        # Get stats
        response = client.get(f"/api/teacher/sections/{section_id}/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["active_enrollments"] == 1  # Only student-007 is active
        assert data["inactive_enrollments"] == 2  # student-005 and student-006
        assert data["total_enrollments"] == 3
    
    def test_stats_performance_many_sections(self, client, mock_teacher_auth):
        """Test that bulk stats endpoint uses efficient queries"""
        # Create multiple sections with varying enrollments
        created_section_ids = []
        
        for i in range(5):
            section_data = {
                "name": f"Performance Test Section {i}",
                "description": "Testing bulk query performance",
                "course_code": f"PERF{i:03d}"
            }
            create_response = client.post("/api/teacher/sections", json=section_data)
            assert create_response.status_code == 201
            section_id = create_response.json()["id"]
            created_section_ids.append(section_id)
            
            # Add varying enrollments
            for j in range(i + 1):
                enrollment_data = {
                    "student_id": f"perf-student-{i}-{j}",
                    "role": "student"
                }
                response = client.post(f"/api/teacher/sections/{section_id}/enroll", json=enrollment_data)
                assert response.status_code == 201
        
        # Get all stats
        response = client.get("/api/teacher/sections/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify our performance test sections are in results
        perf_sections = [s for s in data if "Performance Test Section" in s["name"]]
        assert len(perf_sections) == 5
        
        # Verify enrollment counts
        for section_stats in perf_sections:
            if "Performance Test Section 0" in section_stats["name"]:
                assert section_stats["active_enrollments"] == 1
            elif "Performance Test Section 4" in section_stats["name"]:
                assert section_stats["active_enrollments"] == 5
