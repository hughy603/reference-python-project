#!/usr/bin/env python3
"""
Unified Setup Script for Enterprise Data Engineering Project

This script detects the platform and launches the appropriate setup process:
- For Windows: Launches PowerShell setup or sets up without admin rights
- For WSL/Linux/macOS: Runs the appropriate bash setup
- For all platforms: Handles virtual environment and dependency setup

Usage:
    python scripts/unified_setup.py [--no-admin] [--quick]

Options:
    --no-admin    Setup without requiring admin privileges
    --quick       Skip non-essential setup steps for a faster setup
"""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

# Detect platform
PLATFORM = platform.system()
IS_WINDOWS = PLATFORM == "Windows"
IS_WSL = "microsoft-standard" in platform.release().lower() if not IS_WINDOWS else False
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Console colors
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
BOLD = "\033[1m"
NC = "\033[0m"  # No Color

# Disable colors if not supported
if IS_WINDOWS and "WT_SESSION" not in os.environ:
    GREEN = YELLOW = RED = BLUE = BOLD = NC = ""


def print_status(message: str) -> None:
    """Print a status message."""
    print(f"{GREEN}✓ {message}{NC}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"{RED}✗ {message}{NC}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"{YELLOW}! {message}{NC}")


def print_header(message: str) -> None:
    """Print a header message."""
    print(f"\n{BOLD}{message}{NC}")


def run_command(
    cmd: list[str], error_message: str | None = None, shell: bool = False, check: bool = True
) -> subprocess.CompletedProcess[str] | None:
    """Run a command and handle errors."""
    try:
        return subprocess.run(cmd, shell=shell, check=check, text=True)
    except subprocess.CalledProcessError as e:
        if error_message:
            print_error(f"{error_message}: {e}")
        return None


def detect_environment() -> dict[str, Any]:
    """Detect the current environment and capabilities."""
    print_header("🔍 Detecting environment")

    env_info: dict[str, Any] = {
        "platform": PLATFORM,
        "is_windows": IS_WINDOWS,
        "is_wsl": IS_WSL,
        "python_version": platform.python_version(),
        "is_admin": False,
        "has_virtualenv": False,
        "has_git": False,
    }

    # Check Python version
    print(f'Python version: {env_info["python_version"]}')

    # Check for admin rights on Windows
    if IS_WINDOWS:
        try:
            # This will raise an exception if not admin
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "($([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))",
                ],
                capture_output=True,
                check=True,
            )
            env_info["is_admin"] = True
            print("Admin rights: Yes")
        except:
            print("Admin rights: No")

    # Check for virtual environment capability
    try:
        subprocess.run([sys.executable, "-m", "venv", "--help"], capture_output=True, check=True)
        env_info["has_virtualenv"] = True
        print("Virtual environment support: Yes")
    except:
        print("Virtual environment support: No")

    # Check for Git
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        env_info["has_git"] = True
        print("Git installed: Yes")
    except:
        print("Git installed: No")

    return env_info


def setup_windows(no_admin: bool = False, quick: bool = False) -> bool:
    """Run Windows-specific setup."""
    print_header("🪟 Setting up Windows environment")

    if no_admin:
        print("Running non-administrator setup for Windows...")
        script_path = PROJECT_ROOT / "scripts" / "non_admin_setup.ps1"
    else:
        print("Running full Windows setup (requires administrator privileges)...")
        script_path = PROJECT_ROOT / "scripts" / "windows_setup.ps1"

    if not script_path.exists():
        print_error(f"Setup script not found: {script_path}")
        return False

    # Create arguments for the script
    args: list[str] = []
    if quick:
        args.append("-Quick")

    # Execute PowerShell script
    try:
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)]
        if args:
            cmd.extend(args)

        print(f'Running: {" ".join(cmd)}')
        subprocess.run(cmd, check=True)
        print_status("Windows setup completed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Windows setup failed: {e}")
        return False


def setup_wsl(quick: bool = False) -> bool:
    """Run WSL-specific setup."""
    print_header("🐧 Setting up WSL environment")

    script_path = PROJECT_ROOT / "scripts" / "wsl_setup.sh"

    if not script_path.exists():
        print_error(f"Setup script not found: {script_path}")
        return False

    # Make sure the script is executable
    script_path.chmod(script_path.stat().st_mode | 0o111)

    # Execute WSL setup script
    cmd = [str(script_path)]
    if quick:
        cmd.append("--quick")

    try:
        print(f'Running: {" ".join(cmd)}')
        subprocess.run(cmd, check=True)
        print_status("WSL setup completed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"WSL setup failed: {e}")
        return False


def setup_unix(quick: bool = False) -> bool:
    """Run setup for Unix-like systems (Linux/macOS)."""
    print_header("🐧 Setting up Unix environment")

    script_path = PROJECT_ROOT / "scripts" / "setup.sh"

    if not script_path.exists():
        print_error(f"Setup script not found: {script_path}")
        return False

    # Make sure the script is executable
    script_path.chmod(script_path.stat().st_mode | 0o111)

    # Execute Unix setup script
    cmd = [str(script_path)]
    if quick:
        cmd.append("--quick")

    try:
        print(f'Running: {" ".join(cmd)}')
        subprocess.run(cmd, check=True)
        print_status("Unix setup completed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Unix setup failed: {e}")
        return False


def setup_python_environment() -> bool:
    """Set up Python environment using setup.py."""
    print_header("🐍 Setting up Python environment")

    setup_script = PROJECT_ROOT / "setup.py"

    if not setup_script.exists():
        print_error(f"Setup script not found: {setup_script}")
        return False

    try:
        print("Running Python setup...")
        subprocess.run([sys.executable, str(setup_script)], check=True)
        print_status("Python environment setup completed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Python setup failed: {e}")
        return False


def main() -> None:
    """Main function to run the appropriate setup."""
    parser = argparse.ArgumentParser(
        description="Unified setup script for Enterprise Data Engineering Project"
    )
    parser.add_argument(
        "--no-admin", action="store_true", help="Setup without requiring admin privileges"
    )
    parser.add_argument(
        "--quick", action="store_true", help="Skip non-essential setup steps for a faster setup"
    )
    args = parser.parse_args()

    print_header("🚀 Enterprise Data Engineering Project Setup")
    print(f"Platform: {PLATFORM}")

    # Detect environment
    env_info = detect_environment()

    # Run platform-specific setup
    setup_success = False

    if IS_WINDOWS:
        setup_success = setup_windows(no_admin=args.no_admin, quick=args.quick)
    elif IS_WSL:
        setup_success = setup_wsl(quick=args.quick)
    else:
        setup_success = setup_unix(quick=args.quick)

    # Run Python environment setup regardless of platform
    if setup_success or env_info["has_virtualenv"]:
        setup_python_environment()

    print_header("🎉 Setup process completed!")
    print(
        "If you encountered any issues, please check the documentation or raise an issue on GitHub."
    )
    print("For more information, see:")
    print(f"  - {BLUE}README.md{NC}: Overview and getting started")
    print(f"  - {BLUE}SETUP_GUIDE.md{NC}: Detailed setup instructions")
    print(f"  - {BLUE}QUICKREF.md{NC}: Quick reference guide")


if __name__ == "__main__":
    main()
