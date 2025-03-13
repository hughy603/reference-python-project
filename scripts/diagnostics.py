#!/usr/bin/env python3
"""
Diagnostics script for Enterprise Data Engineering.

This script collects system information and environment details to help
troubleshoot setup and runtime issues.

Usage:
    python scripts/diagnostics.py [--full]

Options:
    --full    Include more detailed information (may include sensitive data)
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Colors for console output
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
BOLD = "\033[1m"
NC = "\033[0m"  # No Color


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{BOLD}{'=' * 40}{NC}")
    print(f"{BOLD}{title}{NC}")
    print(f"{BOLD}{'=' * 40}{NC}\n")


def run_command(cmd: list[str], ignore_errors: bool = False) -> str:
    """Run a command and return the output."""
    try:
        result = subprocess.run(cmd, check=not ignore_errors, text=True, capture_output=True)
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        return f"Error: {e}"


def check_command_exists(command: str) -> bool:
    """Check if a command exists."""
    return shutil.which(command) is not None


def get_system_info() -> None:
    """Get basic system information."""
    print_section("System Information")

    print(f"Date and Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: {platform.platform()}")
    print(f"Python Version: {platform.python_version()}")
    print(f"Python Path: {sys.executable}")
    print(f"Architecture: {platform.machine()}")
    print(f"Processor: {platform.processor()}")

    # Try to get more OS-specific information
    if platform.system() == "Windows":
        print(f"Windows Version: {platform.version()}")
        print("Windows Release: ", platform.release())
        # Check for WSL
        wsl_version = run_command(["wsl", "--version"], ignore_errors=True)
        if not wsl_version.startswith("Error"):
            print(f"WSL Version: {wsl_version}")
    elif platform.system() == "Linux":
        # Check if running in WSL
        if os.path.exists("/proc/version"):
            with open("/proc/version") as f:
                version_info = f.read()
                if "microsoft" in version_info.lower():
                    print("Environment: WSL (Windows Subsystem for Linux)")

        # Try to get distribution info
        try:
            # Optional module - may not be installed
            # type: ignore [import-not-found]
            import distro  # type: ignore

            print(f"Linux Distribution: {distro.name()} {distro.version()}")
        except ImportError:
            dist = run_command(["cat", "/etc/os-release"], ignore_errors=True)
            print(f"Linux Distribution: \n{dist}")
    elif platform.system() == "Darwin":
        mac_version = run_command(["sw_vers"], ignore_errors=True)
        print(f"macOS Details: \n{mac_version}")


def get_environment_vars(include_sensitive: bool = False) -> None:
    """Get relevant environment variables."""
    print_section("Environment Variables")

    relevant_vars = [
        "PATH",
        "PYTHONPATH",
        "VIRTUAL_ENV",
        "AWS_PROFILE",
        "AWS_REGION",
        "TERRAFORM_HOME",
        "JAVA_HOME",
        "HOME",
        "SHELL",
    ]

    if include_sensitive:
        relevant_vars.extend(["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"])
        print(f"{YELLOW}Warning: Displaying sensitive environment variables{NC}")

    for var in relevant_vars:
        if var in os.environ:
            # Mask sensitive variables even if requested
            if var in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]:
                value = os.environ[var]
                if value:
                    value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            else:
                value = os.environ[var]
            print(f"{var}: {value}")
        else:
            print(f"{var}: Not set")


def check_dependencies() -> None:
    """Check if required dependencies are installed."""
    print_section("Dependency Checks")

    dependencies = [
        "python",
        "pip",
        "git",
        "aws",
        "terraform",
        "docker",
        "mkdocs",
        "python3",
        "ruff",
    ]

    for dep in dependencies:
        if check_command_exists(dep):
            version_cmd = {
                "python": ["python", "--version"],
                "pip": ["pip", "--version"],
                "git": ["git", "--version"],
                "aws": ["aws", "--version"],
                "terraform": ["terraform", "version"],
                "docker": ["docker", "--version"],
                "mkdocs": ["mkdocs", "--version"],
                "python3": ["python3", "--version"],
                "ruff": ["ruff", "--version"],
            }.get(dep, [dep, "--version"])

            version = run_command(version_cmd, ignore_errors=True)
            print(f"{GREEN}✓{NC} {dep}: {version}")
        else:
            print(f"{RED}✗{NC} {dep}: Not found")


def check_python_packages() -> None:
    """Check installed Python packages."""
    print_section("Python Packages")

    packages = run_command([sys.executable, "-m", "pip", "list"], ignore_errors=True)
    print(packages)


def check_project_structure() -> None:
    """Check the project structure."""
    print_section("Project Structure")

    # Get the project root directory
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    print(f"Project Root: {project_root}")

    # Check for important directories and files
    important_paths = [
        ".venv",
        "src",
        "tests",
        "docs",
        "infrastructure",
        "pyproject.toml",
        "setup.py",
        ".git",
    ]

    for path in important_paths:
        full_path = project_root / path
        if full_path.exists():
            if full_path.is_dir():
                print(f"{GREEN}✓{NC} Directory {path} exists")
            else:
                print(f"{GREEN}✓{NC} File {path} exists")
        else:
            print(f"{RED}✗{NC} {path} not found")


def check_git_status() -> None:
    """Check git status."""
    print_section("Git Information")

    if check_command_exists("git"):
        # Check if in a git repository
        git_check = run_command(["git", "rev-parse", "--is-inside-work-tree"], ignore_errors=True)
        if git_check == "true":
            # Get current branch
            branch = run_command(["git", "branch", "--show-current"], ignore_errors=True)
            print(f"Current Branch: {branch}")

            # Get latest commit
            commit = run_command(["git", "log", "-1", "--oneline"], ignore_errors=True)
            print(f"Latest Commit: {commit}")

            # Check for uncommitted changes
            status = run_command(["git", "status", "--porcelain"], ignore_errors=True)
            if status:
                print(f"Uncommitted Changes: Yes ({len(status.splitlines())} files)")
            else:
                print("Uncommitted Changes: No")
        else:
            print("Not in a git repository")
    else:
        print("Git not available")


def check_virtual_env() -> None:
    """Check virtual environment status."""
    print_section("Virtual Environment")

    if "VIRTUAL_ENV" in os.environ:
        venv_path = os.environ["VIRTUAL_ENV"]
        print(f"Active Virtual Environment: {venv_path}")

        # Check Python version in venv
        venv_python = os.path.join(
            venv_path, "Scripts" if platform.system() == "Windows" else "bin", "python"
        )
        if os.path.exists(venv_python):
            venv_version = run_command([venv_python, "--version"], ignore_errors=True)
            print(f"Virtual Env Python: {venv_version}")
    else:
        print("No active virtual environment detected")

    # Check for a .venv directory in the project
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    venv_dir = project_root / ".venv"

    if venv_dir.exists():
        print(f"Project Virtual Environment: {venv_dir} (exists)")
    else:
        print("Project Virtual Environment: Not found")


def export_as_json(include_sensitive: bool = False) -> None:
    """Export all diagnostic information as JSON."""
    print_section("JSON Export")

    # Gather all information
    data: dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "python_path": sys.executable,
            "architecture": platform.machine(),
            "processor": platform.processor(),
        },
        "environment": {},
        "dependencies": {},
        "project": {
            "script_path": str(Path(__file__).resolve()),
            "project_root": str(Path(__file__).resolve().parent.parent),
        },
    }

    # Add environment variables
    for var, value in os.environ.items():
        if include_sensitive or var not in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]:
            # Still mask sensitive data in output
            if var in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]:
                if value:
                    value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            data["environment"][var] = value

    # Add dependency checks
    dependencies = ["python", "pip", "git", "aws", "terraform", "docker", "mkdocs"]
    for dep in dependencies:
        data["dependencies"][dep] = {
            "installed": check_command_exists(dep),
            "version": run_command([dep, "--version"], ignore_errors=True)
            if check_command_exists(dep)
            else None,
        }

    print(json.dumps(data, indent=2))


def main() -> None:
    """Run the diagnostics script."""
    parser = argparse.ArgumentParser(description="Diagnostics tool for Enterprise Data Engineering")
    parser.add_argument("--full", action="store_true", help="Include more detailed information")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    print(f"{BOLD}Enterprise Data Engineering Diagnostics{NC}")
    print(f"Running diagnostics at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.json:
        export_as_json(include_sensitive=args.full)
        return

    get_system_info()
    check_virtual_env()
    get_environment_vars(include_sensitive=args.full)
    check_dependencies()
    check_project_structure()
    check_git_status()

    if args.full:
        check_python_packages()

    print_section("Diagnostics Complete")
    print(f"{GREEN}Diagnostics information collection complete.{NC}")
    print("If you're troubleshooting an issue, please include this output when seeking help.")


if __name__ == "__main__":
    main()
