"""
Test script for Phase 1.2 Part 6 - Error Handling
Tests all error cases for the teacher API endpoints
"""

import requests
import json
from typing import Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# API base URL
BASE_URL = "http://localhost:8000/api/teacher"

# Test data
VALID_CLIENT_DATA = {
    "name": "Test Client",
    "age": 30,
    "gender": "female",
    "race": "Hispanic",
    "socioeconomic_status": "middle_class",
    "background_story": "Test background",
    "personality_traits": ["anxious", "defensive"],
    "communication_style": "guarded",
    "issues": ["housing_insecurity"]
}

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
    print(f"\n{Colors.BOLD}{Colors.BLUE}Testing: {test_name}{Colors.ENDC}")
    print("=" * 60)


def print_result(success: bool, message: str):
    """Print a test result with color"""
    if success:
        print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")
    else:
        print(f"{Colors.RED}✗ {message}{Colors.ENDC}")


def print_error_details(response):
    """Print error response details"""
    try:
        error_data = response.json()
        print(f"  Status Code: {response.status_code}")
        print(f"  Error Details: {json.dumps(error_data, indent=2)}")
    except:
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Text: {response.text}")


def test_404_errors():
    """Test 404 Not Found error cases"""
    print_test_header("404 Not Found Errors")
    
    # Test 1: Get non-existent client
    print("\n1. GET non-existent client:")
    response = requests.get(f"{BASE_URL}/clients/non-existent-id")
    if response.status_code == 404:
        print_result(True, "Correctly returned 404 for non-existent client")
        print_error_details(response)
    else:
        print_result(False, f"Expected 404, got {response.status_code}")
        print_error_details(response)
    
    # Test 2: Update non-existent client
    print("\n2. UPDATE non-existent client:")
    response = requests.put(
        f"{BASE_URL}/clients/non-existent-id",
        json={"name": "Updated Name"}
    )
    if response.status_code == 404:
        print_result(True, "Correctly returned 404 for update on non-existent client")
        print_error_details(response)
    else:
        print_result(False, f"Expected 404, got {response.status_code}")
        print_error_details(response)
    
    # Test 3: Delete non-existent client
    print("\n3. DELETE non-existent client:")
    response = requests.delete(f"{BASE_URL}/clients/non-existent-id")
    if response.status_code == 404:
        print_result(True, "Correctly returned 404 for delete on non-existent client")
        print_error_details(response)
    else:
        print_result(False, f"Expected 404, got {response.status_code}")
        print_error_details(response)


def test_403_errors():
    """Test 403 Forbidden error cases"""
    print_test_header("403 Forbidden Errors")
    
    # First, create a client to test with
    print("\nCreating test client...")
    response = requests.post(f"{BASE_URL}/clients", json=VALID_CLIENT_DATA)
    if response.status_code != 201:
        print_result(False, "Failed to create test client")
        print_error_details(response)
        return
    
    client_id = response.json()["id"]
    print_result(True, f"Created test client with ID: {client_id}")
    
    # To properly test 403, we'd need to simulate a different teacher
    # Since we're using mock auth that always returns "teacher-123",
    # we can't actually trigger 403 errors in this test environment
    print(f"\n{Colors.YELLOW}Note: 403 errors cannot be fully tested with mock authentication{Colors.ENDC}")
    print("In production, these would trigger when accessing another teacher's client")
    
    # Clean up
    requests.delete(f"{BASE_URL}/clients/{client_id}")


def test_400_errors():
    """Test 400 Bad Request error cases"""
    print_test_header("400 Bad Request Errors")
    
    # Test 1: Create client with missing required fields
    print("\n1. CREATE client with missing required fields:")
    invalid_data = {"name": "Test Client"}  # Missing many required fields
    response = requests.post(f"{BASE_URL}/clients", json=invalid_data)
    if response.status_code == 422:  # FastAPI returns 422 for validation errors
        print_result(True, "Correctly returned 422 for validation error")
        print_error_details(response)
    else:
        print_result(False, f"Expected 422, got {response.status_code}")
        print_error_details(response)
    
    # Test 2: Create client with invalid data types
    print("\n2. CREATE client with invalid data types:")
    invalid_data = {
        **VALID_CLIENT_DATA,
        "age": "not-a-number"  # Should be integer
    }
    response = requests.post(f"{BASE_URL}/clients", json=invalid_data)
    if response.status_code == 422:
        print_result(True, "Correctly returned 422 for invalid data type")
        print_error_details(response)
    else:
        print_result(False, f"Expected 422, got {response.status_code}")
        print_error_details(response)
    
    # Test 3: Update with empty data
    print("\n3. UPDATE with empty data:")
    # First create a client
    response = requests.post(f"{BASE_URL}/clients", json=VALID_CLIENT_DATA)
    if response.status_code == 201:
        client_id = response.json()["id"]
        
        # Try to update with empty data
        response = requests.put(f"{BASE_URL}/clients/{client_id}", json={})
        if response.status_code == 400:
            print_result(True, "Correctly returned 400 for empty update")
            print_error_details(response)
        else:
            print_result(False, f"Expected 400, got {response.status_code}")
            print_error_details(response)
        
        # Clean up
        requests.delete(f"{BASE_URL}/clients/{client_id}")
    
    # Test 4: Invalid JSON
    print("\n4. CREATE with invalid JSON:")
    response = requests.post(
        f"{BASE_URL}/clients",
        data="not-json",
        headers={"Content-Type": "application/json"}
    )
    if response.status_code in [400, 422]:
        print_result(True, f"Correctly returned {response.status_code} for invalid JSON")
        print_error_details(response)
    else:
        print_result(False, f"Expected 400/422, got {response.status_code}")
        print_error_details(response)


def test_validation_error_details():
    """Test that validation errors provide helpful details"""
    print_test_header("Validation Error Details")
    
    # Test with multiple validation errors
    print("\nCreating client with multiple validation errors:")
    invalid_data = {
        "name": "",  # Empty name
        "age": -5,   # Negative age
        "gender": "invalid_gender",  # Invalid enum
        # Missing required fields: race, socioeconomic_status, etc.
    }
    
    response = requests.post(f"{BASE_URL}/clients", json=invalid_data)
    if response.status_code == 422:
        print_result(True, "Validation error returned with details")
        
        error_data = response.json()
        if "detail" in error_data:
            print(f"\nValidation errors found:")
            for error in error_data["detail"]:
                field = " -> ".join(str(x) for x in error["loc"][1:])  # Skip 'body' in path
                print(f"  - {field}: {error['msg']}")
    else:
        print_result(False, f"Expected 422, got {response.status_code}")
        print_error_details(response)


def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print_test_header("Edge Cases")
    
    # Test 1: Very long client ID
    print("\n1. GET with very long client ID:")
    long_id = "a" * 1000
    response = requests.get(f"{BASE_URL}/clients/{long_id}")
    if response.status_code == 404:
        print_result(True, "Handled very long ID gracefully")
    else:
        print_result(False, f"Unexpected response: {response.status_code}")
    
    # Test 2: Special characters in ID
    print("\n2. GET with special characters in ID:")
    special_id = "../../../etc/passwd"
    response = requests.get(f"{BASE_URL}/clients/{special_id}")
    if response.status_code in [404, 422]:
        print_result(True, f"Handled special characters safely (status: {response.status_code})")
    else:
        print_result(False, f"Unexpected response: {response.status_code}")
    
    # Test 3: SQL injection attempt in ID
    print("\n3. GET with SQL injection attempt:")
    sql_id = "1'; DROP TABLE clients; --"
    response = requests.get(f"{BASE_URL}/clients/{sql_id}")
    if response.status_code in [404, 422]:
        print_result(True, f"Handled SQL injection attempt safely (status: {response.status_code})")
    else:
        print_result(False, f"Unexpected response: {response.status_code}")


def main():
    """Run all error handling tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}Phase 1.2 Part 6 - Error Handling Tests{Colors.ENDC}")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/api/teacher/test")
        if response.status_code != 200:
            print(f"{Colors.RED}Error: API server is not responding correctly{Colors.ENDC}")
            print("Please start the server with: python -m uvicorn backend.app:app --reload")
            return
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}Error: Cannot connect to API server{Colors.ENDC}")
        print("Please start the server with: python -m uvicorn backend.app:app --reload")
        return
    
    print(f"{Colors.GREEN}✓ API server is running{Colors.ENDC}")
    
    # Run all test suites
    test_404_errors()
    test_403_errors()
    test_400_errors()
    test_validation_error_details()
    test_edge_cases()
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}All error handling tests completed!{Colors.ENDC}")
    print("\nNote: Some tests (like 403 Forbidden) cannot be fully tested with mock authentication.")
    print("In production, these would work with real authentication that supports multiple users.")


if __name__ == "__main__":
    main()
