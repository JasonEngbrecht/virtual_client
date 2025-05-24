"""
Test script for PUT /api/teacher/rubrics/{id} endpoint
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/teacher"

# Helper function to create a rubric
def create_test_rubric():
    rubric_data = {
        "name": "Initial Assessment Rubric",
        "description": "This rubric will be updated",
        "criteria": [
            {
                "name": "Listening Skills",
                "description": "Active listening and comprehension",
                "weight": 0.5,
                "evaluation_points": [
                    "Maintains attention",
                    "Asks relevant questions",
                    "Summarizes accurately"
                ]
            },
            {
                "name": "Response Quality",
                "description": "Quality of responses to client",
                "weight": 0.5,
                "evaluation_points": [
                    "Thoughtful responses",
                    "Evidence-based suggestions",
                    "Client-centered approach"
                ]
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/rubrics", json=rubric_data)
    if response.status_code == 201:
        return response.json()["id"]
    else:
        print(f"Failed to create rubric: {response.json()}")
        return None

print("Creating a test rubric...")
rubric_id = create_test_rubric()
if not rubric_id:
    exit(1)
print(f"✓ Created rubric with ID: {rubric_id}")

print("\n" + "="*50 + "\n")

# Test 1: Partial update - just name
print("Test 1: Partial update - changing only the name...")
update_data = {
    "name": "Updated Assessment Rubric v2"
}

response = requests.put(f"{BASE_URL}/rubrics/{rubric_id}", json=update_data)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    updated = response.json()
    print(f"✓ Successfully updated rubric")
    print(f"  - New name: {updated['name']}")
    print(f"  - Description (unchanged): {updated['description']}")
    print(f"  - Criteria count (unchanged): {len(updated['criteria'])}")
else:
    print(f"✗ Error: {response.json()}")

print("\n" + "="*50 + "\n")

# Test 2: Update description
print("Test 2: Updating description...")
update_data = {
    "description": "This rubric has been updated to better assess student performance"
}

response = requests.put(f"{BASE_URL}/rubrics/{rubric_id}", json=update_data)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    print(f"✓ Description updated successfully")
else:
    print(f"✗ Error: {response.json()}")

print("\n" + "="*50 + "\n")

# Test 3: Update criteria completely
print("Test 3: Replacing all criteria...")
update_data = {
    "criteria": [
        {
            "name": "Empathy & Understanding",
            "description": "Demonstrates empathy and understanding",
            "weight": 0.3,
            "evaluation_points": [
                "Validates feelings",
                "Shows compassion",
                "Acknowledges concerns"
            ]
        },
        {
            "name": "Communication",
            "description": "Clear and effective communication",
            "weight": 0.3,
            "evaluation_points": [
                "Clear language",
                "Appropriate tone",
                "Good pacing"
            ]
        },
        {
            "name": "Problem Solving",
            "description": "Helps identify solutions",
            "weight": 0.4,
            "evaluation_points": [
                "Explores options",
                "Collaborative approach",
                "Realistic solutions"
            ]
        }
    ]
}

response = requests.put(f"{BASE_URL}/rubrics/{rubric_id}", json=update_data)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    updated = response.json()
    print(f"✓ Criteria updated successfully")
    print(f"  - New criteria count: {len(updated['criteria'])}")
    for i, criterion in enumerate(updated['criteria']):
        print(f"  - Criterion {i+1}: {criterion['name']} (weight: {criterion['weight']})")
else:
    print(f"✗ Error: {response.json()}")

print("\n" + "="*50 + "\n")

# Test 4: Try invalid weight update
print("Test 4: Attempting invalid criteria update (weights don't sum to 1.0)...")
invalid_update = {
    "criteria": [
        {
            "name": "Criterion 1",
            "description": "First",
            "weight": 0.6,
            "evaluation_points": ["Point 1"]
        },
        {
            "name": "Criterion 2",
            "description": "Second",
            "weight": 0.5,  # Total = 1.1, not 1.0
            "evaluation_points": ["Point 2"]
        }
    ]
}

response = requests.put(f"{BASE_URL}/rubrics/{rubric_id}", json=invalid_update)
print(f"Status: {response.status_code}")
if response.status_code == 422:
    print(f"✓ Correctly rejected invalid weights")
    print(f"  Error details: {response.json()}")
else:
    print(f"✗ Unexpected response: {response.json()}")

print("\n" + "="*50 + "\n")

# Test 5: Empty update attempt
print("Test 5: Attempting empty update...")
response = requests.put(f"{BASE_URL}/rubrics/{rubric_id}", json={})
print(f"Status: {response.status_code}")
if response.status_code == 400:
    print(f"✓ Correctly rejected empty update")
    print(f"  Error: {response.json()['detail']}")
else:
    print(f"✗ Unexpected response: {response.json()}")

print("\n" + "="*50 + "\n")

# Test 6: Non-existent rubric
print("Test 6: Attempting to update non-existent rubric...")
response = requests.put(f"{BASE_URL}/rubrics/fake-id-12345", json={"name": "Won't work"})
print(f"Status: {response.status_code}")
if response.status_code == 404:
    print(f"✓ Correctly returned 404 Not Found")
    print(f"  Error: {response.json()['detail']}")
else:
    print(f"✗ Unexpected response: {response.json()}")

print("\n" + "="*50 + "\n")

# Final verification
print("Final verification - Getting the updated rubric...")
response = requests.get(f"{BASE_URL}/rubrics/{rubric_id}")
if response.status_code == 200:
    final_rubric = response.json()
    print(f"✓ Final rubric state:")
    print(f"  - Name: {final_rubric['name']}")
    print(f"  - Description: {final_rubric['description']}")
    print(f"  - Criteria count: {len(final_rubric['criteria'])}")
    print(f"  - Total weight: {sum(c['weight'] for c in final_rubric['criteria'])}")

print("\n" + "="*50 + "\n")
print("All tests completed!")
