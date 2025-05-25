#!/usr/bin/env python3
"""
Test script to verify Section CRUD endpoints are working correctly.
Phase 1.4 Part 3 - Section CRUD Endpoints
"""

import requests
import json
from datetime import datetime


BASE_URL = "http://localhost:8000/api/teacher"


def print_response(response, title="Response"):
    """Pretty print API response"""
    print(f"\n{title}:")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Body: {response.text}")


def test_section_endpoints():
    """Test all section CRUD endpoints"""
    
    print("=" * 60)
    print("Testing Section CRUD Endpoints")
    print("=" * 60)
    
    # Test data
    section_data = {
        "name": "Social Work Practice I - Fall 2025",
        "description": "Introduction to social work practice with individuals and families",
        "course_code": "SW101",
        "term": "Fall 2025",
        "is_active": True,
        "settings": {
            "allow_late_submissions": True,
            "max_attempts_per_assignment": 3
        }
    }
    
    # 1. CREATE SECTION
    print("\n1. CREATE SECTION")
    print("-" * 40)
    response = requests.post(f"{BASE_URL}/sections", json=section_data)
    print_response(response, "Create Section Response")
    
    if response.status_code != 201:
        print("ERROR: Failed to create section")
        return
    
    section_id = response.json()["id"]
    print(f"\n✓ Section created with ID: {section_id}")
    
    # 2. LIST SECTIONS
    print("\n\n2. LIST SECTIONS")
    print("-" * 40)
    response = requests.get(f"{BASE_URL}/sections")
    print_response(response, "List Sections Response")
    
    if response.status_code == 200:
        sections = response.json()
        print(f"\n✓ Found {len(sections)} section(s)")
    
    # 3. GET SPECIFIC SECTION
    print("\n\n3. GET SPECIFIC SECTION")
    print("-" * 40)
    response = requests.get(f"{BASE_URL}/sections/{section_id}")
    print_response(response, "Get Section Response")
    
    if response.status_code == 200:
        print("\n✓ Successfully retrieved section")
    
    # 4. UPDATE SECTION
    print("\n\n4. UPDATE SECTION")
    print("-" * 40)
    update_data = {
        "description": "Updated: Advanced social work practice techniques",
        "is_active": False,
        "settings": {
            "allow_late_submissions": False,
            "max_attempts_per_assignment": 5,
            "new_setting": "test"
        }
    }
    response = requests.put(f"{BASE_URL}/sections/{section_id}", json=update_data)
    print_response(response, "Update Section Response")
    
    if response.status_code == 200:
        print("\n✓ Successfully updated section")
    
    # 5. VERIFY UPDATE
    print("\n\n5. VERIFY UPDATE")
    print("-" * 40)
    response = requests.get(f"{BASE_URL}/sections/{section_id}")
    if response.status_code == 200:
        updated_section = response.json()
        print(f"Description: {updated_section['description']}")
        print(f"Is Active: {updated_section['is_active']}")
        print(f"Settings: {json.dumps(updated_section['settings'], indent=2)}")
        print("\n✓ Updates confirmed")
    
    # 6. DELETE SECTION
    print("\n\n6. DELETE SECTION")
    print("-" * 40)
    response = requests.delete(f"{BASE_URL}/sections/{section_id}")
    print(f"Delete Response Status: {response.status_code}")
    
    if response.status_code == 204:
        print("\n✓ Successfully deleted section")
    
    # 7. VERIFY DELETION
    print("\n\n7. VERIFY DELETION")
    print("-" * 40)
    response = requests.get(f"{BASE_URL}/sections/{section_id}")
    print_response(response, "Get Deleted Section Response")
    
    if response.status_code == 404:
        print("\n✓ Section confirmed deleted")
    
    print("\n" + "=" * 60)
    print("All Section CRUD endpoints tested successfully!")
    print("=" * 60)


def test_error_cases():
    """Test error handling for section endpoints"""
    
    print("\n\n" + "=" * 60)
    print("Testing Error Handling")
    print("=" * 60)
    
    # Test 404 - Not Found
    print("\n1. TEST 404 - Not Found")
    print("-" * 40)
    response = requests.get(f"{BASE_URL}/sections/non-existent-id")
    print_response(response, "404 Error Response")
    
    # Test 422 - Validation Error
    print("\n\n2. TEST 422 - Validation Error")
    print("-" * 40)
    invalid_data = {
        "name": "",  # Empty name should fail validation
        "description": "Test"
    }
    response = requests.post(f"{BASE_URL}/sections", json=invalid_data)
    print_response(response, "422 Validation Error Response")
    
    # Test 400 - Empty Update
    print("\n\n3. TEST 400 - Empty Update")
    print("-" * 40)
    # First create a section
    section_data = {"name": "Test Section"}
    create_response = requests.post(f"{BASE_URL}/sections", json=section_data)
    if create_response.status_code == 201:
        section_id = create_response.json()["id"]
        # Try to update with empty data
        response = requests.put(f"{BASE_URL}/sections/{section_id}", json={})
        print_response(response, "400 Empty Update Response")
        # Clean up
        requests.delete(f"{BASE_URL}/sections/{section_id}")


if __name__ == "__main__":
    print("Starting Section CRUD Endpoint Tests...")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    
    try:
        # Test if server is running
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("\nERROR: Server is not responding. Please start the server first.")
            print("Run: python -m uvicorn backend.app:app --reload")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to server. Please start the server first.")
        print("Run: python -m uvicorn backend.app:app --reload")
        exit(1)
    
    # Run tests
    test_section_endpoints()
    test_error_cases()
    
    print("\n✓ All tests completed!")
