"""
Unit tests for Client Service
"""

import pytest
from sqlalchemy.orm import Session

from backend.services.client_service import ClientService, client_service
from backend.services.database import BaseCRUD
from backend.models.client_profile import ClientProfileDB, ClientProfileCreate


class TestClientServiceBasic:
    """Test basic client service functionality"""
    
    def test_client_service_instantiation(self):
        """Test that client service can be instantiated"""
        service = ClientService()
        assert service is not None
        assert isinstance(service, ClientService)
        assert isinstance(service, BaseCRUD)
    
    def test_client_service_model(self):
        """Test that client service uses correct model"""
        service = ClientService()
        assert service.model == ClientProfileDB
    
    def test_global_client_service_instance(self):
        """Test that global instance is available"""
        assert client_service is not None
        assert isinstance(client_service, ClientService)
        assert client_service.model == ClientProfileDB
    
    def test_inherits_base_crud_methods(self):
        """Test that client service inherits BaseCRUD methods"""
        service = ClientService()
        
        # Check that all BaseCRUD methods are available
        assert hasattr(service, 'create')
        assert hasattr(service, 'get')
        assert hasattr(service, 'get_multi')
        assert hasattr(service, 'update')
        assert hasattr(service, 'delete')
        assert hasattr(service, 'count')
        assert hasattr(service, 'exists')
        assert hasattr(service, 'get_db')
        
        # Check they are callable
        assert callable(service.create)
        assert callable(service.get)
        assert callable(service.get_multi)
        assert callable(service.update)
        assert callable(service.delete)
        assert callable(service.count)
        assert callable(service.exists)
    
    def test_basic_crud_operations_work(self, db_session, sample_teacher_id):
        """Test that basic CRUD operations work through inheritance"""
        service = ClientService()
        
        # Test create
        client_data = {
            "name": "Test Client Part 1",
            "age": 30,
            "gender": "Male",
            "created_by": sample_teacher_id
        }
        created_client = service.create(db_session, **client_data)
        assert created_client is not None
        assert created_client.name == "Test Client Part 1"
        assert created_client.age == 30
        assert created_client.created_by == sample_teacher_id
        
        # Test get
        retrieved_client = service.get(db_session, created_client.id)
        assert retrieved_client is not None
        assert retrieved_client.id == created_client.id
        assert retrieved_client.name == "Test Client Part 1"
        
        # Test get_multi
        clients = service.get_multi(db_session)
        assert len(clients) >= 1
        assert any(c.id == created_client.id for c in clients)
        
        # Test update
        updated_client = service.update(db_session, created_client.id, age=31)
        assert updated_client is not None
        assert updated_client.age == 31
        
        # Test count
        count = service.count(db_session)
        assert count >= 1
        
        # Test exists
        exists = service.exists(db_session, id=created_client.id)
        assert exists is True
        
        # Test delete
        deleted = service.delete(db_session, created_client.id)
        assert deleted is True
        
        # Verify deleted
        deleted_client = service.get(db_session, created_client.id)
        assert deleted_client is None


class TestClientServiceTeacherMethods:
    """Test teacher-specific methods in ClientService"""
    
    def test_get_teacher_clients(self, db_session):
        """Test getting clients for a specific teacher"""
        service = ClientService()
        teacher1_id = "teacher-1"
        teacher2_id = "teacher-2"
        
        # Create clients for different teachers
        client1 = service.create(db_session, 
                                name="Client 1", 
                                age=25, 
                                created_by=teacher1_id)
        client2 = service.create(db_session, 
                                name="Client 2", 
                                age=30, 
                                created_by=teacher1_id)
        client3 = service.create(db_session, 
                                name="Client 3", 
                                age=35, 
                                created_by=teacher2_id)
        
        # Get teacher1's clients
        teacher1_clients = service.get_teacher_clients(db_session, teacher1_id)
        assert len(teacher1_clients) == 2
        client_ids = [c.id for c in teacher1_clients]
        assert client1.id in client_ids
        assert client2.id in client_ids
        assert client3.id not in client_ids
        
        # Get teacher2's clients
        teacher2_clients = service.get_teacher_clients(db_session, teacher2_id)
        assert len(teacher2_clients) == 1
        assert teacher2_clients[0].id == client3.id
        
        # Test with pagination
        paginated_clients = service.get_teacher_clients(
            db_session, teacher1_id, skip=1, limit=1
        )
        assert len(paginated_clients) == 1
    
    def test_create_client_for_teacher(self, db_session):
        """Test creating a client for a specific teacher"""
        service = ClientService()
        teacher_id = "test-teacher-123"
        
        # Create client data using Pydantic model
        client_data = ClientProfileCreate(
            name="Test Client",
            age=40,
            gender="Female",
            race="Asian",
            socioeconomic_status="Low income",
            issues=["housing_insecurity", "unemployment"],
            background_story="Test background",
            personality_traits=["anxious", "cooperative"],
            communication_style="indirect"
        )
        
        # Create client for teacher
        created_client = service.create_client_for_teacher(
            db_session, client_data, teacher_id
        )
        
        assert created_client is not None
        assert created_client.name == "Test Client"
        assert created_client.age == 40
        assert created_client.created_by == teacher_id
        assert "housing_insecurity" in created_client.issues
        assert "anxious" in created_client.personality_traits
        
        # Verify it's in the teacher's clients
        teacher_clients = service.get_teacher_clients(db_session, teacher_id)
        assert len(teacher_clients) == 1
        assert teacher_clients[0].id == created_client.id
    
    def test_can_update_permission(self, db_session):
        """Test permission check for updating clients"""
        service = ClientService()
        teacher1_id = "teacher-1"
        teacher2_id = "teacher-2"
        
        # Create a client for teacher1
        client = service.create(db_session,
                               name="Update Test Client",
                               age=25,
                               created_by=teacher1_id)
        
        # Teacher1 should be able to update
        assert service.can_update(db_session, client.id, teacher1_id) is True
        
        # Teacher2 should NOT be able to update
        assert service.can_update(db_session, client.id, teacher2_id) is False
        
        # Non-existent client should return False
        assert service.can_update(db_session, "non-existent-id", teacher1_id) is False
    
    def test_can_delete_permission(self, db_session):
        """Test permission check for deleting clients"""
        service = ClientService()
        teacher1_id = "teacher-1"
        teacher2_id = "teacher-2"
        
        # Create a client for teacher1
        client = service.create(db_session,
                               name="Delete Test Client",
                               age=25,
                               created_by=teacher1_id)
        
        # Teacher1 should be able to delete
        assert service.can_delete(db_session, client.id, teacher1_id) is True
        
        # Teacher2 should NOT be able to delete
        assert service.can_delete(db_session, client.id, teacher2_id) is False
        
        # Non-existent client should return False
        assert service.can_delete(db_session, "non-existent-id", teacher1_id) is False
    
    def test_teacher_methods_integration(self, db_session):
        """Test integration of teacher methods"""
        service = ClientService()
        teacher_id = "integration-teacher"
        
        # Create multiple clients
        client_data1 = ClientProfileCreate(name="Client A", age=20)
        client_data2 = ClientProfileCreate(name="Client B", age=30)
        
        client1 = service.create_client_for_teacher(db_session, client_data1, teacher_id)
        client2 = service.create_client_for_teacher(db_session, client_data2, teacher_id)
        
        # Get all teacher's clients
        clients = service.get_teacher_clients(db_session, teacher_id)
        assert len(clients) == 2
        
        # Check permissions
        assert service.can_update(db_session, client1.id, teacher_id) is True
        assert service.can_delete(db_session, client2.id, teacher_id) is True
        
        # Update one client (using inherited method with permission check)
        if service.can_update(db_session, client1.id, teacher_id):
            updated = service.update(db_session, client1.id, age=21)
            assert updated.age == 21
        
        # Delete one client (using inherited method with permission check)
        if service.can_delete(db_session, client2.id, teacher_id):
            deleted = service.delete(db_session, client2.id)
            assert deleted is True
        
        # Verify only one client remains
        remaining_clients = service.get_teacher_clients(db_session, teacher_id)
        assert len(remaining_clients) == 1
        assert remaining_clients[0].id == client1.id
