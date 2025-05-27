"""
Integration tests for MVP Teacher Interface
"""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.models.client_profile import ClientProfileCreate, ClientProfileDB
from backend.services.client_service import client_service
from backend.models.auth import TeacherAuth
from mvp.utils import get_database_connection, get_mock_teacher


class TestTeacherInterfaceIntegration:
    """Integration tests for teacher interface with real database"""
    
    @pytest.fixture
    def db_session(self, db_session):
        """Use the standard test database session"""
        return db_session
    
    @pytest.fixture
    def teacher(self):
        """Get mock teacher for testing"""
        return get_mock_teacher()
    
    @pytest.fixture
    def sample_client_data(self):
        """Sample client data for testing"""
        return ClientProfileCreate(
            name="Integration Test Client",
            age=42,
            gender="Male",
            race="Asian",
            socioeconomic_status="Middle class",
            issues=["mental_health", "unemployment", "family_conflict"],
            background_story="Recently laid off software engineer struggling with depression",
            personality_traits=["withdrawn", "anxious", "logical", "pessimistic"],
            communication_style="brief"
        )
    
    def test_create_client_full_flow(self, db_session, teacher, sample_client_data):
        """Test creating a client through the service"""
        # Create client
        created_client = client_service.create_client_for_teacher(
            db_session, sample_client_data, teacher.teacher_id
        )
        
        # Verify client was created
        assert created_client.id is not None
        assert created_client.name == sample_client_data.name
        assert created_client.age == sample_client_data.age
        assert created_client.created_by == teacher.teacher_id
        assert len(created_client.issues) == 3
        assert len(created_client.personality_traits) == 4
        assert created_client.communication_style == "brief"
    
    def test_get_teacher_clients(self, db_session, teacher):
        """Test retrieving clients for a teacher"""
        # Create multiple clients
        clients_data = [
            ClientProfileCreate(
                name=f"Test Client {i}",
                age=30 + i,
                personality_traits=["anxious", "cooperative"],
                issues=["housing_insecurity"]
            )
            for i in range(3)
        ]
        
        # Create clients
        for client_data in clients_data:
            client_service.create_client_for_teacher(
                db_session, client_data, teacher.teacher_id
            )
        
        # Retrieve clients
        clients = client_service.get_teacher_clients(db_session, teacher.teacher_id)
        
        # Verify
        assert len(clients) >= 3  # May have clients from other tests
        client_names = [client.name for client in clients]
        for i in range(3):
            assert f"Test Client {i}" in client_names
    
    def test_client_isolation_between_teachers(self, db_session):
        """Test that teachers only see their own clients"""
        # Create clients for different teachers
        teacher1_id = "teacher-1"
        teacher2_id = "teacher-2"
        
        client1 = client_service.create_client_for_teacher(
            db_session,
            ClientProfileCreate(
                name="Teacher 1 Client",
                age=25,
                personality_traits=["defensive", "suspicious"]
            ),
            teacher1_id
        )
        
        client2 = client_service.create_client_for_teacher(
            db_session,
            ClientProfileCreate(
                name="Teacher 2 Client",
                age=35,
                personality_traits=["cooperative", "talkative"]
            ),
            teacher2_id
        )
        
        # Get clients for each teacher
        teacher1_clients = client_service.get_teacher_clients(db_session, teacher1_id)
        teacher2_clients = client_service.get_teacher_clients(db_session, teacher2_id)
        
        # Verify isolation
        teacher1_client_names = [c.name for c in teacher1_clients]
        teacher2_client_names = [c.name for c in teacher2_clients]
        
        assert "Teacher 1 Client" in teacher1_client_names
        assert "Teacher 2 Client" not in teacher1_client_names
        assert "Teacher 2 Client" in teacher2_client_names
        assert "Teacher 1 Client" not in teacher2_client_names
    
    def test_client_with_minimal_data(self, db_session, teacher):
        """Test creating a client with only required fields"""
        minimal_client = ClientProfileCreate(
            name="Minimal Client",
            age=50,
            personality_traits=["reserved", "honest"]
        )
        
        created = client_service.create_client_for_teacher(
            db_session, minimal_client, teacher.teacher_id
        )
        
        # Verify
        assert created.name == "Minimal Client"
        assert created.age == 50
        assert created.gender is None
        assert created.race is None
        assert created.socioeconomic_status is None
        assert created.issues == []
        assert created.background_story is None
        assert created.communication_style is None
        assert len(created.personality_traits) == 2
    
    def test_client_with_all_fields(self, db_session, teacher):
        """Test creating a client with all fields populated"""
        full_client = ClientProfileCreate(
            name="Complete Client Profile",
            age=38,
            gender="Non-binary",
            race="Mixed",
            socioeconomic_status="Working class",
            issues=[
                "substance_abuse", "mental_health", "trauma_history",
                "unemployment", "housing_insecurity"
            ],
            background_story="A detailed background story " * 10,  # Long story
            personality_traits=["defensive", "anxious", "emotional", "suspicious", "withdrawn"],
            communication_style="indirect"
        )
        
        created = client_service.create_client_for_teacher(
            db_session, full_client, teacher.teacher_id
        )
        
        # Verify all fields
        assert created.name == full_client.name
        assert created.age == full_client.age
        assert created.gender == full_client.gender
        assert created.race == full_client.race
        assert created.socioeconomic_status == full_client.socioeconomic_status
        assert len(created.issues) == 5
        assert created.background_story == full_client.background_story
        assert len(created.personality_traits) == 5
        assert created.communication_style == full_client.communication_style
    
    def test_database_connection_utility(self):
        """Test the get_database_connection utility function"""
        # Get connection
        db = get_database_connection()
        
        # Verify it's a valid session
        assert isinstance(db, Session)
        
        # Test we can query
        result = db.execute(text("SELECT 1")).scalar()
        assert result == 1
        
        # Clean up
        db.close()
    
    def test_mock_teacher_consistency(self):
        """Test that mock teacher returns consistent data"""
        teacher1 = get_mock_teacher()
        teacher2 = get_mock_teacher()
        
        assert teacher1.teacher_id == teacher2.teacher_id
        assert teacher1.teacher_id == "teacher-1"
        assert isinstance(teacher1, TeacherAuth)
