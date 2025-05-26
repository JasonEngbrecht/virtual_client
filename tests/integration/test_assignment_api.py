"""
Integration tests for assignment API endpoints.
Tests the full flow of assignment management through the API.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.models.assignment import AssignmentType


class TestAssignmentAPI:
    """Test assignment CRUD operations through the API"""
    
    def test_create_assignment_success(
        self, 
        client, 
        test_section_with_teacher, 
        mock_teacher_auth
    ):
        """Test creating a new assignment in a section"""
        section_id = test_section_with_teacher["section_id"]
        
        assignment_data = {
            "title": "Client Interview Practice",
            "description": "Practice conducting an initial assessment",
            "type": "practice",
            "settings": {
                "time_limit": 30,
                "allow_notes": True
            },
            "max_attempts": 3
        }
        
        response = client.post(
            f"/api/teacher/sections/{section_id}/assignments",
            json=assignment_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == assignment_data["title"]
        assert data["description"] == assignment_data["description"]
        assert data["type"] == assignment_data["type"]
        assert data["settings"] == assignment_data["settings"]
        assert data["max_attempts"] == assignment_data["max_attempts"]
        assert data["is_published"] is False  # Default to draft
        assert data["section_id"] == section_id
    
    def test_create_assignment_with_dates(
        self, 
        client, 
        test_section_with_teacher, 
        mock_teacher_auth
    ):
        """Test creating an assignment with availability dates"""
        section_id = test_section_with_teacher["section_id"]
        
        available_from = datetime.utcnow() + timedelta(days=1)
        due_date = datetime.utcnow() + timedelta(days=7)
        
        assignment_data = {
            "title": "Graded Assessment",
            "type": "graded",
            "available_from": available_from.isoformat() + "Z",
            "due_date": due_date.isoformat() + "Z"
        }
        
        response = client.post(
            f"/api/teacher/sections/{section_id}/assignments",
            json=assignment_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["available_from"] is not None
        assert data["due_date"] is not None
    
    def test_create_assignment_invalid_dates(
        self, 
        client, 
        test_section_with_teacher, 
        mock_teacher_auth
    ):
        """Test creating assignment with invalid date range fails"""
        section_id = test_section_with_teacher["section_id"]
        
        # Due date before available_from
        assignment_data = {
            "title": "Invalid Assignment",
            "available_from": "2025-02-15T00:00:00Z",
            "due_date": "2025-02-01T00:00:00Z"
        }
        
        response = client.post(
            f"/api/teacher/sections/{section_id}/assignments",
            json=assignment_data
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_assignment_unauthorized_section(
        self, 
        client, 
        test_section_other_teacher, 
        mock_teacher_auth
    ):
        """Test creating assignment in another teacher's section fails"""
        # test_section_other_teacher belongs to a different teacher
        section_id = test_section_other_teacher.id
        
        assignment_data = {
            "title": "Unauthorized Assignment"
        }
        
        response = client.post(
            f"/api/teacher/sections/{section_id}/assignments",
            json=assignment_data
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_create_assignment_nonexistent_section(
        self, 
        client, 
        mock_teacher_auth
    ):
        """Test creating assignment in non-existent section fails"""
        response = client.post(
            "/api/teacher/sections/nonexistent-section/assignments",
            json={"title": "Test Assignment"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_list_section_assignments(
        self, 
        client, 
        test_section_with_teacher, 
        test_assignments,
        mock_teacher_auth
    ):
        """Test listing assignments in a section"""
        section_id = test_section_with_teacher["section_id"]
        
        response = client.get(
            f"/api/teacher/sections/{section_id}/assignments"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2  # test_assignments creates 2 assignments
        
        # Should be ordered by created_at desc
        assert data[0]["title"] == "Test Assignment 2"
        assert data[1]["title"] == "Test Assignment 1"
    
    def test_list_section_assignments_filter_published(
        self, 
        client, 
        test_section_with_teacher, 
        test_assignments,
        mock_teacher_auth
    ):
        """Test listing only published assignments"""
        section_id = test_section_with_teacher["section_id"]
        
        response = client.get(
            f"/api/teacher/sections/{section_id}/assignments",
            params={"include_draft": False}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1  # Only one published assignment
        assert data[0]["is_published"] is True
    
    def test_list_section_assignments_unauthorized(
        self, 
        client, 
        test_section_other_teacher, 
        mock_teacher_auth
    ):
        """Test listing assignments in another teacher's section fails"""
        response = client.get(
            f"/api/teacher/sections/{test_section_other_teacher.id}/assignments"
        )
        
        assert response.status_code == 403
    
    def test_list_teacher_assignments(
        self, 
        client, 
        test_assignments,
        mock_teacher_auth
    ):
        """Test listing all assignments for a teacher"""
        response = client.get("/api/teacher/assignments")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least the test assignments
    
    def test_list_teacher_assignments_with_pagination(
        self, 
        client, 
        test_assignments,
        mock_teacher_auth
    ):
        """Test pagination when listing teacher assignments"""
        # First page
        response = client.get(
            "/api/teacher/assignments",
            params={"skip": 0, "limit": 1}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        first_assignment = data[0]
        
        # Second page
        response = client.get(
            "/api/teacher/assignments",
            params={"skip": 1, "limit": 1}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] != first_assignment["id"]
    
    def test_list_teacher_assignments_filter_section(
        self, 
        client, 
        test_section_with_teacher,
        test_assignments,
        mock_teacher_auth
    ):
        """Test filtering assignments by section"""
        section_id = test_section_with_teacher["section_id"]
        
        response = client.get(
            "/api/teacher/assignments",
            params={"section_id": section_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(a["section_id"] == section_id for a in data)
    
    def test_get_assignment_success(
        self, 
        client, 
        test_assignments,
        mock_teacher_auth
    ):
        """Test getting a specific assignment"""
        assignment_id = test_assignments[0].id
        
        response = client.get(f"/api/teacher/assignments/{assignment_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == assignment_id
        assert data["title"] == test_assignments[0].title
    
    def test_get_assignment_unauthorized(
        self, 
        client, 
        test_assignment_other_teacher,
        mock_teacher_auth
    ):
        """Test getting assignment from another teacher's section fails"""
        assignment_id = test_assignment_other_teacher.id
        
        response = client.get(f"/api/teacher/assignments/{assignment_id}")
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_get_assignment_not_found(
        self, 
        client, 
        mock_teacher_auth
    ):
        """Test getting non-existent assignment fails"""
        response = client.get("/api/teacher/assignments/nonexistent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_assignment_success(
        self, 
        client, 
        test_assignments,
        mock_teacher_auth
    ):
        """Test updating an assignment"""
        assignment = test_assignments[0]  # Draft assignment
        
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "max_attempts": 5
        }
        
        response = client.put(
            f"/api/teacher/assignments/{assignment.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["max_attempts"] == update_data["max_attempts"]
    
    def test_update_published_assignment_restrictions(
        self, 
        client, 
        test_assignments,
        mock_teacher_auth
    ):
        """Test that published assignments have limited update capabilities"""
        assignment = test_assignments[1]  # Published assignment
        
        # Try to update restricted fields
        update_data = {
            "title": "New Title",  # Restricted
            "type": "graded",  # Restricted
            "description": "New description",  # Allowed
            "due_date": (datetime.utcnow() + timedelta(days=10)).isoformat() + "Z"  # Allowed
        }
        
        response = client.put(
            f"/api/teacher/assignments/{assignment.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        # Restricted fields should not change
        assert data["title"] == assignment.title  # Original title
        assert data["type"] == assignment.type.value  # Original type
        # Allowed fields should change
        assert data["description"] == update_data["description"]
        assert data["due_date"] is not None
    
    def test_update_assignment_unauthorized(
        self, 
        client, 
        test_assignment_other_teacher,
        mock_teacher_auth
    ):
        """Test updating another teacher's assignment fails"""
        response = client.put(
            f"/api/teacher/assignments/{test_assignment_other_teacher.id}",
            json={"title": "Unauthorized Update"}
        )
        
        assert response.status_code == 403
    
    def test_update_assignment_no_fields(
        self, 
        client, 
        test_assignments,
        mock_teacher_auth
    ):
        """Test updating with no valid fields fails"""
        response = client.put(
            f"/api/teacher/assignments/{test_assignments[0].id}",
            json={}
        )
        
        assert response.status_code == 400
        assert "no valid fields" in response.json()["detail"].lower()
    
    def test_delete_assignment_success(
        self, 
        client, 
        test_assignments,
        mock_teacher_auth
    ):
        """Test deleting a draft assignment"""
        assignment = test_assignments[0]  # Draft assignment
        
        response = client.delete(f"/api/teacher/assignments/{assignment.id}")
        
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get(f"/api/teacher/assignments/{assignment.id}")
        assert response.status_code == 404
    
    def test_delete_published_assignment_fails(
        self, 
        client, 
        test_assignments,
        mock_teacher_auth
    ):
        """Test that published assignments cannot be deleted"""
        assignment = test_assignments[1]  # Published assignment
        
        response = client.delete(f"/api/teacher/assignments/{assignment.id}")
        
        assert response.status_code == 409
        assert "unpublish" in response.json()["detail"].lower()
    
    def test_delete_assignment_unauthorized(
        self, 
        client, 
        test_assignment_other_teacher,
        mock_teacher_auth
    ):
        """Test deleting another teacher's assignment fails"""
        response = client.delete(
            f"/api/teacher/assignments/{test_assignment_other_teacher.id}"
        )
        
        assert response.status_code == 403
    
    def test_delete_assignment_not_found(
        self, 
        client, 
        mock_teacher_auth
    ):
        """Test deleting non-existent assignment fails"""
        response = client.delete("/api/teacher/assignments/nonexistent-id")
        
        assert response.status_code == 404


class TestAssignmentAPIEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_create_assignment_invalid_type(
        self, 
        client, 
        test_section_with_teacher,
        mock_teacher_auth
    ):
        """Test creating assignment with invalid type fails"""
        section_id = test_section_with_teacher["section_id"]
        
        response = client.post(
            f"/api/teacher/sections/{section_id}/assignments",
            json={
                "title": "Invalid Type",
                "type": "invalid_type"
            }
        )
        
        assert response.status_code == 422
    
    def test_create_assignment_negative_attempts(
        self, 
        client, 
        test_section_with_teacher,
        mock_teacher_auth
    ):
        """Test creating assignment with negative max_attempts fails"""
        section_id = test_section_with_teacher["section_id"]
        
        response = client.post(
            f"/api/teacher/sections/{section_id}/assignments",
            json={
                "title": "Negative Attempts",
                "max_attempts": -1
            }
        )
        
        assert response.status_code == 422
    
    def test_update_assignment_invalid_dates(
        self, 
        client, 
        test_assignments,
        mock_teacher_auth
    ):
        """Test updating assignment with invalid date range fails"""
        assignment = test_assignments[0]
        
        response = client.put(
            f"/api/teacher/assignments/{assignment.id}",
            json={
                "available_from": "2025-02-15T00:00:00Z",
                "due_date": "2025-02-01T00:00:00Z"
            }
        )
        
        assert response.status_code == 422


class TestAssignmentAPIWorkflow:
    """Test complete assignment workflows"""
    
    def test_complete_assignment_workflow(
        self,
        client,
        test_section_with_teacher,
        mock_teacher_auth
    ):
        """Test a complete workflow: create, read, update, delete"""
        section_id = test_section_with_teacher["section_id"]
        
        # Create assignment
        create_data = {
            "title": "Workflow Test Assignment",
            "description": "Testing complete workflow",
            "type": "practice",
            "max_attempts": 2
        }
        create_response = client.post(
            f"/api/teacher/sections/{section_id}/assignments",
            json=create_data
        )
        assert create_response.status_code == 201
        assignment_id = create_response.json()["id"]
        
        # Read assignment
        get_response = client.get(f"/api/teacher/assignments/{assignment_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == create_data["title"]
        
        # Update assignment
        update_data = {"title": "Updated Workflow Assignment"}
        update_response = client.put(
            f"/api/teacher/assignments/{assignment_id}",
            json=update_data
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == update_data["title"]
        
        # List assignments (should contain our assignment)
        list_response = client.get(
            f"/api/teacher/sections/{section_id}/assignments"
        )
        assert list_response.status_code == 200
        assignments = list_response.json()
        assert any(a["id"] == assignment_id for a in assignments)
        
        # Delete assignment
        delete_response = client.delete(f"/api/teacher/assignments/{assignment_id}")
        assert delete_response.status_code == 204
        
        # Verify deleted
        verify_response = client.get(f"/api/teacher/assignments/{assignment_id}")
        assert verify_response.status_code == 404
