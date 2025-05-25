"""
Simple enrollment API test that works with proper database setup
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

# Import what we need
from backend.app import app
from backend.services.database import Base, get_db
from backend.api.teacher_routes import get_current_teacher
from backend.models.course_section import CourseSectionDB, SectionEnrollmentDB

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_enrollment.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_teacher():
    return "teacher-123"

# Apply overrides
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_teacher] = override_get_current_teacher

# Create test client
client = TestClient(app)

def test_enrollment_workflow():
    """Test the complete enrollment workflow"""
    
    # 1. Create a section
    section_data = {
        "name": "Test Section",
        "description": "Test enrollment",
        "course_code": "TEST101",
        "term": "Spring 2025"
    }
    
    response = client.post("/api/teacher/sections", json=section_data)
    assert response.status_code == 201
    section = response.json()
    section_id = section["id"]
    print(f"✓ Created section: {section_id}")
    
    # 2. Get empty roster
    response = client.get(f"/api/teacher/sections/{section_id}/roster")
    assert response.status_code == 200
    roster = response.json()
    assert len(roster) == 0
    print("✓ Empty roster confirmed")
    
    # 3. Enroll a student
    enrollment_data = {
        "student_id": "student-test-001",
        "role": "student"
    }
    response = client.post(f"/api/teacher/sections/{section_id}/enroll", json=enrollment_data)
    assert response.status_code == 201
    enrollment = response.json()
    assert enrollment["student_id"] == "student-test-001"
    print("✓ Student enrolled")
    
    # 4. Get roster with student
    response = client.get(f"/api/teacher/sections/{section_id}/roster")
    assert response.status_code == 200
    roster = response.json()
    assert len(roster) == 1
    assert roster[0]["student_id"] == "student-test-001"
    print("✓ Student appears in roster")
    
    # 5. Unenroll student
    response = client.delete(f"/api/teacher/sections/{section_id}/enroll/student-test-001")
    assert response.status_code == 204
    print("✓ Student unenrolled")
    
    # 6. Verify empty roster again
    response = client.get(f"/api/teacher/sections/{section_id}/roster")
    assert response.status_code == 200
    roster = response.json()
    assert len(roster) == 0
    print("✓ Roster is empty again")
    
    # 7. Clean up
    response = client.delete(f"/api/teacher/sections/{section_id}")
    assert response.status_code == 204
    print("✓ Section deleted")
    
    print("\n✅ All enrollment tests passed!")

if __name__ == "__main__":
    try:
        test_enrollment_workflow()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Clean up test database
        import os
        if os.path.exists("test_enrollment.db"):
            os.remove("test_enrollment.db")
            print("\n🧹 Cleaned up test database")
