#!/usr/bin/env python3
"""
Task Runner for Enterprise Data Engineering Project

This script provides a Python-based alternative to the Makefile, particularly
useful for Windows users who may not have access to GNU Make.

Usage:
    python scripts/tasks.py [command]

Commands:
    help            - Show this help message
    setup           - Run the unified setup script
    setup-no-admin  - Setup without admin rights
    setup-quick     - Quick setup with minimal dependencies
    test            - Run tests
    coverage        - Run tests with coverage
    lint            - Run linting checks
    format          - Format code
    precommit       - Run pre-commit on all files
    docs            - Build and serve documentation
    docs-build      - Build documentation
    build           - Build Python package
    clean           - Clean build artifacts
    check-all       - Run all checks (lint, test)
    freeze          - Generate requirements.txt from pyproject.toml
    venv            - Create virtual environment
    diagnostics     - Run diagnostics
    diagnostics-full - Run full diagnostics
    check-deps      - Check for outdated dependencies
    update-deps     - Update all dependencies
    verify-setup    - Verify the setup is working

Examples:
    python scripts/tasks.py setup
    python scripts/tasks.py lint
    python scripts/tasks.py test
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Colors for console output
IS_WINDOWS = platform.system() == "Windows"
USE_COLORS = not IS_WINDOWS or "WT_SESSION" in os.environ

# ANSI color codes
GREEN = "\033[0;32m" if USE_COLORS else ""
CYAN = "\033[0;36m" if USE_COLORS else ""
YELLOW = "\033[1;33m" if USE_COLORS else ""
RED = "\033[0;31m" if USE_COLORS else ""
NC = "\033[0m" if USE_COLORS else ""  # No Color


def print_header(message: str) -> None:
    """Print a header message."""
    print(f"\n{CYAN}=== {message} ==={NC}\n")


def run_command(
    cmd: list[str] | str, shell: bool = False, check: bool = True
) -> subprocess.CompletedProcess[str] | None:
    """Run a command and handle errors."""
    print(f'{YELLOW}Running: {" ".join(cmd) if isinstance(cmd, list) else cmd}{NC}')

    try:
        result = subprocess.run(cmd, shell=shell, check=check, cwd=PROJECT_ROOT, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error: Command failed with exit code {e.returncode}{NC}")
        return None


def setup():
    """Run the unified setup script."""
    print_header("Setting up development environment")
    run_command([sys.executable, "scripts/unified_setup.py"])


def setup_no_admin():
    """Run non-admin setup."""
    print_header("Setting up without admin rights")
    run_command([sys.executable, "scripts/unified_setup.py", "--no-admin"])


def setup_quick():
    """Run quick setup."""
    print_header("Running quick setup")
    run_command([sys.executable, "scripts/unified_setup.py", "--quick"])


def run_tests():
    """Run tests."""
    print_header("Running tests")
    run_command([sys.executable, "-m", "pytest"])


def run_coverage():
    """Run tests with coverage."""
    print_header("Running tests with coverage")
    run_command(
        [sys.executable, "-m", "pytest", "--cov=src", "--cov-report=term", "--cov-report=html"]
    )


def run_lint():
    """Run linting checks."""
    print_header("Running linting checks")

    if shutil.which("ruff"):
        run_command(["ruff", "check", "."])
    else:
        # Try using Python module if command not found
        run_command([sys.executable, "-m", "ruff", "check", "."])


def run_format():
    """Format code."""
    print_header("Formatting code")

    if shutil.which("ruff"):
        run_command(["ruff", "format", "."])
    else:
        # Try using Python module if command not found
        run_command([sys.executable, "-m", "ruff", "format", "."])


def run_precommit():
    """Run pre-commit on all files."""
    print_header("Running pre-commit hooks")

    if shutil.which("pre-commit"):
        run_command(["pre-commit", "run", "--all-files"])
    else:
        # Try using Python module if command not found
        run_command([sys.executable, "-m", "pre_commit", "run", "--all-files"])


def run_docs():
    """Build and serve documentation."""
    print_header("Building and serving documentation")

    if shutil.which("hatch"):
        run_command(["hatch", "run", "docs:serve"])
    else:
        # Try using Python module if command not found
        print(f"{YELLOW}Hatch not found, trying mkdocs directly...{NC}")
        if shutil.which("mkdocs"):
            run_command(["mkdocs", "serve"])
        else:
            print(
                f"{RED}Neither hatch nor mkdocs found in PATH. Please install: pip install hatch mkdocs{NC}"
            )


def build_docs():
    """Build documentation."""
    print_header("Building documentation")

    if shutil.which("hatch"):
        run_command(["hatch", "run", "docs:build"])
    else:
        # Try using Python module if command not found
        print(f"{YELLOW}Hatch not found, trying mkdocs directly...{NC}")
        if shutil.which("mkdocs"):
            run_command(["mkdocs", "build"])
        else:
            print(
                f"{RED}Neither hatch nor mkdocs found in PATH. Please install: pip install hatch mkdocs{NC}"
            )


def build_package():
    """Build Python package."""
    print_header("Building package")

    if shutil.which("hatch"):
        run_command(["hatch", "build"])
    else:
        # Try using Python module if command not found
        print(f"{YELLOW}Hatch not found, trying setuptools directly...{NC}")
        run_command([sys.executable, "setup.py", "bdist_wheel"])


def clean():
    """Clean build artifacts."""
    print_header("Cleaning build artifacts")

    # Directories to remove
    dirs_to_remove = ["dist", "build", ".pytest_cache", ".ruff_cache", ".coverage", ".mypy_cache"]

    # Remove directories
    for dir_name in dirs_to_remove:
        dir_path = PROJECT_ROOT / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"Removing {dir_path}")
            shutil.rmtree(dir_path)

    # Find and remove __pycache__ directories
    for pycache_dir in PROJECT_ROOT.glob("**/__pycache__"):
        if pycache_dir.is_dir():
            print(f"Removing {pycache_dir}")
            shutil.rmtree(pycache_dir)


def check_all():
    """Run all checks (lint, test)."""
    print_header("Running all checks")

    # Run lint first
    lint_result = run_lint()
    if lint_result and lint_result.returncode != 0:
        print(f"{RED}Linting failed, not proceeding to tests{NC}")
        return

    # Then run tests
    run_tests()

    print(f"{GREEN}All checks passed!{NC}")


def freeze():
    """Generate requirements.txt from pyproject.toml."""
    print_header("Generating requirements.txt")

    if shutil.which("hatch"):
        run_command(["hatch", "run", "pip", "freeze", ">", "requirements.txt"], shell=True)
    else:
        # Try using pip directly if hatch not found
        run_command([sys.executable, "-m", "pip", "freeze", ">", "requirements.txt"], shell=True)


def create_venv():
    """Create and activate virtual environment."""
    print_header("Creating virtual environment")

    venv_dir = PROJECT_ROOT / ".venv"

    # Create virtual environment
    run_command([sys.executable, "-m", "venv", str(venv_dir)])

    # Display activation instructions
    if IS_WINDOWS:
        activate_cmd = f"{venv_dir}\\Scripts\\activate"
        if not os.path.exists(f"{venv_dir}\\Scripts\\activate"):
            activate_cmd = f"{venv_dir}\\Scripts\\Activate.ps1"
    else:
        activate_cmd = f"source {venv_dir}/bin/activate"

    print(f"\n{GREEN}Virtual environment created!{NC}")
    print(f"Activate with: {YELLOW}{activate_cmd}{NC}")


def run_diagnostics():
    """Run diagnostics for troubleshooting."""
    print_header("Running diagnostics")
    run_command([sys.executable, "scripts/diagnostics.py"])


def run_full_diagnostics():
    """Run full diagnostics with detailed information."""
    print_header("Running full diagnostics")
    run_command([sys.executable, "scripts/diagnostics.py", "--full"])


def check_deps():
    """Check for outdated dependencies."""
    print_header("Checking for outdated dependencies")
    run_command([sys.executable, "-m", "pip", "list", "--outdated"])


def update_deps():
    """Update all dependencies to latest versions."""
    print_header("Updating dependencies")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "-e", ".[dev,docs,test]"])


def verify_setup():
    """Verify the setup is working correctly."""
    print_header("Verifying setup")

    # Check Python version
    print(f"Python: {sys.version.split()[0]} on {platform.system()}")

    # Check pip
    run_command([sys.executable, "-m", "pip", "--version"])

    # Check if package is installed
    try:
        run_command(
            [
                sys.executable,
                "-c",
                "import enterprise_data_engineering; print(f'Package version: {enterprise_data_engineering.__version__}')",
            ],
            check=False,
        )
    except:
        print(f"{RED}Error: Package not properly installed{NC}")


def print_help():
    """Print help message."""
    print(__doc__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Task runner for Enterprise Data Engineering Project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Run 'python scripts/tasks.py help' for more information.",
    )

    parser.add_argument("command", nargs="?", default="help", help="Command to run")

    args = parser.parse_args()

    # Command mapping
    commands = {
        "help": print_help,
        "setup": setup,
        "setup-no-admin": setup_no_admin,
        "setup-quick": setup_quick,
        "test": run_tests,
        "coverage": run_coverage,
        "lint": run_lint,
        "format": run_format,
        "precommit": run_precommit,
        "docs": run_docs,
        "docs-build": build_docs,
        "build": build_package,
        "clean": clean,
        "check-all": check_all,
        "freeze": freeze,
        "venv": create_venv,
        "diagnostics": run_diagnostics,
        "diagnostics-full": run_full_diagnostics,
        "check-deps": check_deps,
        "update-deps": update_deps,
        "verify-setup": verify_setup,
    }

    # Run the selected command
    if args.command in commands:
        commands[args.command]()
    else:
        print(f"{RED}Unknown command: {args.command}{NC}")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
