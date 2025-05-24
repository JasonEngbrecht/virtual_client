"""
Test runner for Phase 1.2 Part 2
Tests teacher-filtered methods in ClientService
"""

import subprocess
import sys

def run_part2_tests():
    """Run tests for Part 2 of Phase 1.2"""
    print("=" * 60)
    print("Running Phase 1.2 Part 2 Tests")
    print("Testing teacher-filtered methods")
    print("=" * 60)
    
    # Run the specific test class for Part 2
    cmd = [
        sys.executable, 
        "-m", 
        "pytest",
        "tests/unit/test_client_service.py::TestClientServiceTeacherMethods",
        "-v",
        "--tb=short"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ Part 2 Complete! Teacher-filtered methods are working correctly.")
        print("\nWhat was implemented:")
        print("- get_teacher_clients() - Filter clients by teacher")
        print("- create_client_for_teacher() - Create with teacher assignment")
        print("- can_update() - Permission check for updates")
        print("- can_delete() - Permission check for deletes")
        print("\nAll methods tested with:")
        print("- Multiple teachers and clients")
        print("- Permission boundaries")
        print("- Pagination support")
        print("- Pydantic model integration")
        print("\nNext step: Part 3 - Create minimal API router")
    else:
        print("\n❌ Part 2 tests failed. Please check the errors above.")
    
    return result.returncode

if __name__ == "__main__":
    exit(run_part2_tests())
