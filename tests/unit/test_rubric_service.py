"""
Unit tests for RubricService
"""

import pytest
from backend.services.rubric_service import RubricService, rubric_service
from backend.models.rubric import EvaluationRubricDB


def test_rubric_service_init():
    """Test that RubricService initializes correctly"""
    # Create a new instance
    service = RubricService()
    
    # Verify it's an instance of RubricService
    assert isinstance(service, RubricService)
    
    # Verify it has the correct model
    assert service.model == EvaluationRubricDB
    
    # Verify the global instance exists
    assert rubric_service is not None
    assert isinstance(rubric_service, RubricService)
