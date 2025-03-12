#!/usr/bin/env python3
"""
Unified setup script for the Enterprise Data Engineering project.

This script provides a streamlined setup process for all platforms:
1. Verifies Python version (3.10+ required)
2. Creates a virtual environment
3. Installs the project with all dependencies
4. Sets up pre-commit hooks
"""

import os
import platform
import subprocess
import sys
import time
import venv
from pathlib import Path

# Console color setup with simple platform detection
IS_WINDOWS = platform.system() == "Windows"
SUPPORTS_COLOR = not IS_WINDOWS or "WT_SESSION" in os.environ

# ANSI color codes (only used if color is supported)
GREEN = "\033[0;32m" if SUPPORTS_COLOR else ""
YELLOW = "\033[1;33m" if SUPPORTS_COLOR else ""
RED = "\033[0;31m" if SUPPORTS_COLOR else ""
BLUE = "\033[0;34m" if SUPPORTS_COLOR else ""
BOLD = "\033[1m" if SUPPORTS_COLOR else ""
NC = "\033[0m" if SUPPORTS_COLOR else ""  # No Color

# Main project directory (where this script is located)
PROJECT_DIR = Path(__file__).resolve().parent
VENV_DIR = PROJECT_DIR / ".venv"


def print_status(message: str) -> None:
    """Print a success message with colorized output."""
    print(f"{GREEN}✓ {message}{NC}")


def print_warning(message: str) -> None:
    """Print a warning message with colorized output."""
    print(f"{YELLOW}! {message}{NC}")


def print_error(message: str) -> None:
    """Print an error message with colorized output and exit."""
    print(f"{RED}✗ {message}{NC}")
    sys.exit(1)


def print_step(step_num: int, total: int, message: str) -> None:
    """Print a step with progress indication."""
    print(f"\n{BOLD}[{step_num}/{total}] {message}...{NC}")


def show_spinner(seconds: int, message: str) -> None:
    """Show a simple spinner for the given number of seconds."""
    if not sys.stdout.isatty():
        print(f"{message}... ", end="")
        time.sleep(seconds)
        print("Done")
        return

    spinner = ["|", "/", "-", "\\"]
    end = time.time() + seconds
    i = 0
    print(f"{message}... ", end="", flush=True)

    while time.time() < end:
        print(f"\b{spinner[i % len(spinner)]}", end="", flush=True)
        i += 1
        time.sleep(0.1)

    print("\bDone")


def run_command(cmd: list[str], error_message: str, capture_output: bool = False) -> str | None:
    """Run a command and handle errors. Returns output if capture_output is True."""
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=capture_output)
        return result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        print_error(f"{error_message}: {e}")
        return None


def check_python_version() -> None:
    """Verify that Python 3.10+ is installed."""
    print_step(1, 4, "Checking Python version")

    min_version = (3, 10)
    current_version = sys.version_info

    if current_version < min_version:
        print_error(f"Python 3.10+ is required (found {sys.version.split()[0]})")

    print_status(f"Python version: {sys.version.split()[0]}")


def setup_venv() -> tuple[Path, Path]:
    """Create and activate a virtual environment."""
    print_step(2, 4, "Setting up virtual environment")

    # Create venv if it doesn't exist
    if not VENV_DIR.exists():
        print("Creating virtual environment...")
        venv.create(VENV_DIR, with_pip=True)
        print_status("Virtual environment created")
    else:
        print_warning("Using existing virtual environment")

    # Get paths to Python and pip in virtual environment
    if IS_WINDOWS:
        python_exe = VENV_DIR / "Scripts" / "python.exe"
        pip_exe = VENV_DIR / "Scripts" / "pip.exe"
    else:
        python_exe = VENV_DIR / "bin" / "python"
        pip_exe = VENV_DIR / "bin" / "pip"

    # Validate the files exist
    if not python_exe.exists():
        print_error(
            f"Python executable not found at {python_exe}. Try removing the .venv directory and running setup again."
        )

    return python_exe, pip_exe


def install_dependencies(python_exe: Path) -> None:
    """Install project in development mode with all extras."""
    print_step(3, 4, "Installing dependencies")

    # Upgrade pip first
    print("Upgrading pip...")
    try:
        run_command(
            [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], "Failed to upgrade pip"
        )
        print_status("Pip upgraded")
    except Exception:
        print_warning("Couldn't upgrade pip, continuing with existing version")

    # Install the project in dev mode with all extras
    print("Installing project dependencies (this may take a few minutes)...")

    # Show a spinner for long-running tasks
    show_spinner(2, "Preparing installation")

    result = run_command(
        [str(python_exe), "-m", "pip", "install", "-e", ".[dev,docs,test]"],
        "Failed to install dependencies. Please check your internet connection and try again.",
        capture_output=True,
    )

    if result and "Successfully installed" in result:
        print_status("Dependencies installed successfully")
    else:
        print_status("Dependencies installed")


def setup_pre_commit(python_exe: Path) -> None:
    """Install and set up pre-commit hooks."""
    print_step(4, 4, "Setting up pre-commit hooks")

    # Install pre-commit
    print("Installing pre-commit...")
    run_command(
        [str(python_exe), "-m", "pip", "install", "pre-commit"], "Failed to install pre-commit"
    )
    print_status("Pre-commit installed")

    # Set up the git hooks
    print("Installing pre-commit hooks...")
    run_command(
        [str(python_exe), "-m", "pre_commit", "install"], "Failed to install pre-commit hooks"
    )
    print_status("Pre-commit hooks installed")

    # Initialize hooks to avoid first-time slowdown
    print("Running pre-commit on key files (this may take a moment)...")

    # Only run on a few key files to speed up initialization
    try:
        show_spinner(3, "Running pre-commit initialization")
        subprocess.run(
            [str(python_exe), "-m", "pre_commit", "run", "--files", "setup.py", "pyproject.toml"],
            check=False,
            capture_output=True,
        )
        print_status("Pre-commit initialization complete")
    except Exception:
        print_warning("Pre-commit initialization had some issues (this is normal for first run)")


def print_next_steps() -> None:
    """Print guidance on next steps."""
    print(f"\n{GREEN}{BOLD}Setup completed successfully!{NC}")

    # Show activation command based on platform
    if IS_WINDOWS:
        activate_cmd = f"{VENV_DIR}\\Scripts\\activate"
    else:
        activate_cmd = f"source {VENV_DIR}/bin/activate"

    print(
        f"""
{BOLD}To activate the virtual environment:{NC}
{YELLOW}{activate_cmd}{NC}

{BOLD}Common commands:{NC}
{YELLOW}pytest{NC}               - Run tests
{YELLOW}ruff check .{NC}         - Run linting checks
{YELLOW}ruff format .{NC}        - Format code
{YELLOW}hatch run docs:serve{NC} - Build and serve documentation

{BLUE}For more information, see:{NC}
{YELLOW}README.md{NC}           - Overview and getting started
{YELLOW}QUICKREF.md{NC}         - Quick reference guide
{YELLOW}docs/index.html{NC}     - Full documentation (after building)
"""
    )


def main() -> None:
    """Run the setup process."""
    print(f"\n{BOLD}Enterprise Data Engineering Setup{NC}\n")

    # Verify Python version
    check_python_version()

    # Set up virtual environment
    python_exe, pip_exe = setup_venv()

    # Install dependencies
    install_dependencies(python_exe)

    # Set up pre-commit
    setup_pre_commit(python_exe)

    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
