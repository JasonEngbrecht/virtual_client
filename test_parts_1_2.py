"""
Test runner for Phase 1.2 Parts 1 & 2
Verifies all client service functionality
"""

import subprocess
import sys

def run_parts_1_and_2():
    """Run tests for Parts 1 and 2 of Phase 1.2"""
    print("=" * 60)
    print("Running Phase 1.2 Parts 1 & 2 Tests")
    print("Testing complete ClientService implementation")
    print("=" * 60)
    
    # Run all client service tests
    cmd = [
        sys.executable, 
        "-m", 
        "pytest",
        "tests/unit/test_client_service.py",
        "-v",
        "--tb=short"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ Parts 1 & 2 Complete!")
        print("\nClientService now has:")
        print("- Basic CRUD operations (inherited from BaseCRUD)")
        print("- Teacher-filtered queries (get_teacher_clients)")
        print("- Teacher-scoped creation (create_client_for_teacher)")
        print("- Permission checks (can_update, can_delete)")
        print("\nReady for Part 3: API Router implementation")
    else:
        print("\n❌ Tests failed. Please check the errors above.")
    
    return result.returncode

if __name__ == "__main__":
    exit(run_parts_1_and_2())
