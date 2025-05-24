"""
Quick test runner for Virtual Client project
"""

import subprocess
import sys

def main():
    print("Running Virtual Client Tests...")
    print("-" * 50)
    
    # Run pytest with cleaner output
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/unit/test_database.py",
        "-v",
        "--tb=short",
        "--no-header"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed.")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
