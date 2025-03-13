#!/usr/bin/env python3
"""
Run all tests for the interactive wizard.

This script runs all tests for the interactive wizard and its components,
including unit tests and integration tests.

Usage:
    python tests/run_wizard_tests.py  # Run all tests
    python tests/run_wizard_tests.py --unit  # Run only unit tests
    python tests/run_wizard_tests.py --integration  # Run only integration tests
"""

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run tests for the interactive wizard")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    return parser.parse_args()


def run_tests(test_files, verbose=False):
    """Run pytest on the specified test files."""
    pytest_args = ["pytest"]

    if verbose:
        pytest_args.append("-v")

    pytest_args.extend(test_files)

    try:
        result = subprocess.run(pytest_args, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with exit code {e.returncode}")
        return False


def main():
    """Run all tests for the interactive wizard."""
    args = parse_args()

    # Get the tests directory
    tests_dir = Path(__file__).resolve().parent

    # Define test files
    unit_tests = [
        str(tests_dir / "test_interactive_wizard.py"),
        str(tests_dir / "test_run_interactive_wizard.py"),
    ]

    integration_tests = [
        str(tests_dir / "test_wizard_scripts.py"),
    ]

    # Determine which tests to run
    if args.unit and not args.integration:
        test_files = unit_tests
        print("Running unit tests...")
    elif args.integration and not args.unit:
        test_files = integration_tests
        print("Running integration tests...")
    else:
        test_files = unit_tests + integration_tests
        print("Running all tests...")

    # Run the tests
    success = run_tests(test_files, args.verbose)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
