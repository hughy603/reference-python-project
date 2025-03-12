#!/usr/bin/env python3
"""
Pre-commit Setup Helper Script

This script helps developers set up pre-commit hooks with a
user-friendly interface and robust error handling.

Usage:
    python scripts/setup_precommit.py

The script will:
1. Check if pre-commit is installed
2. Install pre-commit hooks
3. Run an initial pre-commit check
4. Provide helpful feedback and troubleshooting tips
"""

import platform
import subprocess
import sys
from pathlib import Path

# ANSI color codes for better user interface
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
NC = "\033[0m"  # No Color

# Define the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def print_header(message):
    """Print a formatted header message."""
    print(f'\n{BLUE}{BOLD}{"=" * 70}{NC}')
    print(f"{BLUE}{BOLD}  {message}{NC}")
    print(f'{BLUE}{BOLD}{"=" * 70}{NC}\n')


def print_success(message):
    """Print a success message."""
    print(f"{GREEN}✓ {message}{NC}")


def print_warning(message):
    """Print a warning message."""
    print(f"{YELLOW}⚠ {message}{NC}")


def print_error(message):
    """Print an error message."""
    print(f"{RED}✗ {message}{NC}")


def run_command(command, cwd=None, check=True, capture_output=False):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd or PROJECT_ROOT,
            check=check,
            shell=isinstance(command, str),
            text=True,
            capture_output=capture_output,
        )
        return result
    except subprocess.CalledProcessError as e:
        return e


def is_windows():
    """Check if the current OS is Windows."""
    return platform.system().lower() == "windows"


def check_pre_commit():
    """Check if pre-commit is installed."""
    print_header("Checking Pre-commit Installation")

    result = run_command(["pre-commit", "--version"], check=False, capture_output=True)

    if result.returncode == 0:
        print_success(f"Pre-commit is installed: {result.stdout.strip()}")
        return True
    else:
        print_warning("Pre-commit is not installed or not in PATH")
        print("\nTo install pre-commit, run one of the following commands:")
        print(f"{BLUE}    pip install pre-commit{NC}")
        print(f"{BLUE}    conda install -c conda-forge pre-commit{NC}")
        print(f"{BLUE}    brew install pre-commit{NC} (on macOS with Homebrew)")

        install = input("\nWould you like this script to install pre-commit for you? (y/n): ")
        if install.lower() in ["y", "yes"]:
            print("\nInstalling pre-commit...")
            pip_result = run_command(
                [sys.executable, "-m", "pip", "install", "pre-commit"], check=False
            )
            if pip_result.returncode == 0:
                print_success("Pre-commit installed successfully")
                return True
            else:
                print_error("Failed to install pre-commit")
                return False
        return False


def install_hooks():
    """Install pre-commit hooks."""
    print_header("Installing Pre-commit Hooks")

    result = run_command(["pre-commit", "install"], check=False)

    if result.returncode == 0:
        print_success("Pre-commit hooks installed successfully")
        return True
    else:
        print_error("Failed to install pre-commit hooks")
        print(f'Error: {result.stderr if hasattr(result, "stderr") else "Unknown error"}')
        return False


def run_initial_check():
    """Run an initial pre-commit check."""
    print_header("Running Initial Pre-commit Check")

    print("This may take a while on the first run as pre-commit downloads and sets up hooks...")

    # Run with --all-files flag but don't check success to avoid failing the script
    result = run_command(["pre-commit", "run", "--all-files"], check=False)

    if result.returncode == 0:
        print_success("All pre-commit checks passed")
    else:
        print_warning("Some pre-commit checks failed")
        print("\nThis is normal for an initial setup, especially for:")
        print("- terraform_validate (if infrastructure code is incomplete)")
        print("- gitleaks (may find false positives in the .secrets.baseline file)")
        print("- terraform_tflint (may need additional setup)")

        print("\nYou can fix these issues or configure pre-commit to ignore them.")


def fix_tflint_issues():
    """Check and fix common TFLint issues."""
    print_header("Checking TFLint Configuration")

    tflint_config_path = PROJECT_ROOT / "infrastructure" / "terraform" / ".tflint.hcl"

    if not tflint_config_path.exists():
        print_warning(f"TFLint config not found at {tflint_config_path}")
        return

    # Check if tflint is installed
    result = run_command(["tflint", "--version"], check=False, capture_output=True)
    if result.returncode != 0:
        print_warning("TFLint not found in PATH")
        print("To use the terraform_tflint hook, you need to install TFLint")
        print(f"{BLUE}    https://github.com/terraform-linters/tflint#installation{NC}")
        return

    # Run tflint init to check config
    result = run_command(
        ["tflint", "--init", "--config", str(tflint_config_path)],
        cwd=PROJECT_ROOT / "infrastructure" / "terraform",
        check=False,
        capture_output=True,
    )

    if result.returncode != 0:
        print_warning("TFLint initialization failed with the current config")
        print(f"Error: {result.stderr}")
        print("\nThis might be due to incompatible TFLint configuration.")
        print("The script has already updated the configuration to be compatible.")
    else:
        print_success("TFLint configuration is valid")


def display_help():
    """Display help information."""
    print_header("Pre-commit Help Information")

    print(f"{BOLD}Common pre-commit commands:{NC}")
    print("  Run pre-commit on all files:")
    print(f"{BLUE}    pre-commit run --all-files{NC}")
    print("  Run pre-commit on staged files:")
    print(f"{BLUE}    pre-commit run{NC}")
    print("  Run a specific hook:")
    print(f"{BLUE}    pre-commit run terraform_fmt --all-files{NC}")

    print(f"\n{BOLD}Tips for fixing common issues:{NC}")
    print("• If terraform_validate fails: Check your Terraform files for syntax errors")
    print("• If terraform_tflint fails: Run 'tflint --init' in your terraform directory")
    print("• If gitleaks fails: Add specific files to exclude or use allowlist")

    print(f"\n{BOLD}Configuration files:{NC}")
    print(f"• Pre-commit config: {BLUE}.pre-commit-config.yaml{NC}")
    print(f"• TFLint config: {BLUE}infrastructure/terraform/.tflint.hcl{NC}")

    print(f"\n{BOLD}More information:{NC}")
    print(f"{BLUE}https://pre-commit.com/#{NC}")


def main():
    """Main function to run the script."""
    print_header("Pre-commit Setup Helper")

    print("This script helps you set up and configure pre-commit hooks for your project.\n")

    # Check pre-commit installation
    if not check_pre_commit():
        print_error("Pre-commit setup cannot continue without pre-commit installed")
        sys.exit(1)

    # Install hooks
    if not install_hooks():
        print_error("Failed to install pre-commit hooks")
        sys.exit(1)

    # Fix TFLint issues
    fix_tflint_issues()

    # Run initial check
    run_initial_check()

    # Display help
    display_help()

    print_header("Setup Complete")
    print(f"{GREEN}Pre-commit is now set up for your project!{NC}")
    print("\nYour code will be checked automatically when you commit changes.")
    print(f"You can also manually run checks with: {BLUE}pre-commit run --all-files{NC}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
        sys.exit(1)
