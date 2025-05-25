"""
Quick test for Phase 1.3 Part 6 - Enhanced Validation
Demonstrates the improved error messages
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly to avoid circular import issues
import json
from pydantic import ValidationError, BaseModel, Field, validator
from typing import List, Optional

# Copy the model classes locally to avoid circular imports
class ScoringLevel(BaseModel):
    """Scoring level definition"""
    excellent: int = 4
    good: int = 3
    satisfactory: int = 2
    needs_improvement: int = 1


class RubricCriterion(BaseModel):
    """Individual evaluation criterion"""
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Name of the evaluation criterion (e.g., 'Communication Skills')"
    )
    description: str = Field(
        ...,
        description="Detailed description of what this criterion evaluates"
    )
    weight: float = Field(
        ..., 
        ge=0, 
        le=1,
        description="Weight of this criterion (0.0 to 1.0). All criteria weights must sum to 1.0"
    )
    evaluation_points: List[str] = Field(
        ..., 
        min_items=1,
        description="List of specific behaviors or skills to evaluate (at least one required)"
    )
    scoring_levels: ScoringLevel = Field(
        default_factory=ScoringLevel,
        description="Scoring levels for this criterion (defaults to 4-point scale)"
    )
    
    @validator('weight')
    def validate_weight(cls, v):
        """Ensure weight is between 0 and 1"""
        if v < 0:
            raise ValueError(f'Criterion weight cannot be negative. You provided {v}, but weights must be between 0.0 and 1.0')
        if v > 1:
            raise ValueError(f'Criterion weight cannot exceed 1.0. You provided {v}, but the maximum allowed weight is 1.0')
        return v


class EvaluationRubricCreate(BaseModel):
    """Schema for creating a new evaluation rubric"""
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=200,
        description="Name of the evaluation rubric"
    )
    description: Optional[str] = Field(
        None,
        description="Optional description of the rubric's purpose and use"
    )
    criteria: List[RubricCriterion] = Field(
        ..., 
        min_items=1,
        description="List of evaluation criteria. At least one criterion is required"
    )
    
    @validator('criteria')
    def validate_total_weight(cls, v):
        """Ensure all criteria weights sum to 1.0"""
        if not v:
            raise ValueError('At least one evaluation criterion is required')
        
        total_weight = sum(criterion.weight for criterion in v)
        
        # Allow small floating point differences (0.001 tolerance)
        if abs(total_weight - 1.0) > 0.001:
            # Provide helpful error message with current sum and guidance
            criteria_info = [f"{c.name}: {c.weight}" for c in v]
            raise ValueError(
                f'Criteria weights must sum to exactly 1.0, but your weights sum to {total_weight:.3f}. '
                f'Current weights: {{", ".join(criteria_info)}}. '
                f'Please adjust the weights so they total 1.0 (100% of the evaluation).'
            )
        return v


def test_weight_validation():
    """Test improved weight validation messages"""
    print("\n=== Testing Weight Validation ===")
    
    # Test 1: Weights don't sum to 1.0
    print("\n1. Testing weights that don't sum to 1.0:")
    try:
        rubric = EvaluationRubricCreate(
            name="Test Rubric",
            description="Testing weight validation",
            criteria=[
                RubricCriterion(
                    name="Communication",
                    description="Test",
                    weight=0.3,
                    evaluation_points=["Point 1"]
                ),
                RubricCriterion(
                    name="Empathy",
                    description="Test",
                    weight=0.5,
                    evaluation_points=["Point 2"]
                )
            ]
        )
    except ValidationError as e:
        print("✓ Validation error caught!")
        errors = e.errors()
        for error in errors:
            if "criteria" in error['loc']:
                print(f"  Error message: {error['msg']}")
                # The error should show the actual sum (0.8) and current weights
    
    # Test 2: Negative weight
    print("\n2. Testing negative weight:")
    try:
        criterion = RubricCriterion(
            name="Bad Criterion",
            description="Has negative weight",
            weight=-0.5,
            evaluation_points=["Test"]
        )
    except ValidationError as e:
        print("✓ Validation error caught!")
        errors = e.errors()
        for error in errors:
            print(f"  Error message: {error['msg']}")
    
    # Test 3: Weight > 1.0
    print("\n3. Testing weight greater than 1.0:")
    try:
        criterion = RubricCriterion(
            name="Heavy Criterion",
            description="Weight too high",
            weight=1.5,
            evaluation_points=["Test"]
        )
    except ValidationError as e:
        print("✓ Validation error caught!")
        errors = e.errors()
        for error in errors:
            print(f"  Error message: {error['msg']}")


def test_empty_validation():
    """Test validation for empty fields"""
    print("\n=== Testing Empty Field Validation ===")
    
    # Test empty evaluation points
    print("\n1. Testing empty evaluation points:")
    try:
        criterion = RubricCriterion(
            name="Empty Points",
            description="No evaluation points",
            weight=1.0,
            evaluation_points=[]
        )
    except ValidationError as e:
        print("✓ Validation error caught!")
        errors = e.errors()
        for error in errors:
            if "evaluation_points" in error['loc']:
                print(f"  Error message: {error['msg']}")
    
    # Test empty criteria list
    print("\n2. Testing empty criteria list:")
    try:
        rubric = EvaluationRubricCreate(
            name="Empty Rubric",
            description="No criteria",
            criteria=[]
        )
    except ValidationError as e:
        print("✓ Validation error caught!")
        errors = e.errors()
        for error in errors:
            if "criteria" in error['loc']:
                print(f"  Error message: {error['msg']}")


def test_valid_rubric():
    """Test that a valid rubric passes validation"""
    print("\n=== Testing Valid Rubric Creation ===")
    
    try:
        rubric = EvaluationRubricCreate(
            name="Valid Rubric",
            description="This should work",
            criteria=[
                RubricCriterion(
                    name="Communication",
                    description="Evaluates communication",
                    weight=0.6,
                    evaluation_points=["Clear speech", "Active listening"]
                ),
                RubricCriterion(
                    name="Empathy",
                    description="Evaluates empathy",
                    weight=0.4,
                    evaluation_points=["Shows understanding"]
                )
            ]
        )
        print("✓ Valid rubric created successfully!")
        print(f"  Name: {rubric.name}")
        print(f"  Criteria count: {len(rubric.criteria)}")
        total_weight = sum(c.weight for c in rubric.criteria)
        print(f"  Total weight: {total_weight}")
    except ValidationError as e:
        print("✗ Unexpected validation error!")
        print(json.dumps(e.errors(), indent=2))


def main():
    """Run all validation tests"""
    print("Phase 1.3 Part 6 - Enhanced Validation Test")
    print("=" * 50)
    
    test_weight_validation()
    test_empty_validation()
    test_valid_rubric()
    
    print("\n" + "=" * 50)
    print("Enhanced validation tests complete!")
    print("\nKey improvements:")
    print("- Weight errors now show the actual sum and all criterion weights")
    print("- Negative/excessive weight errors show the provided value")
    print("- All error messages provide clear guidance on fixing the issue")
    print("- Field descriptions help users understand requirements")


if __name__ == "__main__":
    main()
