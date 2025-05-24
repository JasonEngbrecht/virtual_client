"""
Test script to verify authentication dependency is working
Run from project root: python scripts/test_auth_dependency.py
"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000/api/teacher"

def test_auth_dependency():
    """Test that all endpoints work with the authentication dependency"""
    
    print("Testing Authentication Dependency Implementation")
    print("=" * 50)
    
    # Test 1: List clients (should work with mock auth)
    print("\n1. Testing GET /clients...")
    response = requests.get(f"{BASE_URL}/clients")
    if response.status_code == 200:
        print("✓ List clients working with auth dependency")
        clients = response.json()
        print(f"  Found {len(clients)} clients")
    else:
        print(f"✗ Error: {response.status_code}")
        
    # Test 2: Create a client (should work with mock auth)
    print("\n2. Testing POST /clients...")
    test_client = {
        "name": f"Auth Test Client {datetime.now().strftime('%H:%M:%S')}",
        "age": 30,
        "gender": "female",
        "race": "Asian",
        "socioeconomic_status": "middle_class",
        "issues": ["anxiety", "work_stress"],
        "background_story": "Testing authentication dependency",
        "personality_traits": ["friendly", "cooperative"],
        "communication_style": "direct"
    }
    
    response = requests.post(
        f"{BASE_URL}/clients",
        json=test_client,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        print("✓ Create client working with auth dependency")
        created_client = response.json()
        client_id = created_client["id"]
        print(f"  Created client ID: {client_id}")
        print(f"  Created by: {created_client['created_by']}")
        
        # Test 3: Get specific client
        print("\n3. Testing GET /clients/{id}...")
        response = requests.get(f"{BASE_URL}/clients/{client_id}")
        if response.status_code == 200:
            print("✓ Get specific client working with auth dependency")
        else:
            print(f"✗ Error: {response.status_code}")
            
        # Test 4: Update client
        print("\n4. Testing PUT /clients/{id}...")
        update_data = {
            "age": 31,
            "issues": ["anxiety", "work_stress", "relationship_issues"]
        }
        response = requests.put(
            f"{BASE_URL}/clients/{client_id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✓ Update client working with auth dependency")
            updated = response.json()
            print(f"  Updated age: {updated['age']}")
            print(f"  Issues: {updated['issues']}")
        else:
            print(f"✗ Error: {response.status_code}")
            
        # Test 5: Delete client
        print("\n5. Testing DELETE /clients/{id}...")
        response = requests.delete(f"{BASE_URL}/clients/{client_id}")
        if response.status_code == 204:
            print("✓ Delete client working with auth dependency")
        else:
            print(f"✗ Error: {response.status_code}")
            
    else:
        print(f"✗ Error creating client: {response.status_code}")
        print(f"  Response: {response.text}")
    
    print("\n" + "=" * 50)
    print("Authentication dependency test complete!")
    print("\nNOTE: All endpoints are using the mock get_current_teacher()")
    print("which returns 'teacher-123' for testing purposes.")


if __name__ == "__main__":
    print("\nMake sure the server is running:")
    print("  python -m uvicorn backend.app:app --reload")
    print("\nPress Enter to continue with tests...")
    input()
    
    try:
        test_auth_dependency()
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the server.")
        print("  Please make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
