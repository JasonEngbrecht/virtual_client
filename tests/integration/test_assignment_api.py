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


class TestAssignmentPublishing:
    """Test assignment publishing/unpublishing endpoints"""
    
    def test_publish_assignment_success(
        self,
        client,
        test_assignments,
        sample_client_profile,
        sample_rubric,
        db_session,
        mock_teacher_auth
    ):
        """Test successfully publishing an assignment"""
        assignment = test_assignments[0]  # Draft assignment
        
        # First add a client-rubric pair to the assignment
        from backend.models.assignment import AssignmentClientDB
        from uuid import uuid4
        
        assignment_client = AssignmentClientDB(
            id=str(uuid4()),
            assignment_id=assignment.id,
            client_id=sample_client_profile.id,
            rubric_id=sample_rubric.id,
            is_active=True,
            display_order=1
        )
        db_session.add(assignment_client)
        db_session.commit()
        
        # Now publish the assignment
        response = client.post(f"/api/teacher/assignments/{assignment.id}/publish")
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_published"] is True
        assert data["id"] == assignment.id
    
    def test_publish_already_published_assignment(
        self,
        client,
        test_assignments,
        mock_teacher_auth
    ):
        """Test publishing an already published assignment succeeds"""
        assignment = test_assignments[1]  # Already published
        
        response = client.post(f"/api/teacher/assignments/{assignment.id}/publish")
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_published"] is True
    
    def test_publish_assignment_no_clients(
        self,
        client,
        test_assignments,
        mock_teacher_auth
    ):
        """Test publishing assignment without active clients fails"""
        assignment = test_assignments[0]  # Draft with no clients
        
        response = client.post(f"/api/teacher/assignments/{assignment.id}/publish")
        
        assert response.status_code == 400
        assert "client-rubric pair" in response.json()["detail"].lower()
    
    def test_publish_assignment_unauthorized(
        self,
        client,
        test_assignment_other_teacher,
        mock_teacher_auth
    ):
        """Test publishing another teacher's assignment fails"""
        response = client.post(
            f"/api/teacher/assignments/{test_assignment_other_teacher.id}/publish"
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_publish_assignment_not_found(
        self,
        client,
        mock_teacher_auth
    ):
        """Test publishing non-existent assignment fails"""
        response = client.post("/api/teacher/assignments/nonexistent-id/publish")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unpublish_assignment_success(
        self,
        client,
        test_assignments,
        mock_teacher_auth
    ):
        """Test successfully unpublishing an assignment"""
        assignment = test_assignments[1]  # Published assignment
        
        response = client.post(f"/api/teacher/assignments/{assignment.id}/unpublish")
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_published"] is False
        assert data["id"] == assignment.id
    
    def test_unpublish_already_unpublished_assignment(
        self,
        client,
        test_assignments,
        mock_teacher_auth
    ):
        """Test unpublishing an already unpublished assignment succeeds"""
        assignment = test_assignments[0]  # Already unpublished (draft)
        
        response = client.post(f"/api/teacher/assignments/{assignment.id}/unpublish")
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_published"] is False
    
    def test_unpublish_assignment_unauthorized(
        self,
        client,
        test_assignment_other_teacher,
        mock_teacher_auth
    ):
        """Test unpublishing another teacher's assignment fails"""
        response = client.post(
            f"/api/teacher/assignments/{test_assignment_other_teacher.id}/unpublish"
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_unpublish_assignment_not_found(
        self,
        client,
        mock_teacher_auth
    ):
        """Test unpublishing non-existent assignment fails"""
        response = client.post("/api/teacher/assignments/nonexistent-id/unpublish")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_publish_with_invalid_dates(
        self,
        client,
        test_section_with_teacher,
        sample_client_profile,
        sample_rubric,
        db_session,
        mock_teacher_auth
    ):
        """Test publishing assignment with invalid date range fails"""
        from backend.models.assignment import AssignmentDB, AssignmentClientDB, AssignmentType
        from datetime import datetime, timedelta
        from uuid import uuid4
        
        # Create assignment with invalid dates (due_date before available_from)
        assignment = AssignmentDB(
            id=str(uuid4()),
            section_id=test_section_with_teacher["section_id"],
            title="Invalid Date Assignment",
            type=AssignmentType.PRACTICE,
            is_published=False,
            available_from=datetime.utcnow() + timedelta(days=7),
            due_date=datetime.utcnow() + timedelta(days=1)  # Before available_from!
        )
        db_session.add(assignment)
        
        # Add a client so it would otherwise be publishable
        assignment_client = AssignmentClientDB(
            id=str(uuid4()),
            assignment_id=assignment.id,
            client_id=sample_client_profile.id,
            rubric_id=sample_rubric.id,
            is_active=True,
            display_order=1
        )
        db_session.add(assignment_client)
        db_session.commit()
        
        # Try to publish - should fail due to invalid dates
        response = client.post(f"/api/teacher/assignments/{assignment.id}/publish")
        
        assert response.status_code == 400
        # The service logs this as a warning and returns None, which our endpoint
        # interprets as a permission/client issue. This is expected behavior.
    
    def test_delete_after_unpublish_workflow(
        self,
        client,
        test_assignments,
        mock_teacher_auth
    ):
        """Test workflow: unpublish then delete assignment"""
        assignment = test_assignments[1]  # Published assignment
        
        # First try to delete published assignment - should fail
        delete_response = client.delete(f"/api/teacher/assignments/{assignment.id}")
        assert delete_response.status_code == 409
        assert "unpublish" in delete_response.json()["detail"].lower()
        
        # Unpublish the assignment
        unpublish_response = client.post(f"/api/teacher/assignments/{assignment.id}/unpublish")
        assert unpublish_response.status_code == 200
        assert unpublish_response.json()["is_published"] is False
        
        # Now delete should succeed
        delete_response = client.delete(f"/api/teacher/assignments/{assignment.id}")
        assert delete_response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/api/teacher/assignments/{assignment.id}")
        assert get_response.status_code == 404


class TestAssignmentClientManagement:
    """Test assignment-client management endpoints"""
    
    def test_list_assignment_clients_empty(self, client, test_assignments, mock_teacher_auth):
        """Test listing clients for assignment with no clients"""
        assignment = test_assignments[0]
        
        response = client.get(f"/api/teacher/assignments/{assignment.id}/clients")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_list_assignment_clients_with_data(
        self,
        client,
        test_assignment_with_clients,
        mock_teacher_auth
    ):
        """Test listing clients for assignment with multiple clients"""
        assignment_id, clients = test_assignment_with_clients
        
        response = client.get(f"/api/teacher/assignments/{assignment_id}/clients")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Should be ordered by display_order
        assert data[0]["display_order"] == 1
        assert data[1]["display_order"] == 2
        
        # Should include client and rubric details
        assert "client" in data[0]
        assert "rubric" in data[0]
        assert data[0]["client"]["name"] == clients[0].name
        assert data[0]["is_active"] is True
    
    def test_list_assignment_clients_unauthorized(
        self,
        client,
        test_assignment_other_teacher,
        mock_teacher_auth
    ):
        """Test listing clients for another teacher's assignment fails"""
        response = client.get(
            f"/api/teacher/assignments/{test_assignment_other_teacher.id}/clients"
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_list_assignment_clients_not_found(self, client, mock_teacher_auth):
        """Test listing clients for non-existent assignment fails"""
        response = client.get("/api/teacher/assignments/nonexistent-id/clients")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_add_client_to_assignment_success(
        self,
        client,
        test_assignments,
        sample_client_profile,
        sample_rubric,
        mock_teacher_auth
    ):
        """Test successfully adding a client to an assignment"""
        assignment = test_assignments[0]
        
        client_data = {
            "client_id": sample_client_profile.id,
            "rubric_id": sample_rubric.id,
            "display_order": 1
        }
        
        response = client.post(
            f"/api/teacher/assignments/{assignment.id}/clients",
            json=client_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["client_id"] == client_data["client_id"]
        assert data["rubric_id"] == client_data["rubric_id"]
        assert data["display_order"] == client_data["display_order"]
        assert data["is_active"] is True
        assert "client" in data
        assert "rubric" in data
    
    def test_add_client_without_display_order(
        self,
        client,
        test_assignments,
        sample_client_profile,
        sample_rubric,
        mock_teacher_auth
    ):
        """Test adding client without specifying display order"""
        assignment = test_assignments[0]
        
        client_data = {
            "client_id": sample_client_profile.id,
            "rubric_id": sample_rubric.id
        }
        
        response = client.post(
            f"/api/teacher/assignments/{assignment.id}/clients",
            json=client_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["client_id"] == client_data["client_id"]
        assert data["rubric_id"] == client_data["rubric_id"]
        assert "display_order" in data  # Should have default value
    
    def test_add_duplicate_client_already_active(
        self,
        client,
        test_assignment_with_clients,
        sample_rubric,
        mock_teacher_auth
    ):
        """Test adding a client that's already active returns existing"""
        assignment_id, clients = test_assignment_with_clients
        existing_client = clients[0]
        
        client_data = {
            "client_id": existing_client.id,
            "rubric_id": sample_rubric.id,  # Use a valid rubric that belongs to the teacher
            "display_order": 10
        }
        
        response = client.post(
            f"/api/teacher/assignments/{assignment_id}/clients",
            json=client_data
        )
        
        # Should return existing relationship, not create new
        assert response.status_code == 201
        data = response.json()
        assert data["client_id"] == existing_client.id
        # Original values should be preserved
        assert data["display_order"] == 1  # Original display order
    
    def test_add_client_reactivate_soft_deleted(
        self,
        client,
        test_assignment_with_inactive_client,
        sample_rubric,
        mock_teacher_auth
    ):
        """Test adding a soft-deleted client reactivates it"""
        assignment_id, inactive_client = test_assignment_with_inactive_client
        
        client_data = {
            "client_id": inactive_client.id,
            "rubric_id": sample_rubric.id,
            "display_order": 5
        }
        
        response = client.post(
            f"/api/teacher/assignments/{assignment_id}/clients",
            json=client_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["client_id"] == inactive_client.id
        assert data["rubric_id"] == sample_rubric.id
        assert data["display_order"] == 5
        assert data["is_active"] is True  # Reactivated
    
    def test_add_client_unauthorized_assignment(
        self,
        client,
        test_assignment_other_teacher,
        sample_client_profile,
        sample_rubric,
        mock_teacher_auth
    ):
        """Test adding client to another teacher's assignment fails"""
        client_data = {
            "client_id": sample_client_profile.id,
            "rubric_id": sample_rubric.id
        }
        
        response = client.post(
            f"/api/teacher/assignments/{test_assignment_other_teacher.id}/clients",
            json=client_data
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_add_client_not_owned_by_teacher(
        self,
        client,
        test_assignments,
        test_client_other_teacher,
        sample_rubric,
        mock_teacher_auth
    ):
        """Test adding another teacher's client fails"""
        assignment = test_assignments[0]
        
        client_data = {
            "client_id": test_client_other_teacher.id,
            "rubric_id": sample_rubric.id
        }
        
        response = client.post(
            f"/api/teacher/assignments/{assignment.id}/clients",
            json=client_data
        )
        
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()
    
    def test_add_client_rubric_not_owned_by_teacher(
        self,
        client,
        test_assignments,
        sample_client_profile,
        test_rubric_other_teacher,
        mock_teacher_auth
    ):
        """Test adding client with another teacher's rubric fails"""
        assignment = test_assignments[0]
        
        client_data = {
            "client_id": sample_client_profile.id,
            "rubric_id": test_rubric_other_teacher.id
        }
        
        response = client.post(
            f"/api/teacher/assignments/{assignment.id}/clients",
            json=client_data
        )
        
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()
    
    def test_add_client_assignment_not_found(self, client, mock_teacher_auth):
        """Test adding client to non-existent assignment fails"""
        client_data = {
            "client_id": "some-client-id",
            "rubric_id": "some-rubric-id"
        }
        
        response = client.post(
            "/api/teacher/assignments/nonexistent-id/clients",
            json=client_data
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_assignment_client_success(
        self,
        client,
        test_assignment_with_clients,
        sample_rubric,
        mock_teacher_auth
    ):
        """Test successfully updating the rubric for an assignment client"""
        assignment_id, clients = test_assignment_with_clients
        client_to_update = clients[0]
        
        update_data = {"rubric_id": sample_rubric.id}
        
        response = client.put(
            f"/api/teacher/assignments/{assignment_id}/clients/{client_to_update.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["client_id"] == client_to_update.id
        assert data["rubric_id"] == sample_rubric.id
        assert data["is_active"] is True
        assert "rubric" in data
        assert data["rubric"]["id"] == sample_rubric.id
    
    def test_update_assignment_client_missing_rubric_id(
        self,
        client,
        test_assignment_with_clients,
        mock_teacher_auth
    ):
        """Test updating without rubric_id fails"""
        assignment_id, clients = test_assignment_with_clients
        client_to_update = clients[0]
        
        response = client.put(
            f"/api/teacher/assignments/{assignment_id}/clients/{client_to_update.id}",
            json={"wrong_field": "value"}
        )
        
        assert response.status_code == 400
        assert "rubric_id" in response.json()["detail"]
    
    def test_update_assignment_client_unauthorized(
        self,
        client,
        test_assignment_other_teacher,
        mock_teacher_auth
    ):
        """Test updating client for another teacher's assignment fails"""
        update_data = {"rubric_id": "some-rubric-id"}
        
        response = client.put(
            f"/api/teacher/assignments/{test_assignment_other_teacher.id}/clients/some-client-id",
            json=update_data
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_update_assignment_client_not_found(
        self,
        client,
        test_assignments,
        sample_rubric,
        mock_teacher_auth
    ):
        """Test updating non-existent assignment-client relationship fails"""
        assignment = test_assignments[0]
        update_data = {"rubric_id": sample_rubric.id}
        
        response = client.put(
            f"/api/teacher/assignments/{assignment.id}/clients/nonexistent-client-id",
            json=update_data
        )
        
        assert response.status_code == 404
        assert "no active assignment" in response.json()["detail"].lower()
    
    def test_update_assignment_client_inactive(
        self,
        client,
        test_assignment_with_inactive_client,
        sample_rubric,
        mock_teacher_auth
    ):
        """Test updating inactive assignment-client relationship fails"""
        assignment_id, inactive_client = test_assignment_with_inactive_client
        update_data = {"rubric_id": sample_rubric.id}
        
        response = client.put(
            f"/api/teacher/assignments/{assignment_id}/clients/{inactive_client.id}",
            json=update_data
        )
        
        assert response.status_code == 404
        assert "no active assignment" in response.json()["detail"].lower()
    
    def test_update_assignment_client_rubric_not_owned(
        self,
        client,
        test_assignment_with_clients,
        test_rubric_other_teacher,
        mock_teacher_auth
    ):
        """Test updating with another teacher's rubric fails"""
        assignment_id, clients = test_assignment_with_clients
        client_to_update = clients[0]
        
        update_data = {"rubric_id": test_rubric_other_teacher.id}
        
        response = client.put(
            f"/api/teacher/assignments/{assignment_id}/clients/{client_to_update.id}",
            json=update_data
        )
        
        assert response.status_code == 404
        assert "no active assignment" in response.json()["detail"].lower()
    
    def test_remove_client_from_assignment_success(
        self,
        client,
        test_assignment_with_clients,
        db_session,
        mock_teacher_auth
    ):
        """Test successfully removing a client from an assignment"""
        assignment_id, clients = test_assignment_with_clients
        client_to_remove = clients[0]
        
        response = client.delete(
            f"/api/teacher/assignments/{assignment_id}/clients/{client_to_remove.id}"
        )
        
        assert response.status_code == 204
        
        # Verify it's soft deleted
        from backend.models.assignment import AssignmentClientDB
        db_client = db_session.query(AssignmentClientDB).filter(
            AssignmentClientDB.assignment_id == assignment_id,
            AssignmentClientDB.client_id == client_to_remove.id
        ).first()
        assert db_client is not None
        assert db_client.is_active is False
    
    def test_remove_client_unauthorized(
        self,
        client,
        test_assignment_other_teacher,
        mock_teacher_auth
    ):
        """Test removing client from another teacher's assignment fails"""
        response = client.delete(
            f"/api/teacher/assignments/{test_assignment_other_teacher.id}/clients/some-client-id"
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_remove_client_not_found(
        self,
        client,
        test_assignments,
        mock_teacher_auth
    ):
        """Test removing non-existent assignment-client relationship fails"""
        assignment = test_assignments[0]
        
        response = client.delete(
            f"/api/teacher/assignments/{assignment.id}/clients/nonexistent-client-id"
        )
        
        assert response.status_code == 404
        assert "no active assignment" in response.json()["detail"].lower()
    
    def test_remove_already_inactive_client(
        self,
        client,
        test_assignment_with_inactive_client,
        mock_teacher_auth
    ):
        """Test removing already inactive client fails"""
        assignment_id, inactive_client = test_assignment_with_inactive_client
        
        response = client.delete(
            f"/api/teacher/assignments/{assignment_id}/clients/{inactive_client.id}"
        )
        
        assert response.status_code == 404
        assert "no active assignment" in response.json()["detail"].lower()
    
    def test_bulk_add_clients_success(
        self,
        client,
        test_assignments,
        test_multiple_clients,
        test_multiple_rubrics,
        mock_teacher_auth
    ):
        """Test successfully adding multiple clients in bulk"""
        assignment = test_assignments[0]
        clients = test_multiple_clients[:3]
        rubrics = test_multiple_rubrics[:3]
        
        clients_data = [
            {
                "client_id": clients[0].id,
                "rubric_id": rubrics[0].id,
                "display_order": 1
            },
            {
                "client_id": clients[1].id,
                "rubric_id": rubrics[1].id,
                "display_order": 2
            },
            {
                "client_id": clients[2].id,
                "rubric_id": rubrics[2].id,
                "display_order": 3
            }
        ]
        
        response = client.post(
            f"/api/teacher/assignments/{assignment.id}/clients/bulk",
            json=clients_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "failed" in data
        assert len(data["success"]) == 3
        assert len(data["failed"]) == 0
        assert set(data["success"]) == {c.id for c in clients}
    
    def test_bulk_add_clients_partial_success(
        self,
        client,
        test_assignments,
        sample_client_profile,
        test_client_other_teacher,
        sample_rubric,
        mock_teacher_auth
    ):
        """Test bulk add with some valid and some invalid clients"""
        assignment = test_assignments[0]
        
        clients_data = [
            {
                "client_id": sample_client_profile.id,  # Valid
                "rubric_id": sample_rubric.id
            },
            {
                "client_id": test_client_other_teacher.id,  # Invalid - wrong teacher
                "rubric_id": sample_rubric.id
            },
            {
                "client_id": "nonexistent-client-id",  # Invalid - doesn't exist
                "rubric_id": sample_rubric.id
            }
        ]
        
        response = client.post(
            f"/api/teacher/assignments/{assignment.id}/clients/bulk",
            json=clients_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["success"]) == 1
        assert len(data["failed"]) == 2
        assert sample_client_profile.id in data["success"]
        assert test_client_other_teacher.id in data["failed"]
        assert "nonexistent-client-id" in data["failed"]
    
    def test_bulk_add_clients_empty_list(
        self,
        client,
        test_assignments,
        mock_teacher_auth
    ):
        """Test bulk add with empty list fails"""
        assignment = test_assignments[0]
        
        response = client.post(
            f"/api/teacher/assignments/{assignment.id}/clients/bulk",
            json=[]
        )
        
        assert response.status_code == 400
        assert "at least one client" in response.json()["detail"].lower()
    
    def test_bulk_add_clients_unauthorized(
        self,
        client,
        test_assignment_other_teacher,
        sample_client_profile,
        sample_rubric,
        mock_teacher_auth
    ):
        """Test bulk add to another teacher's assignment fails"""
        clients_data = [
            {
                "client_id": sample_client_profile.id,
                "rubric_id": sample_rubric.id
            }
        ]
        
        response = client.post(
            f"/api/teacher/assignments/{test_assignment_other_teacher.id}/clients/bulk",
            json=clients_data
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_bulk_add_clients_assignment_not_found(
        self,
        client,
        mock_teacher_auth
    ):
        """Test bulk add to non-existent assignment fails"""
        clients_data = [
            {
                "client_id": "some-client-id",
                "rubric_id": "some-rubric-id"
            }
        ]
        
        response = client.post(
            "/api/teacher/assignments/nonexistent-id/clients/bulk",
            json=clients_data
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_assignment_client_workflow(
        self,
        client,
        test_assignments,
        sample_client_profile,
        sample_rubric,
        test_multiple_rubrics,
        db_session,
        mock_teacher_auth
    ):
        """Test complete workflow: add, update, remove, re-add"""
        assignment = test_assignments[0]
        new_rubric = test_multiple_rubrics[0]
        
        # 1. Add client to assignment
        add_data = {
            "client_id": sample_client_profile.id,
            "rubric_id": sample_rubric.id,
            "display_order": 1
        }
        add_response = client.post(
            f"/api/teacher/assignments/{assignment.id}/clients",
            json=add_data
        )
        assert add_response.status_code == 201
        
        # 2. List clients - should have one
        list_response = client.get(f"/api/teacher/assignments/{assignment.id}/clients")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
        
        # 3. Update the rubric
        update_response = client.put(
            f"/api/teacher/assignments/{assignment.id}/clients/{sample_client_profile.id}",
            json={"rubric_id": new_rubric.id}
        )
        assert update_response.status_code == 200
        assert update_response.json()["rubric_id"] == new_rubric.id
        
        # 4. Remove the client
        remove_response = client.delete(
            f"/api/teacher/assignments/{assignment.id}/clients/{sample_client_profile.id}"
        )
        assert remove_response.status_code == 204
        
        # 5. List clients - should still show but inactive
        list_response = client.get(f"/api/teacher/assignments/{assignment.id}/clients")
        assert list_response.status_code == 200
        data = list_response.json()
        assert len(data) == 1
        assert data[0]["is_active"] is False
        
        # 6. Re-add the client - should reactivate
        readd_response = client.post(
            f"/api/teacher/assignments/{assignment.id}/clients",
            json=add_data
        )
        assert readd_response.status_code == 201
        assert readd_response.json()["is_active"] is True
