"""
Integration tests for Course Section API endpoints.

Tests the complete request/response cycle for section endpoints,
including authentication, validation, and error handling.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app import app
from backend.models.course_section import CourseSectionDB


# Create test client
client = TestClient(app)


# Test data
VALID_SECTION_DATA = {
    "name": "Social Work Practice I - Fall 2025",
    "description": "Introduction to social work practice with individuals and families",
    "course_code": "SW101",
    "term": "Fall 2025",
    "is_active": True,
    "settings": {
        "allow_late_submissions": True,
        "max_attempts_per_assignment": 3
    }
}


# ==================== LIST SECTIONS TESTS ====================

def test_list_sections_empty(db_session):
    """Test listing sections when none exist."""
    response = client.get("/api/teacher/sections")
    assert response.status_code == 200
    assert response.json() == []


def test_list_sections_with_data(db_session):
    """Test listing sections for the authenticated teacher."""
    # Create a section first
    response1 = client.post("/api/teacher/sections", json=VALID_SECTION_DATA)
    assert response1.status_code == 201
    
    # Create another section
    section2_data = {
        **VALID_SECTION_DATA,
        "name": "Social Work Practice II - Spring 2025",
        "course_code": "SW102",
        "term": "Spring 2025"
    }
    response2 = client.post("/api/teacher/sections", json=section2_data)
    assert response2.status_code == 201
    
    # List all sections
    response = client.get("/api/teacher/sections")
    assert response.status_code == 200
    sections = response.json()
    assert len(sections) == 2
    
    # Verify both sections are returned
    section_names = [s["name"] for s in sections]
    assert "Social Work Practice I - Fall 2025" in section_names
    assert "Social Work Practice II - Spring 2025" in section_names
    
    # Verify teacher_id is set correctly
    for section in sections:
        assert section["teacher_id"] == "teacher-123"  # Mock teacher ID


# ==================== CREATE SECTION TESTS ====================

def test_create_section_success(db_session):
    """Test creating a new section with valid data."""
    response = client.post("/api/teacher/sections", json=VALID_SECTION_DATA)
    
    assert response.status_code == 201
    section = response.json()
    
    # Verify all fields
    assert section["name"] == VALID_SECTION_DATA["name"]
    assert section["description"] == VALID_SECTION_DATA["description"]
    assert section["course_code"] == VALID_SECTION_DATA["course_code"]
    assert section["term"] == VALID_SECTION_DATA["term"]
    assert section["is_active"] == VALID_SECTION_DATA["is_active"]
    assert section["settings"] == VALID_SECTION_DATA["settings"]
    assert section["teacher_id"] == "teacher-123"
    assert "id" in section
    assert "created_at" in section


def test_create_section_minimal(db_session):
    """Test creating a section with only required fields."""
    minimal_data = {
        "name": "Minimal Section"
    }
    response = client.post("/api/teacher/sections", json=minimal_data)
    
    assert response.status_code == 201
    section = response.json()
    
    # Verify required field
    assert section["name"] == "Minimal Section"
    # Verify defaults
    assert section["description"] is None
    assert section["course_code"] is None
    assert section["term"] is None
    assert section["is_active"] is True
    assert section["settings"] == {}


def test_create_section_invalid_data(db_session):
    """Test creating a section with invalid data."""
    # Missing required field
    invalid_data = {
        "description": "Missing name field"
    }
    response = client.post("/api/teacher/sections", json=invalid_data)
    
    assert response.status_code == 422
    error = response.json()
    assert "name" in str(error["detail"])


def test_create_section_empty_name(db_session):
    """Test creating a section with empty name."""
    invalid_data = {
        "name": ""
    }
    response = client.post("/api/teacher/sections", json=invalid_data)
    
    assert response.status_code == 422
    error = response.json()
    assert "name" in str(error["detail"])


# ==================== GET SECTION TESTS ====================

def test_get_section_success(db_session):
    """Test retrieving a specific section."""
    # Create a section first
    create_response = client.post("/api/teacher/sections", json=VALID_SECTION_DATA)
    assert create_response.status_code == 201
    section_id = create_response.json()["id"]
    
    # Get the section
    response = client.get(f"/api/teacher/sections/{section_id}")
    assert response.status_code == 200
    section = response.json()
    
    # Verify data
    assert section["id"] == section_id
    assert section["name"] == VALID_SECTION_DATA["name"]
    assert section["teacher_id"] == "teacher-123"


def test_get_section_not_found(db_session):
    """Test getting a non-existent section."""
    response = client.get("/api/teacher/sections/non-existent-id")
    
    assert response.status_code == 404
    error = response.json()
    assert "Section with ID 'non-existent-id' not found" in error["detail"]


def test_get_section_wrong_teacher(db_session):
    """Test getting a section that belongs to another teacher."""
    # Create a section with the mock teacher
    create_response = client.post("/api/teacher/sections", json=VALID_SECTION_DATA)
    assert create_response.status_code == 201
    section_id = create_response.json()["id"]
    
    # Manually update the teacher_id in the database
    section = db_session.query(CourseSectionDB).filter_by(id=section_id).first()
    section.teacher_id = "other-teacher-456"
    db_session.commit()
    
    # Try to get the section
    response = client.get(f"/api/teacher/sections/{section_id}")
    
    assert response.status_code == 403
    error = response.json()
    assert "You don't have permission to access this section" in error["detail"]


# ==================== UPDATE SECTION TESTS ====================

def test_update_section_success(db_session):
    """Test updating a section with valid data."""
    # Create a section first
    create_response = client.post("/api/teacher/sections", json=VALID_SECTION_DATA)
    assert create_response.status_code == 201
    section_id = create_response.json()["id"]
    
    # Update the section
    update_data = {
        "description": "Updated description for the course",
        "is_active": False,
        "settings": {
            "allow_late_submissions": False,
            "new_setting": "value"
        }
    }
    response = client.put(f"/api/teacher/sections/{section_id}", json=update_data)
    
    assert response.status_code == 200
    updated_section = response.json()
    
    # Verify updates
    assert updated_section["description"] == update_data["description"]
    assert updated_section["is_active"] == update_data["is_active"]
    assert updated_section["settings"] == update_data["settings"]
    # Verify unchanged fields
    assert updated_section["name"] == VALID_SECTION_DATA["name"]
    assert updated_section["course_code"] == VALID_SECTION_DATA["course_code"]


def test_update_section_partial(db_session):
    """Test partial update of a section."""
    # Create a section first
    create_response = client.post("/api/teacher/sections", json=VALID_SECTION_DATA)
    assert create_response.status_code == 201
    section_id = create_response.json()["id"]
    
    # Update only one field
    update_data = {
        "term": "Summer 2025"
    }
    response = client.put(f"/api/teacher/sections/{section_id}", json=update_data)
    
    assert response.status_code == 200
    updated_section = response.json()
    
    # Verify update
    assert updated_section["term"] == "Summer 2025"
    # Verify other fields unchanged
    assert updated_section["name"] == VALID_SECTION_DATA["name"]
    assert updated_section["description"] == VALID_SECTION_DATA["description"]


def test_update_section_not_found(db_session):
    """Test updating a non-existent section."""
    update_data = {"name": "Updated Name"}
    response = client.put("/api/teacher/sections/non-existent-id", json=update_data)
    
    assert response.status_code == 404
    error = response.json()
    assert "Section with ID 'non-existent-id' not found" in error["detail"]


def test_update_section_wrong_teacher(db_session):
    """Test updating a section that belongs to another teacher."""
    # Create a section
    create_response = client.post("/api/teacher/sections", json=VALID_SECTION_DATA)
    assert create_response.status_code == 201
    section_id = create_response.json()["id"]
    
    # Change the teacher_id
    section = db_session.query(CourseSectionDB).filter_by(id=section_id).first()
    section.teacher_id = "other-teacher-456"
    db_session.commit()
    
    # Try to update
    update_data = {"name": "Updated Name"}
    response = client.put(f"/api/teacher/sections/{section_id}", json=update_data)
    
    assert response.status_code == 403
    error = response.json()
    assert "You don't have permission to update this section" in error["detail"]


def test_update_section_empty_data(db_session):
    """Test updating a section with empty data."""
    # Create a section
    create_response = client.post("/api/teacher/sections", json=VALID_SECTION_DATA)
    assert create_response.status_code == 201
    section_id = create_response.json()["id"]
    
    # Try to update with empty data
    response = client.put(f"/api/teacher/sections/{section_id}", json={})
    
    assert response.status_code == 400
    error = response.json()
    assert "No valid fields provided for update" in error["detail"]


# ==================== DELETE SECTION TESTS ====================

def test_delete_section_success(db_session):
    """Test deleting a section."""
    # Create a section first
    create_response = client.post("/api/teacher/sections", json=VALID_SECTION_DATA)
    assert create_response.status_code == 201
    section_id = create_response.json()["id"]
    
    # Delete the section
    response = client.delete(f"/api/teacher/sections/{section_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/teacher/sections/{section_id}")
    assert get_response.status_code == 404


def test_delete_section_not_found(db_session):
    """Test deleting a non-existent section."""
    response = client.delete("/api/teacher/sections/non-existent-id")
    
    assert response.status_code == 404
    error = response.json()
    assert "Section with ID 'non-existent-id' not found" in error["detail"]


def test_delete_section_wrong_teacher(db_session):
    """Test deleting a section that belongs to another teacher."""
    # Create a section
    create_response = client.post("/api/teacher/sections", json=VALID_SECTION_DATA)
    assert create_response.status_code == 201
    section_id = create_response.json()["id"]
    
    # Change the teacher_id
    section = db_session.query(CourseSectionDB).filter_by(id=section_id).first()
    section.teacher_id = "other-teacher-456"
    db_session.commit()
    
    # Try to delete
    response = client.delete(f"/api/teacher/sections/{section_id}")
    
    assert response.status_code == 403
    error = response.json()
    assert "You don't have permission to delete this section" in error["detail"]


# ==================== WORKFLOW TESTS ====================

def test_complete_section_workflow(db_session):
    """Test a complete workflow: create, read, update, delete."""
    # Create
    create_response = client.post("/api/teacher/sections", json=VALID_SECTION_DATA)
    assert create_response.status_code == 201
    section_id = create_response.json()["id"]
    
    # Read
    get_response = client.get(f"/api/teacher/sections/{section_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == VALID_SECTION_DATA["name"]
    
    # Update
    update_data = {"name": "Updated Section Name"}
    update_response = client.put(f"/api/teacher/sections/{section_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Section Name"
    
    # List (should contain our section)
    list_response = client.get("/api/teacher/sections")
    assert list_response.status_code == 200
    sections = list_response.json()
    assert len(sections) == 1
    assert sections[0]["name"] == "Updated Section Name"
    
    # Delete
    delete_response = client.delete(f"/api/teacher/sections/{section_id}")
    assert delete_response.status_code == 204
    
    # Verify deleted
    verify_response = client.get(f"/api/teacher/sections/{section_id}")
    assert verify_response.status_code == 404
