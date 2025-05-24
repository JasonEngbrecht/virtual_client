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
    
    # TODO: After implementing create endpoint, add test data and verify list returns it
