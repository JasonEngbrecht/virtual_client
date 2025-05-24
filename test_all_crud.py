"""
Test all CRUD endpoints for teacher/clients
Run this after starting the server to verify all endpoints work together
"""

import requests
import json

def test_all_crud_endpoints():
    """Test all CRUD endpoints in sequence"""
    print("=" * 60)
    print("Testing ALL Teacher Client CRUD Endpoints")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/teacher/clients"
    
    try:
        # 1. LIST (GET /clients)
        print("\n1. Testing LIST (GET /clients)")
        response = requests.get(base_url)
        print(f"Status Code: {response.status_code}")
        initial_count = len(response.json()) if response.status_code == 200 else 0
        print(f"Initial client count: {initial_count}")
        
        # 2. CREATE (POST /clients)
        print("\n2. Testing CREATE (POST /clients)")
        new_client_data = {
            "name": "CRUD Test Client",
            "age": 25,
            "race": "Asian",
            "gender": "Female",
            "socioeconomic_status": "Low income",
            "issues": ["anxiety", "unemployment"],
            "background_story": "Test client for CRUD operations",
            "personality_traits": ["cooperative", "anxious"],
            "communication_style": "indirect"
        }
        response = requests.post(base_url, json=new_client_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            created_client = response.json()
            client_id = created_client["id"]
            print(f"✓ Created client with ID: {client_id}")
        else:
            print(f"✗ Failed to create client: {response.text}")
            return
            
        # 3. RETRIEVE (GET /clients/{id})
        print(f"\n3. Testing RETRIEVE (GET /clients/{client_id})")
        response = requests.get(f"{base_url}/{client_id}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ Retrieved client: {response.json()['name']}")
        else:
            print(f"✗ Failed to retrieve client")
            
        # 4. UPDATE (PUT /clients/{id})
        print(f"\n4. Testing UPDATE (PUT /clients/{client_id})")
        update_data = {
            "age": 26,
            "issues": ["anxiety", "unemployment", "housing_insecurity"]
        }
        response = requests.put(f"{base_url}/{client_id}", json=update_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            updated = response.json()
            print(f"✓ Updated age to {updated['age']} and issues to {updated['issues']}")
        else:
            print(f"✗ Failed to update client")
            
        # 5. LIST AGAIN (verify count increased)
        print("\n5. Testing LIST again (verify count)")
        response = requests.get(base_url)
        new_count = len(response.json()) if response.status_code == 200 else 0
        print(f"Client count after creation: {new_count} (was {initial_count})")
        if new_count == initial_count + 1:
            print("✓ Count correctly increased by 1")
        else:
            print("✗ Count did not increase as expected")
            
        # 6. DELETE (DELETE /clients/{id})
        print(f"\n6. Testing DELETE (DELETE /clients/{client_id})")
        response = requests.delete(f"{base_url}/{client_id}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 204:
            print("✓ Client deleted successfully")
        else:
            print(f"✗ Failed to delete client")
            
        # 7. VERIFY DELETION (GET should return 404)
        print("\n7. Verifying deletion")
        response = requests.get(f"{base_url}/{client_id}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 404:
            print("✓ Client correctly not found after deletion")
        else:
            print("✗ Client still exists after deletion")
            
        # 8. FINAL COUNT
        print("\n8. Final client count")
        response = requests.get(base_url)
        final_count = len(response.json()) if response.status_code == 200 else 0
        print(f"Final count: {final_count} (should equal initial count of {initial_count})")
        if final_count == initial_count:
            print("✓ Count correctly returned to initial value")
        else:
            print("✗ Count mismatch")
            
        print("\n" + "=" * 60)
        print("✅ ALL CRUD OPERATIONS COMPLETED!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to server")
        print("Make sure the server is running with: python start_server.py")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    test_all_crud_endpoints()
