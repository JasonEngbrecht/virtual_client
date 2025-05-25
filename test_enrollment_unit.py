"""
Run enrollment service unit tests
"""

import subprocess
import sys

def run_tests():
    """Run the enrollment service unit tests"""
    print("Running Enrollment Service Unit Tests...")
    print("=" * 50)
    
    # Run pytest on the enrollment service tests
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/unit/test_enrollment_service.py", 
        "-v", "--tb=short"
    ])
    
    return result.returncode == 0

if __name__ == "__main__":
    success = run_tests()
    if success:
        print("\n✅ All enrollment service tests passed!")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
    
    sys.exit(0 if success else 1)
