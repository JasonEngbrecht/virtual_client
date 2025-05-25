"""
Unit tests for Section Service
"""

import pytest
from uuid import uuid4
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from backend.services.section_service import SectionService, section_service
from backend.models.course_section import CourseSectionDB, CourseSectionCreate
from backend.services.database import BaseCRUD


class TestSectionService:
    """Test cases for SectionService class"""
    
    def test_service_instantiation(self):
        """Test that SectionService can be instantiated"""
        service = SectionService()
        assert isinstance(service, SectionService)
        assert isinstance(service, BaseCRUD)
        assert service.model == CourseSectionDB
    
    def test_global_service_instance(self):
        """Test that global section_service is available"""
        assert section_service is not None
        assert isinstance(section_service, SectionService)
    
    def test_get_teacher_sections(self):
        """Test getting sections for a specific teacher"""
        # Arrange
        service = SectionService()
        mock_db = MagicMock(spec=Session)
        teacher_id = "teacher-123"
        
        # Create mock sections
        section1 = CourseSectionDB(
            id=str(uuid4()),
            teacher_id=teacher_id,
            name="SW 101 - Fall 2025",
            description="Introduction to Social Work"
        )
        section2 = CourseSectionDB(
            id=str(uuid4()),
            teacher_id=teacher_id,
            name="SW 102 - Spring 2025",
            description="Advanced Social Work Practice"
        )
        
        # Mock the get_multi method
        with patch.object(service, 'get_multi', return_value=[section1, section2]) as mock_get_multi:
            # Act
            result = service.get_teacher_sections(mock_db, teacher_id, skip=0, limit=10)
            
            # Assert
            assert len(result) == 2
            assert result[0].name == "SW 101 - Fall 2025"
            assert result[1].name == "SW 102 - Spring 2025"
            
            # Verify get_multi was called with correct parameters
            mock_get_multi.assert_called_once_with(
                mock_db,
                skip=0,
                limit=10,
                teacher_id=teacher_id
            )
    
    def test_create_section_for_teacher(self):
        """Test creating a section for a specific teacher"""
        # Arrange
        service = SectionService()
        mock_db = MagicMock(spec=Session)
        teacher_id = "teacher-456"
        
        section_data = CourseSectionCreate(
            name="SW 201 - Fall 2025",
            description="Intermediate Social Work",
            course_code="SW201",
            term="Fall 2025"
        )
        
        expected_section = CourseSectionDB(
            id=str(uuid4()),
            teacher_id=teacher_id,
            name="SW 201 - Fall 2025",
            description="Intermediate Social Work",
            course_code="SW201",
            term="Fall 2025"
        )
        
        # Mock the create method
        with patch.object(service, 'create', return_value=expected_section) as mock_create:
            # Act
            result = service.create_section_for_teacher(mock_db, section_data, teacher_id)
            
            # Assert
            assert result.teacher_id == teacher_id
            assert result.name == "SW 201 - Fall 2025"
            
            # Verify create was called with correct parameters
            expected_dict = section_data.model_dump()
            expected_dict['teacher_id'] = teacher_id
            mock_create.assert_called_once_with(mock_db, **expected_dict)
    
    def test_can_update_returns_true_for_owner(self):
        """Test that can_update returns True for section owner"""
        # Arrange
        service = SectionService()
        mock_db = MagicMock(spec=Session)
        section_id = str(uuid4())
        teacher_id = "teacher-123"
        
        mock_section = CourseSectionDB(
            id=section_id,
            teacher_id=teacher_id,
            name="SW 101"
        )
        
        # Mock the get method
        with patch.object(service, 'get', return_value=mock_section) as mock_get:
            # Act
            result = service.can_update(mock_db, section_id, teacher_id)
            
            # Assert
            assert result is True
            mock_get.assert_called_once_with(mock_db, section_id)
    
    def test_can_update_returns_false_for_non_owner(self):
        """Test that can_update returns False for non-owner"""
        # Arrange
        service = SectionService()
        mock_db = MagicMock(spec=Session)
        section_id = str(uuid4())
        owner_id = "teacher-123"
        other_teacher_id = "teacher-456"
        
        mock_section = CourseSectionDB(
            id=section_id,
            teacher_id=owner_id,
            name="SW 101"
        )
        
        # Mock the get method
        with patch.object(service, 'get', return_value=mock_section) as mock_get:
            # Act
            result = service.can_update(mock_db, section_id, other_teacher_id)
            
            # Assert
            assert result is False
            mock_get.assert_called_once_with(mock_db, section_id)
    
    def test_can_update_returns_false_for_nonexistent_section(self):
        """Test that can_update returns False for nonexistent section"""
        # Arrange
        service = SectionService()
        mock_db = MagicMock(spec=Session)
        section_id = str(uuid4())
        teacher_id = "teacher-123"
        
        # Mock the get method to return None
        with patch.object(service, 'get', return_value=None) as mock_get:
            # Act
            result = service.can_update(mock_db, section_id, teacher_id)
            
            # Assert
            assert result is False
            mock_get.assert_called_once_with(mock_db, section_id)
    
    def test_can_delete_returns_true_for_owner(self):
        """Test that can_delete returns True for section owner"""
        # Arrange
        service = SectionService()
        mock_db = MagicMock(spec=Session)
        section_id = str(uuid4())
        teacher_id = "teacher-123"
        
        mock_section = CourseSectionDB(
            id=section_id,
            teacher_id=teacher_id,
            name="SW 101"
        )
        
        # Mock the get method (via can_update)
        with patch.object(service, 'get', return_value=mock_section) as mock_get:
            # Act
            result = service.can_delete(mock_db, section_id, teacher_id)
            
            # Assert
            assert result is True
            mock_get.assert_called_once_with(mock_db, section_id)
    
    def test_can_delete_returns_false_for_non_owner(self):
        """Test that can_delete returns False for non-owner"""
        # Arrange
        service = SectionService()
        mock_db = MagicMock(spec=Session)
        section_id = str(uuid4())
        owner_id = "teacher-123"
        other_teacher_id = "teacher-456"
        
        mock_section = CourseSectionDB(
            id=section_id,
            teacher_id=owner_id,
            name="SW 101"
        )
        
        # Mock the get method (via can_update)
        with patch.object(service, 'get', return_value=mock_section) as mock_get:
            # Act
            result = service.can_delete(mock_db, section_id, other_teacher_id)
            
            # Assert
            assert result is False
            mock_get.assert_called_once_with(mock_db, section_id)
    
    def test_can_delete_returns_false_for_nonexistent_section(self):
        """Test that can_delete returns False for nonexistent section"""
        # Arrange
        service = SectionService()
        mock_db = MagicMock(spec=Session)
        section_id = str(uuid4())
        teacher_id = "teacher-123"
        
        # Mock the get method to return None (via can_update)
        with patch.object(service, 'get', return_value=None) as mock_get:
            # Act
            result = service.can_delete(mock_db, section_id, teacher_id)
            
            # Assert
            assert result is False
            mock_get.assert_called_once_with(mock_db, section_id)
