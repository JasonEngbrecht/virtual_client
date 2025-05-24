"""
Test POST /api/teacher/clients endpoint
Run this after starting the server to verify the endpoint works
"""

import requests
import json

def test_create_client():
    """Test the POST /api/teacher/clients endpoint"""
    print("=" * 60)
    print("Testing POST /api/teacher/clients")
    print("=" * 60)
    
    url = "http://localhost:8000/api/teacher/clients"
    
    # Test client data
    client_data = {
        "name": "Jane Smith",
        "age": 42,
        "race": "African American",
        "gender": "Female",
        "socioeconomic_status": "Middle class",
        "issues": ["mental_health", "family_conflict"],
        "background_story": "Jane is dealing with depression and conflicts with her teenage daughter...",
        "personality_traits": ["withdrawn", "emotional"],
        "communication_style": "indirect"
    }
    
    try:
        print("\nSending POST request with client data:")
        print(json.dumps(client_data, indent=2))
        
        response = requests.post(url, json=client_data)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 201:
            created_client = response.json()
            print("\nClient created successfully!")
            print(json.dumps(created_client, indent=2))
        else:
            print(f"\nError: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to server")
        print("Make sure the server is running with: python start_server.py")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    test_create_client()
