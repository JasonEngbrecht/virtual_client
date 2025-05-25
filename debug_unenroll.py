"""
Debug the unenrollment 500 error
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/teacher"

# Create a test section
section_data = {
    "name": "Debug Unenroll Section",
    "description": "Testing unenrollment error",
    "course_code": "DEBUG101",
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
    print(f"✗ Failed to create section: {response.status_code}")
    exit(1)

# Enroll a student
print("\nEnrolling student...")
enrollment_data = {
    "student_id": "debug-student-001",
    "role": "student"
}
response = requests.post(f"{BASE_URL}/sections/{section_id}/enroll", json=enrollment_data)
if response.status_code == 201:
    enrollment = response.json()
    print(f"✓ Enrolled student: {enrollment['student_id']}")
    print(f"  Enrollment ID: {enrollment['id']}")
else:
    print(f"✗ Failed to enroll: {response.status_code}")
    exit(1)

# Check roster before unenrollment
print("\nChecking roster before unenrollment...")
response = requests.get(f"{BASE_URL}/sections/{section_id}/roster")
if response.status_code == 200:
    roster = response.json()
    print(f"✓ Roster has {len(roster)} student(s)")
    for enrollment in roster:
        print(f"  - {enrollment['student_id']} (active: {enrollment['is_active']})")

# Try to unenroll with detailed error handling
print("\nAttempting to unenroll student...")
response = requests.delete(f"{BASE_URL}/sections/{section_id}/enroll/debug-student-001")
print(f"Response status: {response.status_code}")
print(f"Response headers: {dict(response.headers)}")
if response.status_code == 204:
    print("✓ Successfully unenrolled (204 No Content)")
    print(f"Response body: '{response.text}' (should be empty)")
elif response.status_code == 500:
    print("✗ Got 500 error")
    print(f"Response body: {response.text}")
    try:
        error_detail = response.json()
        print(f"Error detail: {json.dumps(error_detail, indent=2)}")
    except:
        print("Could not parse error as JSON")
else:
    print(f"✗ Unexpected status: {response.status_code}")
    print(f"Response: {response.text}")

# Check roster after unenrollment attempt
print("\nChecking roster after unenrollment attempt...")
response = requests.get(f"{BASE_URL}/sections/{section_id}/roster")
if response.status_code == 200:
    roster = response.json()
    print(f"✓ Roster now has {len(roster)} student(s)")
    if len(roster) == 0:
        print("  ✓ Student was successfully unenrolled despite the error!")
    for enrollment in roster:
        print(f"  - {enrollment['student_id']} (active: {enrollment['is_active']})")

# Clean up
print("\nCleaning up...")
response = requests.delete(f"{BASE_URL}/sections/{section_id}")
if response.status_code == 204:
    print("✓ Deleted test section")

print("\nDebug complete!")
