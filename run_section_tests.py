"""
Quick test runner for Section API integration tests
"""

import subprocess
import sys

print("Running Section API Integration Tests...")
print("=" * 60)

# Run the tests
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/integration/test_section_api.py", "-v"],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\n" + "=" * 60)
if result.returncode == 0:
    print("✓ All tests passed!")
else:
    print("✗ Some tests failed. Please check the output above.")
    
print("=" * 60)
