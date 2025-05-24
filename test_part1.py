"""
Test runner for Phase 1.2 Part 1
Tests basic ClientService implementation
"""

import subprocess
import sys

def run_part1_tests():
    """Run tests for Part 1 of Phase 1.2"""
    print("=" * 60)
    print("Running Phase 1.2 Part 1 Tests")
    print("Testing basic ClientService implementation")
    print("=" * 60)
    
    # Run the specific test file
    cmd = [
        sys.executable, 
        "-m", 
        "pytest",
        "tests/unit/test_client_service.py::TestClientServiceBasic",
        "-v",
        "--tb=short"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ Part 1 Complete! ClientService is working correctly.")
        print("\nWhat was implemented:")
        print("- ClientService class inheriting from BaseCRUD")
        print("- Global client_service instance")
        print("- All CRUD operations available through inheritance")
        print("\nNext step: Part 2 - Add teacher-filtered methods")
    else:
        print("\n❌ Part 1 tests failed. Please check the errors above.")
    
    return result.returncode

if __name__ == "__main__":
    exit(run_part1_tests())
