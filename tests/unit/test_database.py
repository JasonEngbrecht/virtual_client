"""
Tests for database service and base CRUD operations
"""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.services.database import DatabaseService, BaseCRUD, db_service
from backend.models import ClientProfileDB, ClientProfile, ClientProfileCreate


class TestDatabaseService:
    """Test database service functionality"""
    
    def test_database_service_initialization(self):
        """Test that database service initializes correctly"""
        # Use the global db_service instance
        assert db_service is not None
        assert db_service.engine is not None
        assert db_service.SessionLocal is not None
    
    def test_get_db_context_manager(self):
        """Test database session context manager"""
        with db_service.get_db() as session:
            assert session is not None
            # Session should be active
            assert session.is_active
    
    def test_tables_created(self, db_session):
        """Test that all tables are created"""
        # Get table names from database
        result = db_session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = {row[0] for row in result}
        
        # Check expected tables exist
        expected_tables = {
            'client_profiles',
            'evaluation_rubrics',
            'sessions',
            'evaluations',
            'course_sections',
            'section_enrollments'
        }
        
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in database"


class TestBaseCRUD:
    """Test base CRUD operations"""
    
    @pytest.fixture
    def client_crud(self):
        """Create a CRUD instance for ClientProfile"""
        # Use in-memory database for tests
        return BaseCRUD(ClientProfileDB, "sqlite:///:memory:")
    
    def test_create(self, db_session, client_crud, sample_teacher_id):
        """Test creating a record"""
        client_data = {
            "name": "John Doe",
            "age": 30,
            "race": "Caucasian",
            "gender": "Male",
            "socioeconomic_status": "Middle class",
            "issues": ["depression", "anxiety"],
            "background_story": "Test story",
            "personality_traits": ["withdrawn", "anxious"],
            "communication_style": "indirect",
            "created_by": sample_teacher_id
        }
        
        created = client_crud.create(db_session, **client_data)
        
        assert created is not None
        assert created.id is not None
        assert created.name == "John Doe"
        assert created.age == 30
        assert created.created_by == sample_teacher_id
    
    def test_get(self, db_session, client_crud, sample_client_profile):
        """Test retrieving a record by ID"""
        retrieved = client_crud.get(db_session, sample_client_profile.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_client_profile.id
        assert retrieved.name == sample_client_profile.name
    
    def test_get_not_found(self, db_session, client_crud):
        """Test retrieving non-existent record"""
        retrieved = client_crud.get(db_session, "non-existent-id")
        assert retrieved is None
    
    def test_get_multi(self, db_session, client_crud, sample_teacher_id):
        """Test retrieving multiple records"""
        # Create multiple clients
        for i in range(3):
            client_crud.create(
                db_session,
                name=f"Client {i}",
                age=25 + i,
                created_by=sample_teacher_id
            )
        
        # Get all
        results = client_crud.get_multi(db_session)
        assert len(results) >= 3
        
        # Get with limit
        results = client_crud.get_multi(db_session, limit=2)
        assert len(results) == 2
        
        # Get with filter
        results = client_crud.get_multi(db_session, created_by=sample_teacher_id)
        assert all(r.created_by == sample_teacher_id for r in results)
    
    def test_update(self, db_session, client_crud, sample_client_profile):
        """Test updating a record"""
        updated = client_crud.update(
            db_session,
            sample_client_profile.id,
            name="Updated Name",
            age=40
        )
        
        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.age == 40
        # Other fields should remain unchanged
        assert updated.gender == sample_client_profile.gender
    
    def test_update_not_found(self, db_session, client_crud):
        """Test updating non-existent record"""
        updated = client_crud.update(
            db_session,
            "non-existent-id",
            name="New Name"
        )
        assert updated is None
    
    def test_delete(self, db_session, client_crud, sample_client_profile):
        """Test deleting a record"""
        # Verify exists
        assert client_crud.get(db_session, sample_client_profile.id) is not None
        
        # Delete
        deleted = client_crud.delete(db_session, sample_client_profile.id)
        assert deleted is True
        
        # Verify deleted
        assert client_crud.get(db_session, sample_client_profile.id) is None
    
    def test_delete_not_found(self, db_session, client_crud):
        """Test deleting non-existent record"""
        deleted = client_crud.delete(db_session, "non-existent-id")
        assert deleted is False
    
    def test_count(self, db_session, client_crud, sample_teacher_id):
        """Test counting records"""
        # Initial count
        initial_count = client_crud.count(db_session)
        
        # Create some records
        for i in range(3):
            client_crud.create(
                db_session,
                name=f"Count Test {i}",
                age=30,
                created_by=sample_teacher_id
            )
        
        # Count all
        total_count = client_crud.count(db_session)
        assert total_count == initial_count + 3
        
        # Count with filter
        filtered_count = client_crud.count(db_session, age=30)
        assert filtered_count >= 3
    
    def test_exists(self, db_session, client_crud, sample_client_profile):
        """Test checking if record exists"""
        # Check by ID
        exists = client_crud.exists(db_session, id=sample_client_profile.id)
        assert exists is True
        
        # Check by other fields
        exists = client_crud.exists(
            db_session,
            name=sample_client_profile.name,
            created_by=sample_client_profile.created_by
        )
        assert exists is True
        
        # Check non-existent
        exists = client_crud.exists(db_session, id="non-existent-id")
        assert exists is False


@pytest.mark.unit
class TestDatabaseInitScript:
    """Test the database initialization script"""
    
    def test_init_script_imports(self):
        """Test that init_db script can be imported"""
        try:
            from backend.scripts import init_db
            assert hasattr(init_db, 'init_database')
            assert hasattr(init_db, 'verify_database')
            assert hasattr(init_db, 'add_sample_data')
        except ImportError as e:
            pytest.fail(f"Failed to import init_db script: {e}")
    
    def test_init_database_creates_file(self, tmp_path):
        """Test that init_database creates a database file"""
        from backend.scripts.init_db import init_database, verify_database, get_project_root
        
        # Create temporary database path
        db_path = tmp_path / "test.db"
        
        # Get the actual schema path from project
        project_root = get_project_root()
        schema_path = project_root / "database" / "schema.sql"
        
        # Initialize database
        init_database(str(db_path), str(schema_path))
        
        # Check file exists
        assert db_path.exists()
        
        # Verify database structure
        assert verify_database(str(db_path))
