"""
Integration tests for Rubric API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app import app
from backend.services.database import Base, get_db
from backend.models.rubric import EvaluationRubricDB


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


def test_list_rubrics():
    """Test GET /api/teacher/rubrics endpoint"""
    # Initially, should return empty list
    response = client.get("/api/teacher/rubrics")
    assert response.status_code == 200
    assert response.json() == []


def test_create_rubric():
    """Test POST /api/teacher/rubrics endpoint"""
    # Create a valid rubric
    rubric_data = {
        "name": "Test Rubric",
        "description": "A test evaluation rubric",
        "criteria": [
            {
                "name": "Communication",
                "description": "Evaluates communication skills",
                "weight": 0.5,
                "evaluation_points": ["Clear speech", "Active listening"]
            },
            {
                "name": "Empathy",
                "description": "Evaluates empathy",
                "weight": 0.5,
                "evaluation_points": ["Shows understanding", "Validates feelings"]
            }
        ]
    }
    
    response = client.post("/api/teacher/rubrics", json=rubric_data)
    assert response.status_code == 201
    
    rubric = response.json()
    assert rubric["name"] == "Test Rubric"
    assert rubric["description"] == "A test evaluation rubric"
    assert len(rubric["criteria"]) == 2
    assert rubric["created_by"] == "teacher-123"  # Mock teacher ID
    assert "id" in rubric
    
    # Verify it appears in the list
    response = client.get("/api/teacher/rubrics")
    assert response.status_code == 200
    rubrics = response.json()
    assert len(rubrics) == 1
    assert rubrics[0]["id"] == rubric["id"]


def test_create_rubric_invalid_weights():
    """Test POST /api/teacher/rubrics with invalid weight sum"""
    # Create rubric with weights not summing to 1.0
    rubric_data = {
        "name": "Invalid Rubric",
        "description": "Weights don't sum to 1.0",
        "criteria": [
            {
                "name": "Criterion 1",
                "description": "First criterion",
                "weight": 0.3,
                "evaluation_points": ["Point 1"]
            },
            {
                "name": "Criterion 2",
                "description": "Second criterion",
                "weight": 0.5,  # Total = 0.8, not 1.0
                "evaluation_points": ["Point 2"]
            }
        ]
    }
    
    response = client.post("/api/teacher/rubrics", json=rubric_data)
    assert response.status_code == 422  # Validation error
    error = response.json()
    assert "detail" in error
    # Check that the error mentions weight validation
    assert any("weight" in str(item).lower() or "sum to 1.0" in str(item) 
               for item in error["detail"])


def test_create_rubric_empty_criteria():
    """Test POST /api/teacher/rubrics with empty criteria"""
    rubric_data = {
        "name": "Empty Criteria Rubric",
        "description": "No criteria",
        "criteria": []
    }
    
    response = client.post("/api/teacher/rubrics", json=rubric_data)
    assert response.status_code == 422  # Validation error
    error = response.json()
    assert "detail" in error


def test_create_rubric_missing_fields():
    """Test POST /api/teacher/rubrics with missing required fields"""
    # Missing name
    rubric_data = {
        "description": "Missing name",
        "criteria": [
            {
                "name": "Test",
                "description": "Test",
                "weight": 1.0,
                "evaluation_points": ["Point"]
            }
        ]
    }
    
    response = client.post("/api/teacher/rubrics", json=rubric_data)
    assert response.status_code == 422  # Validation error
    error = response.json()
    assert "detail" in error


def test_get_rubric():
    """Test GET /api/teacher/rubrics/{id} endpoint"""
    # First, create a rubric
    rubric_data = {
        "name": "Test Get Rubric",
        "description": "Testing the get endpoint",
        "criteria": [
            {
                "name": "Test Criterion",
                "description": "A test criterion",
                "weight": 1.0,
                "evaluation_points": ["Point 1", "Point 2"]
            }
        ]
    }
    
    create_response = client.post("/api/teacher/rubrics", json=rubric_data)
    assert create_response.status_code == 201
    created_rubric = create_response.json()
    rubric_id = created_rubric["id"]
    
    # Now get the rubric by ID
    get_response = client.get(f"/api/teacher/rubrics/{rubric_id}")
    assert get_response.status_code == 200
    
    retrieved_rubric = get_response.json()
    assert retrieved_rubric["id"] == rubric_id
    assert retrieved_rubric["name"] == "Test Get Rubric"
    assert retrieved_rubric["description"] == "Testing the get endpoint"
    assert len(retrieved_rubric["criteria"]) == 1
    assert retrieved_rubric["created_by"] == "teacher-123"


def test_get_rubric_not_found():
    """Test GET /api/teacher/rubrics/{id} with non-existent ID"""
    non_existent_id = "non-existent-rubric-id"
    
    response = client.get(f"/api/teacher/rubrics/{non_existent_id}")
    assert response.status_code == 404
    
    error = response.json()
    assert "detail" in error
    assert non_existent_id in error["detail"]
    assert "not found" in error["detail"].lower()


def test_get_rubric_wrong_teacher():
    """Test GET /api/teacher/rubrics/{id} for another teacher's rubric"""
    # Create a rubric with teacher-123
    rubric_data = {
        "name": "Another Teacher's Rubric",
        "description": "This belongs to teacher-123",
        "criteria": [
            {
                "name": "Criterion",
                "description": "Test",
                "weight": 1.0,
                "evaluation_points": ["Point"]
            }
        ]
    }
    
    create_response = client.post("/api/teacher/rubrics", json=rubric_data)
    assert create_response.status_code == 201
    rubric_id = create_response.json()["id"]
    
    # Manually update the rubric in the database to belong to a different teacher
    # This simulates trying to access another teacher's rubric
    from backend.models.rubric import EvaluationRubricDB
    db = next(override_get_db())
    rubric = db.query(EvaluationRubricDB).filter(EvaluationRubricDB.id == rubric_id).first()
    if rubric:
        rubric.created_by = "teacher-456"  # Different teacher
        db.commit()
    db.close()
    
    # Now try to get the rubric as teacher-123
    response = client.get(f"/api/teacher/rubrics/{rubric_id}")
    assert response.status_code == 403
    
    error = response.json()
    assert "detail" in error
    assert "permission" in error["detail"].lower()


def test_update_rubric_partial():
    """Test PUT /api/teacher/rubrics/{id} with partial update"""
    # First, create a rubric
    rubric_data = {
        "name": "Original Rubric Name",
        "description": "Original description",
        "criteria": [
            {
                "name": "Criterion 1",
                "description": "First criterion",
                "weight": 0.6,
                "evaluation_points": ["Point 1"]
            },
            {
                "name": "Criterion 2",
                "description": "Second criterion",
                "weight": 0.4,
                "evaluation_points": ["Point 2"]
            }
        ]
    }
    
    create_response = client.post("/api/teacher/rubrics", json=rubric_data)
    assert create_response.status_code == 201
    rubric_id = create_response.json()["id"]
    
    # Update only the name
    update_data = {
        "name": "Updated Rubric Name"
    }
    
    update_response = client.put(f"/api/teacher/rubrics/{rubric_id}", json=update_data)
    assert update_response.status_code == 200
    
    updated_rubric = update_response.json()
    assert updated_rubric["id"] == rubric_id
    assert updated_rubric["name"] == "Updated Rubric Name"
    assert updated_rubric["description"] == "Original description"  # Unchanged
    assert len(updated_rubric["criteria"]) == 2  # Unchanged


def test_update_rubric_criteria():
    """Test PUT /api/teacher/rubrics/{id} updating criteria"""
    # Create a rubric
    rubric_data = {
        "name": "Rubric to Update",
        "description": "Will update criteria",
        "criteria": [
            {
                "name": "Old Criterion",
                "description": "Will be replaced",
                "weight": 1.0,
                "evaluation_points": ["Old point"]
            }
        ]
    }
    
    create_response = client.post("/api/teacher/rubrics", json=rubric_data)
    assert create_response.status_code == 201
    rubric_id = create_response.json()["id"]
    
    # Update with new criteria
    update_data = {
        "criteria": [
            {
                "name": "New Criterion 1",
                "description": "First new criterion",
                "weight": 0.7,
                "evaluation_points": ["New point 1", "New point 2"]
            },
            {
                "name": "New Criterion 2",
                "description": "Second new criterion",
                "weight": 0.3,
                "evaluation_points": ["Another point"]
            }
        ]
    }
    
    update_response = client.put(f"/api/teacher/rubrics/{rubric_id}", json=update_data)
    assert update_response.status_code == 200
    
    updated_rubric = update_response.json()
    assert len(updated_rubric["criteria"]) == 2
    assert updated_rubric["criteria"][0]["name"] == "New Criterion 1"
    assert updated_rubric["criteria"][0]["weight"] == 0.7


def test_update_rubric_invalid_weights():
    """Test PUT /api/teacher/rubrics/{id} with invalid criteria weights"""
    # Create a rubric
    rubric_data = {
        "name": "Test Rubric",
        "description": "Test",
        "criteria": [{"name": "Test", "description": "Test", "weight": 1.0, "evaluation_points": ["Test"]}]
    }
    
    create_response = client.post("/api/teacher/rubrics", json=rubric_data)
    assert create_response.status_code == 201
    rubric_id = create_response.json()["id"]
    
    # Try to update with invalid weights
    update_data = {
        "criteria": [
            {
                "name": "Criterion 1",
                "description": "First",
                "weight": 0.4,
                "evaluation_points": ["Point"]
            },
            {
                "name": "Criterion 2",
                "description": "Second",
                "weight": 0.4,  # Total = 0.8, not 1.0
                "evaluation_points": ["Point"]
            }
        ]
    }
    
    update_response = client.put(f"/api/teacher/rubrics/{rubric_id}", json=update_data)
    assert update_response.status_code == 422  # Validation error


def test_update_rubric_not_found():
    """Test PUT /api/teacher/rubrics/{id} with non-existent ID"""
    update_data = {"name": "New Name"}
    
    response = client.put("/api/teacher/rubrics/non-existent-id", json=update_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_rubric_wrong_teacher():
    """Test PUT /api/teacher/rubrics/{id} for another teacher's rubric"""
    # Create a rubric
    rubric_data = {
        "name": "Test Rubric",
        "description": "Test",
        "criteria": [{"name": "Test", "description": "Test", "weight": 1.0, "evaluation_points": ["Test"]}]
    }
    
    create_response = client.post("/api/teacher/rubrics", json=rubric_data)
    assert create_response.status_code == 201
    rubric_id = create_response.json()["id"]
    
    # Change the rubric's owner
    from backend.models.rubric import EvaluationRubricDB
    db = next(override_get_db())
    rubric = db.query(EvaluationRubricDB).filter(EvaluationRubricDB.id == rubric_id).first()
    if rubric:
        rubric.created_by = "teacher-999"
        db.commit()
    db.close()
    
    # Try to update as teacher-123
    update_data = {"name": "Should Not Work"}
    response = client.put(f"/api/teacher/rubrics/{rubric_id}", json=update_data)
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


def test_update_rubric_empty_data():
    """Test PUT /api/teacher/rubrics/{id} with empty update data"""
    # Create a rubric
    rubric_data = {
        "name": "Test Rubric",
        "description": "Test",
        "criteria": [{"name": "Test", "description": "Test", "weight": 1.0, "evaluation_points": ["Test"]}]
    }
    
    create_response = client.post("/api/teacher/rubrics", json=rubric_data)
    assert create_response.status_code == 201
    rubric_id = create_response.json()["id"]
    
    # Send empty update
    response = client.put(f"/api/teacher/rubrics/{rubric_id}", json={})
    assert response.status_code == 400
    assert "No valid fields" in response.json()["detail"]


def test_delete_rubric():
    """Test DELETE /api/teacher/rubrics/{id} endpoint"""
    # First, create a rubric to delete
    rubric_data = {
        "name": "Rubric to Delete",
        "description": "This will be deleted",
        "criteria": [
            {
                "name": "Test Criterion",
                "description": "Test",
                "weight": 1.0,
                "evaluation_points": ["Test point"]
            }
        ]
    }
    
    create_response = client.post("/api/teacher/rubrics", json=rubric_data)
    assert create_response.status_code == 201
    rubric_id = create_response.json()["id"]
    
    # Delete the rubric
    delete_response = client.delete(f"/api/teacher/rubrics/{rubric_id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b''  # No content
    
    # Verify it's deleted by trying to get it
    get_response = client.get(f"/api/teacher/rubrics/{rubric_id}")
    assert get_response.status_code == 404
    assert "not found" in get_response.json()["detail"].lower()


def test_delete_rubric_not_found():
    """Test DELETE /api/teacher/rubrics/{id} with non-existent ID"""
    response = client.delete("/api/teacher/rubrics/non-existent-rubric-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_rubric_wrong_teacher():
    """Test DELETE /api/teacher/rubrics/{id} for another teacher's rubric"""
    # Create a rubric
    rubric_data = {
        "name": "Another Teacher's Rubric",
        "description": "Belongs to another teacher",
        "criteria": [{"name": "Test", "description": "Test", "weight": 1.0, "evaluation_points": ["Test"]}]
    }
    
    create_response = client.post("/api/teacher/rubrics", json=rubric_data)
    assert create_response.status_code == 201
    rubric_id = create_response.json()["id"]
    
    # Change the rubric's owner
    from backend.models.rubric import EvaluationRubricDB
    db = next(override_get_db())
    rubric = db.query(EvaluationRubricDB).filter(EvaluationRubricDB.id == rubric_id).first()
    if rubric:
        rubric.created_by = "teacher-456"
        db.commit()
    db.close()
    
    # Try to delete as teacher-123
    response = client.delete(f"/api/teacher/rubrics/{rubric_id}")
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


def test_delete_rubric_verify_list():
    """Test that deleted rubric is removed from list"""
    # Create two rubrics
    rubric1_data = {
        "name": "Rubric 1",
        "description": "First rubric",
        "criteria": [{"name": "Test", "description": "Test", "weight": 1.0, "evaluation_points": ["Test"]}]
    }
    rubric2_data = {
        "name": "Rubric 2",
        "description": "Second rubric",
        "criteria": [{"name": "Test", "description": "Test", "weight": 1.0, "evaluation_points": ["Test"]}]
    }
    
    response1 = client.post("/api/teacher/rubrics", json=rubric1_data)
    assert response1.status_code == 201
    rubric1_id = response1.json()["id"]
    
    response2 = client.post("/api/teacher/rubrics", json=rubric2_data)
    assert response2.status_code == 201
    rubric2_id = response2.json()["id"]
    
    # Get initial list
    list_response = client.get("/api/teacher/rubrics")
    initial_rubrics = list_response.json()
    initial_ids = [r["id"] for r in initial_rubrics]
    assert rubric1_id in initial_ids
    assert rubric2_id in initial_ids
    
    # Delete rubric1
    delete_response = client.delete(f"/api/teacher/rubrics/{rubric1_id}")
    assert delete_response.status_code == 204
    
    # Verify only rubric2 remains in list
    list_response = client.get("/api/teacher/rubrics")
    remaining_rubrics = list_response.json()
    remaining_ids = [r["id"] for r in remaining_rubrics]
    assert rubric1_id not in remaining_ids
    assert rubric2_id in remaining_ids
