"""
Test script for DELETE /api/teacher/rubrics/{id} endpoint
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/teacher"

# Helper function to create test rubrics
def create_test_rubrics():
    rubrics = []
    
    for i in range(3):
        rubric_data = {
            "name": f"Test Rubric {i+1}",
            "description": f"Rubric #{i+1} for deletion testing",
            "criteria": [
                {
                    "name": f"Criterion A",
                    "description": f"First criterion for rubric {i+1}",
                    "weight": 0.6,
                    "evaluation_points": ["Point 1", "Point 2", "Point 3"]
                },
                {
                    "name": f"Criterion B",
                    "description": f"Second criterion for rubric {i+1}",
                    "weight": 0.4,
                    "evaluation_points": ["Point 4", "Point 5"]
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/rubrics", json=rubric_data)
        if response.status_code == 201:
            rubric = response.json()
            rubrics.append({
                "id": rubric["id"],
                "name": rubric["name"]
            })
        else:
            print(f"Failed to create rubric: {response.json()}")
            
    return rubrics

print("Creating test rubrics...")
test_rubrics = create_test_rubrics()
print(f"✓ Created {len(test_rubrics)} test rubrics")
for rubric in test_rubrics:
    print(f"  - {rubric['name']} (ID: {rubric['id']})")

print("\n" + "="*50 + "\n")

# Test 1: Delete a rubric successfully
print("Test 1: Deleting first rubric...")
if test_rubrics:
    rubric_to_delete = test_rubrics[0]
    response = requests.delete(f"{BASE_URL}/rubrics/{rubric_to_delete['id']}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 204:
        print(f"✓ Successfully deleted '{rubric_to_delete['name']}'")
        print("  - Response has no content (as expected)")
        
        # Verify deletion by trying to retrieve it
        verify_response = requests.get(f"{BASE_URL}/rubrics/{rubric_to_delete['id']}")
        if verify_response.status_code == 404:
            print("  - Verified: Rubric no longer exists")
        else:
            print(f"  - Warning: Unexpected status when verifying deletion: {verify_response.status_code}")
    else:
        print(f"✗ Error: {response.json()}")

print("\n" + "="*50 + "\n")

# Test 2: Try to delete non-existent rubric
print("Test 2: Attempting to delete non-existent rubric...")
fake_id = "non-existent-rubric-99999"
response = requests.delete(f"{BASE_URL}/rubrics/{fake_id}")
print(f"Status: {response.status_code}")

if response.status_code == 404:
    print(f"✓ Correctly returned 404 Not Found")
    print(f"  Error: {response.json()['detail']}")
else:
    print(f"✗ Unexpected response: {response.json()}")

print("\n" + "="*50 + "\n")

# Test 3: Verify remaining rubrics in list
print("Test 3: Checking remaining rubrics...")
response = requests.get(f"{BASE_URL}/rubrics")
if response.status_code == 200:
    remaining_rubrics = response.json()
    print(f"✓ Found {len(remaining_rubrics)} rubrics remaining")
    
    # Should be 2 rubrics left (we deleted 1 of 3)
    if len(test_rubrics) > 0:
        deleted_id = test_rubrics[0]['id']
        remaining_ids = [r['id'] for r in remaining_rubrics]
        
        if deleted_id not in remaining_ids:
            print("  - Confirmed: Deleted rubric is not in the list")
        else:
            print("  - Error: Deleted rubric still appears in list!")
            
        # List remaining rubrics
        print("  Remaining rubrics:")
        for rubric in remaining_rubrics:
            print(f"    - {rubric['name']} (ID: {rubric['id']})")
else:
    print(f"✗ Failed to get rubrics list: {response.json()}")

print("\n" + "="*50 + "\n")

# Test 4: Delete all remaining rubrics
print("Test 4: Cleaning up - deleting all remaining rubrics...")
response = requests.get(f"{BASE_URL}/rubrics")
if response.status_code == 200:
    remaining = response.json()
    deleted_count = 0
    
    for rubric in remaining:
        delete_response = requests.delete(f"{BASE_URL}/rubrics/{rubric['id']}")
        if delete_response.status_code == 204:
            deleted_count += 1
            print(f"  ✓ Deleted: {rubric['name']}")
        else:
            print(f"  ✗ Failed to delete {rubric['name']}: {delete_response.status_code}")
    
    print(f"\n✓ Cleanup complete: Deleted {deleted_count} rubrics")
    
    # Final verification
    final_check = requests.get(f"{BASE_URL}/rubrics")
    if final_check.status_code == 200:
        final_count = len(final_check.json())
        if final_count == 0:
            print("  - Verified: No rubrics remaining")
        else:
            print(f"  - Warning: {final_count} rubrics still exist")

print("\n" + "="*50 + "\n")

# Test 5: Edge case - double deletion attempt
print("Test 5: Attempting to delete already-deleted rubric...")
if test_rubrics:
    already_deleted_id = test_rubrics[0]['id']
    response = requests.delete(f"{BASE_URL}/rubrics/{already_deleted_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 404:
        print("✓ Correctly returned 404 for already-deleted rubric")
        print(f"  Error: {response.json()['detail']}")
    else:
        print(f"✗ Unexpected response: {response.json()}")

print("\n" + "="*50 + "\n")
print("All tests completed!")
