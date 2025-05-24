"""
Test GET /api/teacher/clients/{id} endpoint
Run this after starting the server to verify the endpoint works
"""

import requests
import json

def test_get_client_by_id():
    """Test the GET /api/teacher/clients/{id} endpoint"""
    print("=" * 60)
    print("Testing GET /api/teacher/clients/{id}")
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
        client_name = clients[0]["name"]
        print(f"\nTesting with client ID: {client_id} (Name: {client_name})")
        
        # Test successful retrieval
        get_url = f"http://localhost:8000/api/teacher/clients/{client_id}"
        response = requests.get(get_url)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            client = response.json()
            print("\nClient retrieved successfully!")
            print(json.dumps(client, indent=2))
        else:
            print(f"\nError: {response.text}")
            
        # Test with non-existent ID
        print("\n" + "-" * 40)
        print("Testing with non-existent ID...")
        fake_id = "00000000-0000-0000-0000-000000000000"
        fake_url = f"http://localhost:8000/api/teacher/clients/{fake_id}"
        response = requests.get(fake_url)
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
    test_get_client_by_id()
