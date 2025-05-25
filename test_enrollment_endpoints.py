"""
Test enrollment endpoints manually
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/teacher"

# First, let's create a test section
section_data = {
    "name": "Test Enrollment Section",
    "description": "Section for testing enrollment endpoints",
    "course_code": "TEST101",
    "term": "Spring 2025",
    "is_active": True
}

print("Creating test section...")
response = requests.post(f"{BASE_URL}/sections", json=section_data)
if response.status_code == 201:
    section = response.json()
    section_id = section["id"]
    print(f"✓ Created section: {section_id}")
else:
    print(f"✗ Failed to create section: {response.status_code} - {response.text}")
    exit(1)

# Test 1: Get empty roster
print("\nTest 1: Get empty roster")
response = requests.get(f"{BASE_URL}/sections/{section_id}/roster")
if response.status_code == 200:
    roster = response.json()
    print(f"✓ Got roster: {len(roster)} students (should be 0)")
    assert len(roster) == 0
else:
    print(f"✗ Failed: {response.status_code} - {response.text}")

# Test 2: Enroll a student
print("\nTest 2: Enroll a student")
enrollment_data = {
    "student_id": "student-test-001",
    "role": "student"
}
response = requests.post(f"{BASE_URL}/sections/{section_id}/enroll", json=enrollment_data)
if response.status_code == 201:
    enrollment = response.json()
    print(f"✓ Enrolled student: {enrollment['student_id']}")
    print(f"  Enrollment ID: {enrollment['id']}")
    print(f"  Is Active: {enrollment['is_active']}")
else:
    print(f"✗ Failed: {response.status_code} - {response.text}")

# Test 3: Get roster with one student
print("\nTest 3: Get roster with one student")
response = requests.get(f"{BASE_URL}/sections/{section_id}/roster")
if response.status_code == 200:
    roster = response.json()
    print(f"✓ Got roster: {len(roster)} students (should be 1)")
    assert len(roster) == 1
    assert roster[0]["student_id"] == "student-test-001"
else:
    print(f"✗ Failed: {response.status_code} - {response.text}")

# Test 4: Enroll same student again (should succeed without creating duplicate)
print("\nTest 4: Enroll same student again")
response = requests.post(f"{BASE_URL}/sections/{section_id}/enroll", json=enrollment_data)
if response.status_code == 201:
    enrollment2 = response.json()
    print(f"✓ Re-enrollment handled correctly")
    print(f"  Same enrollment ID: {enrollment['id'] == enrollment2['id']}")
else:
    print(f"✗ Failed: {response.status_code} - {response.text}")

# Test 5: Enroll another student
print("\nTest 5: Enroll another student")
enrollment_data2 = {
    "student_id": "student-test-002",
    "role": "student"
}
response = requests.post(f"{BASE_URL}/sections/{section_id}/enroll", json=enrollment_data2)
if response.status_code == 201:
    print(f"✓ Enrolled second student")
else:
    print(f"✗ Failed: {response.status_code} - {response.text}")

# Test 6: Get roster with two students
print("\nTest 6: Get roster with two students")
response = requests.get(f"{BASE_URL}/sections/{section_id}/roster")
if response.status_code == 200:
    roster = response.json()
    print(f"✓ Got roster: {len(roster)} students (should be 2)")
    assert len(roster) == 2
else:
    print(f"✗ Failed: {response.status_code} - {response.text}")

# Test 7: Unenroll first student
print("\nTest 7: Unenroll first student")
response = requests.delete(f"{BASE_URL}/sections/{section_id}/enroll/student-test-001")
if response.status_code == 204:
    print(f"✓ Successfully unenrolled student")
else:
    print(f"✗ Failed: {response.status_code} - {response.text}")

# Test 8: Get roster after unenrollment
print("\nTest 8: Get roster after unenrollment")
response = requests.get(f"{BASE_URL}/sections/{section_id}/roster")
if response.status_code == 200:
    roster = response.json()
    print(f"✓ Got roster: {len(roster)} students (should be 1)")
    assert len(roster) == 1
    assert roster[0]["student_id"] == "student-test-002"
else:
    print(f"✗ Failed: {response.status_code} - {response.text}")

# Test 9: Try to unenroll non-enrolled student
print("\nTest 9: Try to unenroll non-enrolled student")
response = requests.delete(f"{BASE_URL}/sections/{section_id}/enroll/student-not-exists")
if response.status_code == 404:
    error = response.json()
    print(f"✓ Correctly rejected: {error['detail']}")
else:
    print(f"✗ Failed: Expected 404, got {response.status_code}")

# Test 10: Re-enroll previously unenrolled student
print("\nTest 10: Re-enroll previously unenrolled student")
enrollment_data3 = {
    "student_id": "student-test-001",
    "role": "student"
}
response = requests.post(f"{BASE_URL}/sections/{section_id}/enroll", json=enrollment_data3)
if response.status_code == 201:
    print(f"✓ Successfully re-enrolled student (reactivation)")
else:
    print(f"✗ Failed: {response.status_code} - {response.text}")

# Clean up
print("\nCleaning up...")
response = requests.delete(f"{BASE_URL}/sections/{section_id}")
if response.status_code == 204:
    print("✓ Deleted test section")
else:
    print(f"✗ Failed to delete section: {response.status_code}")

print("\n✅ All enrollment endpoint tests completed!")
