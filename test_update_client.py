"""
Test PUT /api/teacher/clients/{id} endpoint
Run this after starting the server to verify the endpoint works
"""

import requests
import json

def test_update_client():
    """Test the PUT /api/teacher/clients/{id} endpoint"""
    print("=" * 60)
    print("Testing PUT /api/teacher/clients/{id}")
    print("=" * 60)
    
    # First, get the list of clients to get a valid ID
    list_url = "http://localhost:8000/api/teacher/clients"
    
    try:
        # Get list of clients
        response = requests.get(list_url)
        if response.status_code != 200:
            print("Error: Could not get client list")
            print(f"Status: {response.status_code}, Response: {response.text}")
            return
            
        clients = response.json()
        if not clients:
            print("No clients found. Please create some clients first.")
            print("Run: python add_test_client.py")
            return
            
        # Test with the first client's ID
        client_id = clients[0]["id"]
        original_name = clients[0]["name"]
        original_age = clients[0]["age"]
        print(f"\nTesting with client ID: {client_id}")
        print(f"Original name: {original_name}, age: {original_age}")
        
        # Test partial update (only updating some fields)
        print("\n" + "-" * 40)
        print("Test 1: Partial update (age and issues)")
        update_url = f"http://localhost:8000/api/teacher/clients/{client_id}"
        update_data = {
            "age": original_age + 1,
            "issues": ["mental_health", "unemployment", "housing_insecurity"]
        }
        
        response = requests.put(update_url, json=update_data)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            updated_client = response.json()
            print("\nClient updated successfully!")
            print(f"New age: {updated_client['age']} (was {original_age})")
            print(f"New issues: {updated_client['issues']}")
            print(f"Name unchanged: {updated_client['name']}")
        else:
            print(f"\nError: {response.text}")
            
        # Test updating all fields
        print("\n" + "-" * 40)
        print("Test 2: Full update")
        full_update_data = {
            "name": original_name + " (Updated)",
            "age": 45,
            "race": "Hispanic",
            "gender": "Non-binary",
            "socioeconomic_status": "Middle class",
            "issues": ["chronic_illness", "elder_care"],
            "background_story": "Updated background story...",
            "personality_traits": ["optimistic", "talkative"],
            "communication_style": "verbose"
        }
        
        response = requests.put(update_url, json=full_update_data)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            updated_client = response.json()
            print("\nClient fully updated!")
            print(json.dumps(updated_client, indent=2))
        else:
            print(f"\nError: {response.text}")
            
        # Test with non-existent ID
        print("\n" + "-" * 40)
        print("Test 3: Update non-existent client")
        fake_id = "00000000-0000-0000-0000-000000000000"
        fake_url = f"http://localhost:8000/api/teacher/clients/{fake_id}"
        response = requests.put(fake_url, json={"age": 50})
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 404:
            print("✓ Correctly returned 404 for non-existent client")
        else:
            print("✗ Should have returned 404 for non-existent client")
            
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to server")
        print("Make sure the server is running with: python start_server.py")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    test_update_client()
