"""
Test runner script for Virtual Client project
Run from project root: python run_tests.py
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

import sys
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_tests(test_path=None, markers=None, verbose=False):
    """
    Run pytest with specified options
    
    Args:
        test_path: Specific test file or directory to run
        markers: Test markers to filter (e.g., 'unit', 'integration')
        verbose: Show verbose output
    """
    # Use sys.executable to ensure we use the same Python interpreter
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add test path if specified
    if test_path:
        cmd.append(test_path)
    else:
        cmd.append("tests/")
    
    # Add markers if specified
    if markers:
        cmd.extend(["-m", markers])
    
    # Add verbose flag
    if verbose:
        cmd.append("-v")
    
    # Add coverage report
    cmd.extend(["--cov=backend", "--cov-report=term-missing"])
    
    # Show test output
    cmd.append("-s")
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 80)
    
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Virtual Client tests")
    parser.add_argument(
        "test_path",
        nargs="?",
        help="Specific test file or directory to run"
    )
    parser.add_argument(
        "-m", "--markers",
        help="Run tests matching given mark expression (e.g., 'unit', 'integration', 'not slow')"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run unit tests only"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests only"
    )
    parser.add_argument(
        "--db",
        action="store_true",
        help="Run database tests only"
    )
    
    args = parser.parse_args()
    
    # Handle convenience flags
    markers = args.markers
    if args.unit:
        markers = "unit"
    elif args.integration:
        markers = "integration"
    
    test_path = args.test_path
    if args.db:
        test_path = "tests/unit/test_database.py"
    
    # Run tests
    exit_code = run_tests(
        test_path=test_path,
        markers=markers,
        verbose=args.verbose
    )
    
    sys.exit(exit_code)
