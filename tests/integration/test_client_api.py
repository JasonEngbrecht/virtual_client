"""
Integration tests for Client Profile API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app import app
from backend.models.client_profile import ClientProfileDB, ClientProfileCreate
from backend.services.client_service import client_service


# Create test client
client = TestClient(app)


class TestClientAPI:
    """Test suite for client profile API endpoints"""
    
    def test_list_clients_empty(self, db_session):
        """Test listing clients when none exist"""
        response = client.get("/api/teacher/clients")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_client_success(self, db_session):
        """Test creating a new client with all fields"""
        client_data = {
            "name": "Jane Doe",
            "age": 35,
            "race": "Hispanic",
            "gender": "Female",
            "socioeconomic_status": "Low income",
            "issues": ["housing_insecurity", "mental_health"],
            "background_story": "Recently lost job and facing eviction",
            "personality_traits": ["anxious", "cooperative"],
            "communication_style": "indirect"
        }
        
        response = client.post("/api/teacher/clients", json=client_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == "Jane Doe"
        assert data["age"] == 35
        assert data["race"] == "Hispanic"
        assert data["gender"] == "Female"
        assert data["socioeconomic_status"] == "Low income"
        assert set(data["issues"]) == {"housing_insecurity", "mental_health"}
        assert data["background_story"] == "Recently lost job and facing eviction"
        assert set(data["personality_traits"]) == {"anxious", "cooperative"}
        assert data["communication_style"] == "indirect"
        assert data["created_by"] == "teacher-123"
        assert "id" in data
        assert "created_at" in data
    
    def test_create_client_minimal(self, db_session):
        """Test creating a client with only required fields"""
        client_data = {
            "name": "John Smith",
            "age": 25
        }
        
        response = client.post("/api/teacher/clients", json=client_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == "John Smith"
        assert data["age"] == 25
        assert data["issues"] == []
        assert data["personality_traits"] == []
        assert data["race"] is None
        assert data["gender"] is None
    
    def test_create_client_invalid_age(self, db_session):
        """Test creating a client with invalid age"""
        # Test age too low
        client_data = {
            "name": "Test Client",
            "age": 0
        }
        response = client.post("/api/teacher/clients", json=client_data)
        assert response.status_code == 422
        
        # Test age too high
        client_data = {
            "name": "Test Client",
            "age": 150
        }
        response = client.post("/api/teacher/clients", json=client_data)
        assert response.status_code == 422
    
    def test_create_client_invalid_name(self, db_session):
        """Test creating a client with invalid name"""
        # Test empty name
        client_data = {
            "name": "",
            "age": 30
        }
        response = client.post("/api/teacher/clients", json=client_data)
        assert response.status_code == 422
        
        # Test missing name
        client_data = {
            "age": 30
        }
        response = client.post("/api/teacher/clients", json=client_data)
        assert response.status_code == 422
    
    def test_get_client_success(self, db_session):
        """Test retrieving a specific client"""
        # First create a client
        client_data = {
            "name": "Test Client",
            "age": 40,
            "issues": ["unemployment"]
        }
        create_response = client.post("/api/teacher/clients", json=client_data)
        assert create_response.status_code == 201
        client_id = create_response.json()["id"]
        
        # Now retrieve it
        response = client.get(f"/api/teacher/clients/{client_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == client_id
        assert data["name"] == "Test Client"
        assert data["age"] == 40
        assert data["issues"] == ["unemployment"]
    
    def test_get_client_not_found(self, db_session):
        """Test retrieving a non-existent client"""
        response = client.get("/api/teacher/clients/non-existent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_client_wrong_teacher(self, db_session):
        """Test retrieving a client belonging to another teacher"""
        # Create a client directly in the database with a different teacher
        client_data = ClientProfileCreate(
            name="Other Teacher's Client",
            age=30
        )
        profile = client_service.create_client_for_teacher(
            db_session,
            client_data,
            "other-teacher-456"
        )
        db_session.commit()
        client_id = profile.id
        
        # Try to access it as teacher-123
        response = client.get(f"/api/teacher/clients/{client_id}")
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_update_client_success(self, db_session):
        """Test updating a client with full data"""
        # First create a client
        client_data = {
            "name": "Original Name",
            "age": 30,
            "race": "White"
        }
        create_response = client.post("/api/teacher/clients", json=client_data)
        assert create_response.status_code == 201
        client_id = create_response.json()["id"]
        
        # Update it
        update_data = {
            "name": "Updated Name",
            "age": 31,
            "race": "Caucasian",
            "issues": ["financial_crisis", "mental_health"],
            "personality_traits": ["defensive", "anxious"]
        }
        response = client.put(f"/api/teacher/clients/{client_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["age"] == 31
        assert data["race"] == "Caucasian"
        assert set(data["issues"]) == {"financial_crisis", "mental_health"}
        assert set(data["personality_traits"]) == {"defensive", "anxious"}
    
    def test_update_client_partial(self, db_session):
        """Test partial update of a client"""
        # First create a client
        client_data = {
            "name": "Test Client",
            "age": 40,
            "race": "Asian",
            "gender": "Male",
            "issues": ["unemployment"]
        }
        create_response = client.post("/api/teacher/clients", json=client_data)
        assert create_response.status_code == 201
        client_id = create_response.json()["id"]
        
        # Partial update - only change age and add a trait
        update_data = {
            "age": 41,
            "personality_traits": ["withdrawn"]
        }
        response = client.put(f"/api/teacher/clients/{client_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test Client"  # Unchanged
        assert data["age"] == 41  # Updated
        assert data["race"] == "Asian"  # Unchanged
        assert data["gender"] == "Male"  # Unchanged
        assert data["issues"] == ["unemployment"]  # Unchanged
        assert data["personality_traits"] == ["withdrawn"]  # Updated
    
    def test_update_client_not_found(self, db_session):
        """Test updating a non-existent client"""
        update_data = {"name": "New Name"}
        response = client.put("/api/teacher/clients/non-existent-id", json=update_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_client_wrong_teacher(self, db_session):
        """Test updating a client belonging to another teacher"""
        # Create a client for another teacher
        client_data = ClientProfileCreate(
            name="Other Teacher's Client",
            age=30
        )
        profile = client_service.create_client_for_teacher(
            db_session,
            client_data,
            "other-teacher-456"
        )
        db_session.commit()
        client_id = profile.id
        
        # Try to update it as teacher-123
        update_data = {"name": "Hacked Name"}
        response = client.put(f"/api/teacher/clients/{client_id}", json=update_data)
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_update_client_empty_data(self, db_session):
        """Test updating a client with empty data"""
        # First create a client
        client_data = {"name": "Test Client", "age": 30}
        create_response = client.post("/api/teacher/clients", json=client_data)
        assert create_response.status_code == 201
        client_id = create_response.json()["id"]
        
        # Try to update with empty data
        response = client.put(f"/api/teacher/clients/{client_id}", json={})
        assert response.status_code == 400
        assert "No valid fields" in response.json()["detail"]
    
    def test_update_client_invalid_age(self, db_session):
        """Test updating a client with invalid age"""
        # First create a client
        client_data = {"name": "Test Client", "age": 30}
        create_response = client.post("/api/teacher/clients", json=client_data)
        assert create_response.status_code == 201
        client_id = create_response.json()["id"]
        
        # Try to update with invalid age
        update_data = {"age": 200}
        response = client.put(f"/api/teacher/clients/{client_id}", json=update_data)
        assert response.status_code == 422
    
    def test_delete_client_success(self, db_session):
        """Test deleting a client"""
        # First create a client
        client_data = {"name": "To Be Deleted", "age": 25}
        create_response = client.post("/api/teacher/clients", json=client_data)
        assert create_response.status_code == 201
        client_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/api/teacher/clients/{client_id}")
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = client.get(f"/api/teacher/clients/{client_id}")
        assert get_response.status_code == 404
    
    def test_delete_client_not_found(self, db_session):
        """Test deleting a non-existent client"""
        response = client.delete("/api/teacher/clients/non-existent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_delete_client_wrong_teacher(self, db_session):
        """Test deleting a client belonging to another teacher"""
        # Create a client for another teacher
        client_data = ClientProfileCreate(
            name="Other Teacher's Client",
            age=30
        )
        profile = client_service.create_client_for_teacher(
            db_session,
            client_data,
            "other-teacher-456"
        )
        db_session.commit()
        client_id = profile.id
        
        # Try to delete it as teacher-123
        response = client.delete(f"/api/teacher/clients/{client_id}")
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    def test_list_clients_with_data(self, db_session):
        """Test listing multiple clients"""
        # Create several clients
        clients_data = [
            {"name": "Client 1", "age": 25, "issues": ["mental_health"]},
            {"name": "Client 2", "age": 30, "gender": "Female"},
            {"name": "Client 3", "age": 45, "race": "Black", "issues": ["housing_insecurity", "unemployment"]}
        ]
        
        created_ids = []
        for cdata in clients_data:
            response = client.post("/api/teacher/clients", json=cdata)
            assert response.status_code == 201
            created_ids.append(response.json()["id"])
        
        # List all clients
        response = client.get("/api/teacher/clients")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        
        # Verify all clients are present
        returned_ids = [c["id"] for c in data]
        assert set(returned_ids) == set(created_ids)
        
        # Verify client data
        client_names = [c["name"] for c in data]
        assert set(client_names) == {"Client 1", "Client 2", "Client 3"}
    
    def test_teacher_isolation(self, db_session):
        """Test that teachers can only see their own clients"""
        # Create a client for teacher-123 (default mock teacher)
        client_data = {"name": "My Client", "age": 35}
        response = client.post("/api/teacher/clients", json=client_data)
        assert response.status_code == 201
        
        # Create clients for another teacher directly
        for i in range(2):
            other_client_data = ClientProfileCreate(
                name=f"Other Teacher Client {i+1}",
                age=40 + i
            )
            client_service.create_client_for_teacher(
                db_session,
                other_client_data,
                "other-teacher-456"
            )
        db_session.commit()
        
        # List clients - should only see our own
        response = client.get("/api/teacher/clients")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "My Client"
        assert data[0]["created_by"] == "teacher-123"
    
    def test_complete_client_workflow(self, db_session):
        """Test complete workflow: create, update, list, delete"""
        # 1. Create a client
        client_data = {
            "name": "Workflow Test Client",
            "age": 28,
            "race": "White",
            "gender": "Non-binary",
            "issues": ["substance_abuse"],
            "personality_traits": ["defensive", "suspicious"]
        }
        create_response = client.post("/api/teacher/clients", json=client_data)
        assert create_response.status_code == 201
        client_id = create_response.json()["id"]
        
        # 2. Update the client
        update_data = {
            "age": 29,
            "issues": ["substance_abuse", "mental_health"],
            "background_story": "Recently completed rehab program"
        }
        update_response = client.put(f"/api/teacher/clients/{client_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["age"] == 29
        assert "mental_health" in update_response.json()["issues"]
        
        # 3. List clients to verify it's there
        list_response = client.get("/api/teacher/clients")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
        assert list_response.json()[0]["id"] == client_id
        
        # 4. Get specific client
        get_response = client.get(f"/api/teacher/clients/{client_id}")
        assert get_response.status_code == 200
        assert get_response.json()["background_story"] == "Recently completed rehab program"
        
        # 5. Delete the client
        delete_response = client.delete(f"/api/teacher/clients/{client_id}")
        assert delete_response.status_code == 204
        
        # 6. Verify it's gone
        final_list_response = client.get("/api/teacher/clients")
        assert final_list_response.status_code == 200
        assert final_list_response.json() == []
