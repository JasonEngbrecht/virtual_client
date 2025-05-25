"""
Run enrollment API integration tests
"""

import subprocess
import sys

print("Running enrollment API integration tests...")
print("=" * 60)

# Run the specific test file
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/integration/test_enrollment_api.py", "-v"],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# Print summary
if result.returncode == 0:
    print("\n✅ All enrollment API tests passed!")
else:
    print(f"\n❌ Tests failed with return code: {result.returncode}")
    print("\nTo debug, run:")
    print("  python -m pytest tests/integration/test_enrollment_api.py -v -s")

sys.exit(result.returncode)
