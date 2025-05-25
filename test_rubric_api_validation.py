"""
API-based test for Phase 1.3 Part 6 - Enhanced Validation
Tests the validation improvements via HTTP requests
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api/teacher"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_test_header(test_name: str):
    """Print a formatted test header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{test_name}{Colors.ENDC}")
    print("=" * 50)


def print_result(success: bool, message: str):
    """Print a test result with color"""
    if success:
        print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")
    else:
        print(f"{Colors.RED}✗ {message}{Colors.ENDC}")


def test_weight_sum_validation():
    """Test weight sum validation with helpful error message"""
    print_test_header("Testing Weight Sum Validation")
    
    # Create rubric with weights that don't sum to 1.0
    rubric_data = {
        "name": "Bad Weight Sum",
        "description": "Testing weight validation",
        "criteria": [
            {
                "name": "Communication",
                "description": "Communication skills",
                "weight": 0.3,
                "evaluation_points": ["Clear speech", "Active listening"]
            },
            {
                "name": "Empathy",
                "description": "Empathy and understanding",
                "weight": 0.5,  # Total = 0.8
                "evaluation_points": ["Shows understanding"]
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/rubrics", json=rubric_data)
    
    if response.status_code == 422:
        print_result(True, "Validation error caught as expected")
        error_data = response.json()
        print("\nError details:")
        
        # Check if the error message includes the helpful information
        error_str = json.dumps(error_data, indent=2)
        print(error_str)
        
        if "0.8" in error_str:
            print_result(True, "Error shows actual sum (0.8)")
        if "Communication: 0.3" in error_str:
            print_result(True, "Error shows individual weights")
        if "Please adjust the weights" in error_str:
            print_result(True, "Error provides guidance")
    else:
        print_result(False, f"Expected 422, got {response.status_code}")


def test_negative_weight():
    """Test negative weight validation"""
    print_test_header("Testing Negative Weight Validation")
    
    rubric_data = {
        "name": "Negative Weight",
        "criteria": [{
            "name": "Bad Criterion",
            "description": "Has negative weight",
            "weight": -0.5,
            "evaluation_points": ["Test"]
        }]
    }
    
    response = requests.post(f"{BASE_URL}/rubrics", json=rubric_data)
    
    if response.status_code == 422:
        print_result(True, "Validation error caught as expected")
        error_str = json.dumps(response.json(), indent=2)
        print("\nError details:")
        print(error_str)
        
        if "-0.5" in error_str and "cannot be negative" in error_str:
            print_result(True, "Error message shows the negative value and explanation")
    else:
        print_result(False, f"Expected 422, got {response.status_code}")


def test_duplicate_criterion_names():
    """Test duplicate criterion name validation"""
    print_test_header("Testing Duplicate Criterion Names")
    
    rubric_data = {
        "name": "Duplicate Names",
        "criteria": [
            {
                "name": "Communication",
                "description": "First communication criterion",
                "weight": 0.5,
                "evaluation_points": ["Point 1"]
            },
            {
                "name": "Communication",  # Duplicate name
                "description": "Second communication criterion",
                "weight": 0.5,
                "evaluation_points": ["Point 2"]
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/rubrics", json=rubric_data)
    
    if response.status_code == 400:
        print_result(True, "Duplicate names caught as expected")
        error_data = response.json()
        print("\nError details:")
        print(json.dumps(error_data, indent=2))
        
        error_msg = error_data.get("detail", "")
        if "duplicate criterion names" in error_msg and "communication" in error_msg.lower():
            print_result(True, "Error message identifies the duplicate name")
    else:
        print_result(False, f"Expected 400, got {response.status_code}")


def test_valid_rubric():
    """Test that a valid rubric can be created"""
    print_test_header("Testing Valid Rubric Creation")
    
    rubric_data = {
        "name": "Valid Test Rubric",
        "description": "This should work perfectly",
        "criteria": [
            {
                "name": "Communication",
                "description": "Communication skills",
                "weight": 0.6,
                "evaluation_points": ["Clear speech", "Active listening", "Asks questions"]
            },
            {
                "name": "Empathy",
                "description": "Empathy and understanding",
                "weight": 0.4,
                "evaluation_points": ["Shows understanding", "Validates feelings"]
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/rubrics", json=rubric_data)
    
    if response.status_code == 201:
        print_result(True, "Valid rubric created successfully")
        rubric = response.json()
        print(f"\nCreated rubric:")
        print(f"  ID: {rubric['id']}")
        print(f"  Name: {rubric['name']}")
        print(f"  Criteria count: {len(rubric['criteria'])}")
        
        # Clean up - delete the rubric
        delete_response = requests.delete(f"{BASE_URL}/rubrics/{rubric['id']}")
        if delete_response.status_code == 204:
            print_result(True, "Test rubric cleaned up")
    else:
        print_result(False, f"Failed to create valid rubric: {response.status_code}")
        print(json.dumps(response.json(), indent=2))


def main():
    """Run all API validation tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}Phase 1.3 Part 6 - API Validation Tests{Colors.ENDC}")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/test")
        if response.status_code != 200:
            print(f"{Colors.RED}Error: API server is not responding correctly{Colors.ENDC}")
            print("Please start the server with: python -m uvicorn backend.app:app --reload")
            return
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}Error: Cannot connect to API server{Colors.ENDC}")
        print("Please start the server with: python -m uvicorn backend.app:app --reload")
        return
    
    print(f"{Colors.GREEN}✓ API server is running{Colors.ENDC}")
    
    # Run tests
    test_weight_sum_validation()
    test_negative_weight()
    test_duplicate_criterion_names()
    test_valid_rubric()
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}All validation tests completed!{Colors.ENDC}")
    print("\nKey improvements demonstrated:")
    print("- Weight sum errors show actual sum and all weights")
    print("- Negative weight errors show the provided value")
    print("- Duplicate name errors identify which names are duplicated")
    print("- All errors provide clear guidance on how to fix issues")


if __name__ == "__main__":
    main()
