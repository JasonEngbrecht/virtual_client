"""
Test script for POST /api/teacher/rubrics endpoint
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/teacher"

# Test case 1: Valid rubric with weights summing to 1.0
print("Test 1: Creating valid rubric...")
valid_rubric = {
    "name": "Empathy and Communication Assessment",
    "description": "Evaluates student's empathy and communication skills",
    "criteria": [
        {
            "name": "Active Listening",
            "description": "Demonstrates active listening skills",
            "weight": 0.3,
            "evaluation_points": [
                "Maintains eye contact",
                "Asks clarifying questions",
                "Paraphrases client statements"
            ]
        },
        {
            "name": "Empathy",
            "description": "Shows understanding and empathy",
            "weight": 0.4,
            "evaluation_points": [
                "Validates client feelings",
                "Uses empathetic language",
                "Shows emotional awareness"
            ]
        },
        {
            "name": "Professional Boundaries",
            "description": "Maintains appropriate boundaries",
            "weight": 0.3,
            "evaluation_points": [
                "Keeps focus on client",
                "Avoids personal disclosure",
                "Maintains professional tone"
            ]
        }
    ]
}

response = requests.post(f"{BASE_URL}/rubrics", json=valid_rubric)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    rubric_id = response.json()["id"]
    print(f"Success! Created rubric with ID: {rubric_id}")
    print(f"Rubric name: {response.json()['name']}")
else:
    print(f"Error: {response.json()}")

print("\n" + "="*50 + "\n")

# Test case 2: Invalid rubric with weights not summing to 1.0
print("Test 2: Creating invalid rubric (weights don't sum to 1.0)...")
invalid_rubric = {
    "name": "Invalid Weight Rubric",
    "description": "This should fail validation",
    "criteria": [
        {
            "name": "Criterion 1",
            "description": "First criterion",
            "weight": 0.5,
            "evaluation_points": ["Point 1"]
        },
        {
            "name": "Criterion 2",
            "description": "Second criterion",
            "weight": 0.3,  # Total = 0.8, not 1.0
            "evaluation_points": ["Point 2"]
        }
    ]
}

response = requests.post(f"{BASE_URL}/rubrics", json=invalid_rubric)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\n" + "="*50 + "\n")

# Test case 3: Empty criteria list
print("Test 3: Creating rubric with empty criteria...")
empty_criteria_rubric = {
    "name": "Empty Criteria Rubric",
    "description": "This should fail validation",
    "criteria": []
}

response = requests.post(f"{BASE_URL}/rubrics", json=empty_criteria_rubric)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\n" + "="*50 + "\n")

# Test case 4: Missing required fields
print("Test 4: Creating rubric with missing name...")
missing_name_rubric = {
    "description": "Missing name field",
    "criteria": [
        {
            "name": "Test",
            "description": "Test criterion",
            "weight": 1.0,
            "evaluation_points": ["Point 1"]
        }
    ]
}

response = requests.post(f"{BASE_URL}/rubrics", json=missing_name_rubric)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\n" + "="*50 + "\n")

# Get all rubrics to verify creation
print("Getting all rubrics to verify creation...")
response = requests.get(f"{BASE_URL}/rubrics")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    rubrics = response.json()
    print(f"Total rubrics: {len(rubrics)}")
    for rubric in rubrics:
        print(f"- {rubric['name']} (ID: {rubric['id']})")
