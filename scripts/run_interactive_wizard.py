#!/usr/bin/env python3
"""
Run Interactive Project Initialization Wizard

This script checks for required dependencies and launches the interactive
project initialization wizard. It will install the 'rich' package if
not already present for an enhanced experience.

Usage:
    python scripts/run_interactive_wizard.py  # Run the wizard

    # With specific options
    python scripts/run_interactive_wizard.py --no-install  # Don't attempt to install dependencies
"""

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.append(str(SCRIPT_DIR))


def check_dependency(package: str) -> bool:
    """Check if a package is installed."""
    return importlib.util.find_spec(package) is not None


def install_package(package: str) -> bool:
    """Attempt to install a package using pip."""
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the interactive project initialization wizard"
    )
    parser.add_argument(
        "--no-install",
        action="store_true",
        help="Don't attempt to install missing dependencies",
    )
    return parser.parse_args()


def main() -> None:
    """Main function to run the wizard."""
    args = parse_arguments()

    # Check for required dependencies
    required_packages = ["rich", "yaml"]
    missing_packages = [pkg for pkg in required_packages if not check_dependency(pkg)]

    # Handle yaml special case (imported as PyYAML but used as yaml)
    if "yaml" in missing_packages:
        if check_dependency("PyYAML"):
            missing_packages.remove("yaml")
        else:
            missing_packages[missing_packages.index("yaml")] = "PyYAML"

    # Attempt to install missing packages
    if missing_packages and not args.no_install:
        print(f"Installing missing dependencies: {', '.join(missing_packages)}")
        for package in missing_packages:
            if not install_package(package):
                print(f"Failed to install {package}. Please install it manually:")
                print(f"  pip install {package}")
                if package == "rich":
                    print("Continuing with basic UI...")
                elif package.lower() == "pyyaml":
                    print("PyYAML is required. Exiting.")
                    sys.exit(1)

    # Import and run the wizard
    try:
        from interactive_wizard import main as run_wizard

        run_wizard()
    except ImportError as e:
        print(f"Error importing wizard: {e}")
        print("Make sure the interactive_wizard.py file is in the scripts directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running wizard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
