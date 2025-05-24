"""
Test runner for Phase 1.2 Part 3
Tests API router setup and endpoints
"""

import subprocess
import sys
import time
import requests
import threading

def start_server():
    """Start the FastAPI server in a subprocess"""
    cmd = [sys.executable, "-m", "uvicorn", "backend.app:app", "--port", "8001"]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def test_endpoints():
    """Test that the endpoints are accessible"""
    base_url = "http://localhost:8001"
    
    # Test endpoints
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/api/teacher/test", "Teacher test endpoint"),
        ("/api/teacher/test-db", "Teacher database test"),
        ("/docs", "API documentation")
    ]
    
    all_passed = True
    
    print("\nTesting endpoints:")
    print("-" * 50)
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint:<25} - {description}")
            else:
                print(f"❌ {endpoint:<25} - Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {endpoint:<25} - Error: {str(e)}")
            all_passed = False
    
    return all_passed

def run_part3_tests():
    """Run tests for Part 3 of Phase 1.2"""
    print("=" * 60)
    print("Running Phase 1.2 Part 3 Tests")
    print("Testing API router setup")
    print("=" * 60)
    
    # Start the server
    print("\nStarting FastAPI server on port 8001...")
    server_process = start_server()
    
    # Give the server time to start
    time.sleep(3)
    
    try:
        # Check if server started successfully
        if server_process.poll() is not None:
            print("❌ Server failed to start!")
            return 1
        
        # Test the endpoints
        all_passed = test_endpoints()
        
        if all_passed:
            print("\n✅ Part 3 Complete! API router is working correctly.")
            print("\nWhat was implemented:")
            print("- Created backend/api/teacher_routes.py")
            print("- Added test endpoints (/test and /test-db)")
            print("- Updated app.py to include the router")
            print("- All endpoints are accessible")
            print("\nAPI Documentation available at: http://localhost:8000/docs")
            print("\nNext step: Part 4 - Add CRUD endpoints one at a time")
            return 0
        else:
            print("\n❌ Part 3 tests failed. Please check the errors above.")
            return 1
            
    finally:
        # Stop the server
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("Please install requests: pip install requests")
        exit(1)
    
    exit(run_part3_tests())
