"""
Test GET /api/teacher/clients endpoint
Run this after starting the server to verify the endpoint works
"""

import requests
import json

def test_get_clients():
    """Test the GET /api/teacher/clients endpoint"""
    print("=" * 60)
    print("Testing GET /api/teacher/clients")
    print("=" * 60)
    
    url = "http://localhost:8000/api/teacher/clients"
    
    try:
        response = requests.get(url)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            clients = response.json()
            print(f"\nNumber of clients found: {len(clients)}")
            
            if clients:
                print("\nFirst client:")
                print(json.dumps(clients[0], indent=2))
            else:
                print("\nNo clients found for teacher-123")
                print("This is expected if no test data was created for this teacher_id")
        else:
            print(f"\nError: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to server")
        print("Make sure the server is running with: python start_server.py")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    test_get_clients()
