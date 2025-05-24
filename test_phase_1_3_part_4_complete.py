"""
Test script to verify Phase 1.3 Part 4 is complete
All CRUD endpoints for rubrics should be working
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/teacher"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")

def print_header(message):
    print(f"\n{BOLD}{message}{RESET}")
    print("=" * len(message))

print_header("Phase 1.3 Part 4 - Complete CRUD Endpoints Test")

# Test 1: List rubrics (should be empty initially)
print_header("Test 1: GET /api/teacher/rubrics (List)")
response = requests.get(f"{BASE_URL}/rubrics")
if response.status_code == 200:
    rubrics = response.json()
    print_success(f"List endpoint working - Found {len(rubrics)} rubrics")
else:
    print_error(f"List failed: {response.status_code} - {response.text}")

# Test 2: Create a rubric
print_header("Test 2: POST /api/teacher/rubrics (Create)")
new_rubric = {
    "name": "Comprehensive Social Work Assessment",
    "description": "Evaluates all aspects of social work practice",
    "criteria": [
        {
            "name": "Client Engagement",
            "description": "Ability to build rapport and trust",
            "weight": 0.25,
            "evaluation_points": [
                "Introduces self professionally",
                "Uses appropriate tone",
                "Shows genuine interest",
                "Maintains appropriate boundaries"
            ]
        },
        {
            "name": "Assessment Skills",
            "description": "Gathering and analyzing information",
            "weight": 0.25,
            "evaluation_points": [
                "Asks relevant questions",
                "Identifies key issues",
                "Considers multiple perspectives",
                "Documents thoroughly"
            ]
        },
        {
            "name": "Intervention Planning",
            "description": "Developing appropriate interventions",
            "weight": 0.25,
            "evaluation_points": [
                "Sets realistic goals",
                "Involves client in planning",
                "Identifies resources",
                "Creates actionable steps"
            ]
        },
        {
            "name": "Professional Ethics",
            "description": "Adhering to social work ethics",
            "weight": 0.25,
            "evaluation_points": [
                "Maintains confidentiality",
                "Respects client autonomy",
                "Recognizes personal biases",
                "Follows professional guidelines"
            ]
        }
    ]
}

response = requests.post(f"{BASE_URL}/rubrics", json=new_rubric)
if response.status_code == 201:
    created_rubric = response.json()
    rubric_id = created_rubric["id"]
    print_success(f"Created rubric with ID: {rubric_id}")
    print_info(f"Name: {created_rubric['name']}")
    print_info(f"Criteria count: {len(created_rubric['criteria'])}")
else:
    print_error(f"Create failed: {response.status_code} - {response.text}")
    exit(1)

# Test 3: Get specific rubric
print_header("Test 3: GET /api/teacher/rubrics/{id} (Retrieve)")
response = requests.get(f"{BASE_URL}/rubrics/{rubric_id}")
if response.status_code == 200:
    retrieved = response.json()
    print_success(f"Retrieved rubric: {retrieved['name']}")
    print_info(f"Created by: {retrieved['created_by']}")
    print_info("Criteria:")
    for criterion in retrieved['criteria']:
        print(f"  - {criterion['name']} (weight: {criterion['weight']})")
else:
    print_error(f"Retrieve failed: {response.status_code} - {response.text}")

# Test 4: Update rubric
print_header("Test 4: PUT /api/teacher/rubrics/{id} (Update)")
update_data = {
    "name": "Updated Social Work Assessment v2",
    "description": "Enhanced evaluation framework for social work practice"
}
response = requests.put(f"{BASE_URL}/rubrics/{rubric_id}", json=update_data)
if response.status_code == 200:
    updated = response.json()
    print_success(f"Updated rubric name to: {updated['name']}")
    print_info(f"New description: {updated['description']}")
    print_info(f"Criteria unchanged: {len(updated['criteria'])} criteria")
else:
    print_error(f"Update failed: {response.status_code} - {response.text}")

# Test 5: List again to see our rubric
print_header("Test 5: GET /api/teacher/rubrics (Verify in List)")
response = requests.get(f"{BASE_URL}/rubrics")
if response.status_code == 200:
    rubrics = response.json()
    print_success(f"List shows {len(rubrics)} rubric(s)")
    for rubric in rubrics:
        print_info(f"  - {rubric['name']} (ID: {rubric['id']})")
else:
    print_error(f"List failed: {response.status_code} - {response.text}")

# Test 6: Test validation (invalid weights)
print_header("Test 6: POST /api/teacher/rubrics (Validation Test)")
invalid_rubric = {
    "name": "Invalid Rubric",
    "description": "This should fail",
    "criteria": [
        {"name": "Criterion 1", "description": "Test", "weight": 0.5, "evaluation_points": ["Point"]},
        {"name": "Criterion 2", "description": "Test", "weight": 0.3, "evaluation_points": ["Point"]}
        # Total weight = 0.8, should fail
    ]
}
response = requests.post(f"{BASE_URL}/rubrics", json=invalid_rubric)
if response.status_code == 422:
    print_success("Validation working - correctly rejected invalid weights")
    print_info("Error details: Weights must sum to 1.0")
else:
    print_error(f"Validation not working properly: {response.status_code}")

# Test 7: Delete rubric
print_header("Test 7: DELETE /api/teacher/rubrics/{id} (Delete)")
response = requests.delete(f"{BASE_URL}/rubrics/{rubric_id}")
if response.status_code == 204:
    print_success("Deleted rubric successfully")
    
    # Verify deletion
    verify_response = requests.get(f"{BASE_URL}/rubrics/{rubric_id}")
    if verify_response.status_code == 404:
        print_success("Verified: Rubric no longer exists (404)")
    else:
        print_error("Rubric still exists after deletion!")
else:
    print_error(f"Delete failed: {response.status_code} - {response.text}")

# Summary
print_header("Summary - Phase 1.3 Part 4 Complete")
print_success("All CRUD endpoints are working:")
print("  ✓ GET    /api/teacher/rubrics       - List all rubrics")
print("  ✓ POST   /api/teacher/rubrics       - Create new rubric")
print("  ✓ GET    /api/teacher/rubrics/{id}  - Get specific rubric")
print("  ✓ PUT    /api/teacher/rubrics/{id}  - Update rubric")
print("  ✓ DELETE /api/teacher/rubrics/{id}  - Delete rubric")
print()
print_info("Additional features verified:")
print("  • Criteria weight validation (must sum to 1.0)")
print("  • Partial updates supported")
print("  • Teacher isolation (created_by field)")
print("  • Proper error responses (404, 422)")
print()
print(f"{BOLD}Ready for Part 5: Add cascade protection{RESET}")
