"""
Test script for GET /api/teacher/rubrics/{id} endpoint
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/teacher"

print("Test 1: Create a rubric first...")
# Create a rubric to test retrieval
rubric_data = {
    "name": "Sample Assessment Rubric",
    "description": "A comprehensive rubric for testing retrieval",
    "criteria": [
        {
            "name": "Communication Skills",
            "description": "Evaluates verbal and non-verbal communication",
            "weight": 0.4,
            "evaluation_points": [
                "Clear articulation",
                "Active listening",
                "Appropriate tone",
                "Body language"
            ]
        },
        {
            "name": "Problem Solving",
            "description": "Assesses analytical and problem-solving abilities",
            "weight": 0.35,
            "evaluation_points": [
                "Identifies key issues",
                "Develops solutions",
                "Considers alternatives"
            ]
        },
        {
            "name": "Professionalism",
            "description": "Maintains professional standards",
            "weight": 0.25,
            "evaluation_points": [
                "Punctuality",
                "Appropriate attire",
                "Ethical behavior"
            ]
        }
    ]
}

response = requests.post(f"{BASE_URL}/rubrics", json=rubric_data)
if response.status_code == 201:
    created_rubric = response.json()
    rubric_id = created_rubric["id"]
    print(f"✓ Created rubric with ID: {rubric_id}")
else:
    print(f"✗ Failed to create rubric: {response.json()}")
    exit(1)

print("\n" + "="*50 + "\n")

# Test 2: Retrieve the created rubric
print(f"Test 2: Retrieving rubric by ID...")
response = requests.get(f"{BASE_URL}/rubrics/{rubric_id}")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    retrieved_rubric = response.json()
    print(f"✓ Successfully retrieved rubric:")
    print(f"  - Name: {retrieved_rubric['name']}")
    print(f"  - Description: {retrieved_rubric['description']}")
    print(f"  - Number of criteria: {len(retrieved_rubric['criteria'])}")
    print(f"  - Created by: {retrieved_rubric['created_by']}")
    
    # Display criteria details
    print("\n  Criteria:")
    for criterion in retrieved_rubric['criteria']:
        print(f"    - {criterion['name']} (weight: {criterion['weight']})")
        print(f"      Points: {', '.join(criterion['evaluation_points'][:2])}...")
else:
    print(f"✗ Error: {response.json()}")

print("\n" + "="*50 + "\n")

# Test 3: Try to retrieve non-existent rubric
print("Test 3: Attempting to retrieve non-existent rubric...")
fake_id = "non-existent-rubric-12345"
response = requests.get(f"{BASE_URL}/rubrics/{fake_id}")
print(f"Status: {response.status_code}")
if response.status_code == 404:
    print(f"✓ Correctly returned 404 Not Found")
    print(f"  Error: {response.json()['detail']}")
else:
    print(f"✗ Unexpected response: {response.json()}")

print("\n" + "="*50 + "\n")

# Test 4: Verify the rubric appears in the list
print("Test 4: Verifying rubric appears in list...")
response = requests.get(f"{BASE_URL}/rubrics")
if response.status_code == 200:
    rubrics = response.json()
    rubric_ids = [r['id'] for r in rubrics]
    if rubric_id in rubric_ids:
        print(f"✓ Rubric found in list (total rubrics: {len(rubrics)})")
    else:
        print(f"✗ Rubric not found in list!")
else:
    print(f"✗ Failed to get rubrics list: {response.json()}")

print("\n" + "="*50 + "\n")
print("All tests completed!")
