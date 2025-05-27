"""
Tests for MVP utilities

Tests the shared utilities used by all MVP Streamlit interfaces.
"""

import pytest
import sys
from pathlib import Path
from sqlalchemy.orm import Session

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from mvp.utils import (
    get_database_connection,
    get_mock_teacher,
    get_mock_student,
    format_cost,
    format_tokens,
    estimate_conversation_cost,
    check_database_connection,
    DEFAULT_MODEL,
    MODEL_COSTS
)
from backend.models.auth import TeacherAuth, StudentAuth


class TestMVPUtils:
    """Test suite for MVP utilities"""
    
    def test_get_database_connection(self):
        """Test database connection retrieval"""
        db = get_database_connection()
        assert db is not None
        assert isinstance(db, Session)
        # Clean up
        db.close()
    
    def test_check_database_connection(self):
        """Test database connection check"""
        result = check_database_connection()
        assert isinstance(result, bool)
        # Should be True in test environment
        assert result is True
    
    def test_get_mock_teacher(self):
        """Test mock teacher authentication"""
        teacher = get_mock_teacher()
        assert isinstance(teacher, TeacherAuth)
        assert teacher.id == "teacher-1"
        assert teacher.teacher_id == "teacher-1"
    
    def test_get_mock_student(self):
        """Test mock student authentication"""
        student = get_mock_student()
        assert isinstance(student, StudentAuth)
        assert student.id == "student-1"
        assert student.student_id == "student-1"
    
    def test_format_cost(self):
        """Test cost formatting"""
        # Test very small costs (4 decimal places)
        assert format_cost(0.0001) == "$0.0001"
        assert format_cost(0.0045) == "$0.0045"
        
        # Test small costs (3 decimal places)
        assert format_cost(0.123) == "$0.123"
        assert format_cost(0.999) == "$0.999"
        
        # Test larger costs (2 decimal places)
        assert format_cost(1.00) == "$1.00"
        assert format_cost(10.50) == "$10.50"
        assert format_cost(100.00) == "$100.00"
    
    def test_format_tokens(self):
        """Test token count formatting"""
        # Small counts (no formatting)
        assert format_tokens(50) == "50"
        assert format_tokens(999) == "999"
        
        # Large counts (with commas)
        assert format_tokens(1000) == "1,000"
        assert format_tokens(1500) == "1,500"
        assert format_tokens(150000) == "150,000"
        assert format_tokens(1234567) == "1,234,567"
    
    def test_estimate_conversation_cost_default_model(self):
        """Test conversation cost estimation with default model"""
        # Test with default Haiku model
        cost = estimate_conversation_cost(
            messages_count=10,
            avg_tokens_per_message=50,
            model=DEFAULT_MODEL
        )
        
        # 10 messages * 50 tokens = 500 total tokens
        # Split 50/50: 250 input, 250 output
        # Haiku costs: $0.00025/1K input, $0.00125/1K output
        expected = (250 * 0.00025 / 1000) + (250 * 0.00125 / 1000)
        assert cost == pytest.approx(expected, rel=1e-6)
    
    def test_estimate_conversation_cost_sonnet_model(self):
        """Test conversation cost estimation with Sonnet model"""
        cost = estimate_conversation_cost(
            messages_count=10,
            avg_tokens_per_message=50,
            model="claude-3-5-sonnet-20241022"
        )
        
        # 10 messages * 50 tokens = 500 total tokens
        # Split 50/50: 250 input, 250 output
        # Sonnet costs: $0.003/1K input, $0.015/1K output
        expected = (250 * 0.003 / 1000) + (250 * 0.015 / 1000)
        assert cost == pytest.approx(expected, rel=1e-6)
    
    def test_estimate_conversation_cost_unknown_model(self):
        """Test conversation cost estimation with unknown model (should use default)"""
        cost = estimate_conversation_cost(
            messages_count=10,
            avg_tokens_per_message=50,
            model="unknown-model"
        )
        
        # Should fall back to default model costs
        default_costs = MODEL_COSTS[DEFAULT_MODEL]
        expected = (250 * default_costs["input"] / 1000) + (250 * default_costs["output"] / 1000)
        assert cost == pytest.approx(expected, rel=1e-6)
    
    def test_model_costs_structure(self):
        """Test that model costs are properly defined"""
        assert DEFAULT_MODEL in MODEL_COSTS
        assert "claude-3-5-sonnet-20241022" in MODEL_COSTS
        
        for model, costs in MODEL_COSTS.items():
            assert "input" in costs
            assert "output" in costs
            assert isinstance(costs["input"], (int, float))
            assert isinstance(costs["output"], (int, float))
            assert costs["input"] > 0
            assert costs["output"] > 0
