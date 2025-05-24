"""
Quick test to verify the API server is working after removing the custom validation handler
"""

import requests
import sys

def test_server():
    """Test that the server is running and endpoints work"""
    print("Testing API server...")
    
    try:
        # Test health check
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✓ Server is running")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
            
        # Test teacher router
        response = requests.get("http://localhost:8000/api/teacher/test")
        if response.status_code == 200:
            print("✓ Teacher router is working")
        else:
            print(f"✗ Teacher router test failed: {response.status_code}")
            return False
            
        # Test validation error (should return 422)
        response = requests.post(
            "http://localhost:8000/api/teacher/clients",
            json={"name": "Test"}  # Missing required fields
        )
        if response.status_code == 422:
            print("✓ Validation errors return 422 (correct)")
            print(f"  Error format: {response.json()['detail'][0]['msg']}")
        else:
            print(f"✗ Expected 422 for validation error, got: {response.status_code}")
            return False
            
        print("\n✅ All tests passed! Server is working correctly.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Is it running?")
        print("  Start with: python -m uvicorn backend.app:app --reload")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
