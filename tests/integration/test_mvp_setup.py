"""
Integration tests for MVP setup

Tests that the MVP infrastructure is properly set up and working.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from mvp.utils import (
    get_database_connection,
    get_mock_teacher,
    get_mock_student,
    check_database_connection
)
from backend.models import ClientProfileDB, SessionDB, MessageDB


class TestMVPIntegration:
    """Integration tests for MVP setup"""
    
    def test_database_tables_exist(self):
        """Test that all required database tables exist"""
        db = get_database_connection()
        
        try:
            # Check client_profiles table
            result = db.execute(text("SELECT COUNT(*) FROM client_profiles"))
            assert result.scalar() >= 0
            
            # Check sessions table
            result = db.execute(text("SELECT COUNT(*) FROM sessions"))
            assert result.scalar() >= 0
            
            # Check messages table
            result = db.execute(text("SELECT COUNT(*) FROM messages"))
            assert result.scalar() >= 0
            
            # Check assignments table
            result = db.execute(text("SELECT COUNT(*) FROM assignments"))
            assert result.scalar() >= 0
            
        finally:
            db.close()
    
    def test_mock_users_can_query_data(self):
        """Test that mock users can access appropriate data"""
        db = get_database_connection()
        teacher = get_mock_teacher()
        student = get_mock_student()
        
        try:
            # Teacher should be able to query clients they created
            clients = db.query(ClientProfileDB).filter_by(
                created_by=teacher.teacher_id
            ).all()
            # This is OK if no clients exist yet
            assert isinstance(clients, list)
            
            # Student should be able to query their sessions
            sessions = db.query(SessionDB).filter_by(
                student_id=student.student_id
            ).all()
            # This is OK if no sessions exist yet
            assert isinstance(sessions, list)
            
        finally:
            db.close()
    
    def test_mvp_directory_structure(self):
        """Test that MVP directory structure is correct"""
        mvp_path = project_root / "mvp"
        
        # Check directory exists
        assert mvp_path.exists()
        assert mvp_path.is_dir()
        
        # Check required files exist
        required_files = [
            "__init__.py",
            "utils.py",
            "test_streamlit.py",
            "teacher_test.py",
            "student_practice.py",
            "admin_monitor.py"
        ]
        
        for filename in required_files:
            file_path = mvp_path / filename
            assert file_path.exists(), f"Missing required file: {filename}"
            assert file_path.is_file(), f"Expected file but found directory: {filename}"
    
    def test_imports_work(self):
        """Test that all MVP modules can be imported"""
        try:
            # Import utils
            from mvp import utils
            
            # Import individual functions
            from mvp.utils import (
                setup_page_config,
                show_error_message,
                show_success_message,
                show_info_message,
                show_warning_message,
                create_sidebar_navigation,
                initialize_session_state,
                render_chat_message,
                render_metric_card
            )
            
            # All imports successful
            assert True
            
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")
    
    def test_database_connection_in_mvp_context(self):
        """Test database connection specifically for MVP usage patterns"""
        # Test multiple sequential connections (Streamlit pattern)
        for i in range(3):
            db = get_database_connection()
            assert db is not None
            
            # Perform a simple query
            result = db.execute(text("SELECT 1"))
            assert result.scalar() == 1
            
            db.close()
    
    @pytest.mark.parametrize("table_name,model_class", [
        ("client_profiles", ClientProfileDB),
        ("sessions", SessionDB),
        ("messages", MessageDB)
    ])
    def test_orm_models_match_tables(self, table_name, model_class):
        """Test that ORM models correctly map to database tables"""
        db = get_database_connection()
        
        try:
            # Try to query using the ORM model
            count = db.query(model_class).count()
            assert count >= 0  # Should not raise error
            
        finally:
            db.close()
    
    def test_mvp_constants_valid(self):
        """Test that MVP constants are properly defined"""
        from mvp.utils import DEFAULT_MODEL, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE
        
        # Check model is valid
        assert DEFAULT_MODEL == "claude-3-haiku-20240307"
        
        # Check token limit is reasonable for MVP
        assert DEFAULT_MAX_TOKENS == 150
        assert DEFAULT_MAX_TOKENS > 0
        assert DEFAULT_MAX_TOKENS <= 1000  # Keep costs low for MVP
        
        # Check temperature is valid
        assert DEFAULT_TEMPERATURE == 0.7
        assert 0 <= DEFAULT_TEMPERATURE <= 1
