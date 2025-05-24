"""
Test DELETE /api/teacher/clients/{id} endpoint
Run this after starting the server to verify the endpoint works
"""

import requests
import json

def test_delete_client():
    """Test the DELETE /api/teacher/clients/{id} endpoint"""
    print("=" * 60)
    print("Testing DELETE /api/teacher/clients/{id}")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/teacher/clients"
    
    try:
        # First, create a test client to delete
        print("\nCreating a test client to delete...")
        test_client_data = {
            "name": "Test Client for Deletion",
            "age": 30,
            "issues": ["test_issue"],
            "personality_traits": ["test_trait"],
            "communication_style": "direct"
        }
        
        response = requests.post(base_url, json=test_client_data)
        if response.status_code != 201:
            print("Error: Could not create test client")
            print(f"Status: {response.status_code}, Response: {response.text}")
            return
            
        created_client = response.json()
        client_id = created_client["id"]
        client_name = created_client["name"]
        print(f"Created test client: {client_name} (ID: {client_id})")
        
        # Verify the client exists
        print("\n" + "-" * 40)
        print("Test 1: Verify client exists before deletion")
        get_url = f"{base_url}/{client_id}"
        response = requests.get(get_url)
        print(f"GET Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✓ Client exists")
        else:
            print("✗ Client should exist but wasn't found")
            return
            
        # Delete the client
        print("\n" + "-" * 40)
        print("Test 2: Delete the client")
        delete_url = f"{base_url}/{client_id}"
        response = requests.delete(delete_url)
        print(f"DELETE Status Code: {response.status_code}")
        
        if response.status_code == 204:
            print("✓ Client deleted successfully (204 No Content)")
        else:
            print(f"✗ Expected 204, got {response.status_code}")
            print(f"Response: {response.text}")
            
        # Verify the client is gone
        print("\n" + "-" * 40)
        print("Test 3: Verify client no longer exists")
        response = requests.get(get_url)
        print(f"GET Status Code: {response.status_code}")
        if response.status_code == 404:
            print("✓ Client correctly not found after deletion")
        else:
            print("✗ Client still exists after deletion!")
            
        # Test deleting non-existent client
        print("\n" + "-" * 40)
        print("Test 4: Delete non-existent client")
        fake_id = "00000000-0000-0000-0000-000000000000"
        fake_url = f"{base_url}/{fake_id}"
        response = requests.delete(fake_url)
        print(f"DELETE Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 404:
            print("✓ Correctly returned 404 for non-existent client")
        else:
            print("✗ Should have returned 404 for non-existent client")
            
        # List all clients to confirm deletion
        print("\n" + "-" * 40)
        print("Test 5: List all clients to confirm deletion")
        response = requests.get(base_url)
        if response.status_code == 200:
            clients = response.json()
            deleted_client_found = any(c["id"] == client_id for c in clients)
            if not deleted_client_found:
                print("✓ Deleted client not in list")
            else:
                print("✗ Deleted client still appears in list!")
            print(f"Total clients remaining: {len(clients)}")
            
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to server")
        print("Make sure the server is running with: python start_server.py")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    test_delete_client()
