#!/usr/bin/env python
"""
Nexus Repository Setup Script.

This script configures the project to use an Enterprise Nexus repository for dependencies.
It sets up the necessary environment variables and pip configuration to work with Nexus.
"""

import argparse
import os
import sys
from pathlib import Path

# Add the src directory to the path to import the Nexus module
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from enterprise_data_engineering.common_utils import nexus_utils as nexus
except ImportError:
    print("Error: Could not import the Nexus module.")
    print("Ensure the required dependencies are installed:")
    print("  pip install -e .[nexus]")
    sys.exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Configure Enterprise Nexus repository for this project"
    )
    parser.add_argument(
        "--url",
        help="Nexus repository URL",
        default=os.environ.get("NEXUS_REPOSITORY_URL", ""),
    )
    parser.add_argument(
        "--username",
        help="Nexus username",
        default=os.environ.get("NEXUS_USERNAME", ""),
    )
    parser.add_argument(
        "--password",
        help="Nexus password",
        default=os.environ.get("NEXUS_PASSWORD", ""),
    )
    parser.add_argument(
        "--verify-ssl",
        help="Verify SSL certificates",
        action="store_true",
        default=True,
    )
    parser.add_argument(
        "--no-verify-ssl",
        help="Do not verify SSL certificates",
        dest="verify_ssl",
        action="store_false",
    )
    parser.add_argument(
        "--env",
        help="Set environment variables",
        action="store_true",
    )
    parser.add_argument(
        "--pip",
        help="Configure pip",
        action="store_true",
    )
    parser.add_argument(
        "--check",
        help="Check Nexus connection",
        action="store_true",
    )
    parser.add_argument(
        "--all",
        help="Perform all setup steps",
        action="store_true",
    )

    return parser.parse_args()


def setup_env_vars(url: str, username: str, password: str) -> bool:
    """
    Set environment variables for Nexus.

    Args:
        url: Nexus repository URL
        username: Nexus username
        password: Nexus password

    Returns:
        bool: True if successful, False otherwise
    """
    if not url:
        url = input("Enter Nexus repository URL: ")

    if not username:
        username = input("Enter Nexus username (press Enter to skip): ")

    if not password:
        password = input("Enter Nexus password (press Enter to skip): ")

    if url:
        os.environ["NEXUS_REPOSITORY_URL"] = url
        print(f"Set NEXUS_REPOSITORY_URL environment variable to {url}")
    else:
        print("Error: No repository URL provided")
        return False

    if username:
        os.environ["NEXUS_USERNAME"] = username
        print(f"Set NEXUS_USERNAME environment variable to {username}")

    if password:
        os.environ["NEXUS_PASSWORD"] = password
        print("Set NEXUS_PASSWORD environment variable")

    # Create a .env file for future use
    env_file = project_root / ".env"
    with open(env_file, "w") as f:
        f.write(f"NEXUS_REPOSITORY_URL={url}\n")
        if username:
            f.write(f"NEXUS_USERNAME={username}\n")
        if password:
            f.write(f"NEXUS_PASSWORD={password}\n")

    print(f"Created .env file at {env_file}")
    print("NOTE: Add this file to .gitignore if it contains sensitive information!")

    # Add to .gitignore if not already there
    gitignore_file = project_root / ".gitignore"
    if gitignore_file.exists():
        with open(gitignore_file) as f:
            content = f.read()

        if ".env" not in content:
            with open(gitignore_file, "a") as f:
                f.write("\n# Local environment variables\n.env\n")
            print("Added .env to .gitignore")

    return True


def create_shell_scripts(url: str, username: str, password: str) -> None:
    """
    Create shell scripts to set environment variables.

    Args:
        url: Nexus repository URL
        username: Nexus username
        password: Nexus password
    """
    # Create a shell script for Unix-like systems
    unix_script = project_root / "scripts" / "set_nexus_env.sh"
    with open(unix_script, "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write("# Set Nexus environment variables\n")
        f.write(f'export NEXUS_REPOSITORY_URL="{url}"\n')
        if username:
            f.write(f'export NEXUS_USERNAME="{username}"\n')
        if password:
            f.write(f'export NEXUS_PASSWORD="{password}"\n')

    # Make the script executable
    unix_script.chmod(0o755)
    print(f"Created Unix shell script at {unix_script}")

    # Create a PowerShell script for Windows
    ps_script = project_root / "scripts" / "Set-NexusEnv.ps1"
    with open(ps_script, "w") as f:
        f.write("# Set Nexus environment variables\n")
        f.write(f'$env:NEXUS_REPOSITORY_URL = "{url}"\n')
        if username:
            f.write(f'$env:NEXUS_USERNAME = "{username}"\n')
        if password:
            f.write(f'$env:NEXUS_PASSWORD = "{password}"\n')

        # Add instructions for making the variables permanent
        f.write("\n# To make these variables permanent, you can run:\n")
        f.write(
            '# [System.Environment]::SetEnvironmentVariable("NEXUS_REPOSITORY_URL", $env:NEXUS_REPOSITORY_URL, "User")\n'
        )
        if username:
            f.write(
                '# [System.Environment]::SetEnvironmentVariable("NEXUS_USERNAME", $env:NEXUS_USERNAME, "User")\n'
            )
        if password:
            f.write(
                '# [System.Environment]::SetEnvironmentVariable("NEXUS_PASSWORD", $env:NEXUS_PASSWORD, "User")\n'
            )

    print(f"Created PowerShell script at {ps_script}")


def main():
    """Main entry point for the script."""
    args = parse_args()

    # Default to --all if no specific actions are specified
    if not (args.env or args.pip or args.check):
        args.all = True

    # Initialize the Nexus client
    client = nexus.NexusClient(
        repository_url=args.url,
        username=args.username,
        password=args.password,
        verify_ssl=args.verify_ssl,
    )

    # Set environment variables
    if args.env or args.all:
        success = setup_env_vars(args.url, args.username, args.password)
        if not success:
            return 1

        # Refresh client with new environment variables
        client = nexus.NexusClient(
            repository_url=os.environ.get("NEXUS_REPOSITORY_URL"),
            username=os.environ.get("NEXUS_USERNAME"),
            password=os.environ.get("NEXUS_PASSWORD"),
            verify_ssl=args.verify_ssl,
        )

        # Create shell scripts
        create_shell_scripts(
            os.environ.get("NEXUS_REPOSITORY_URL", ""),
            os.environ.get("NEXUS_USERNAME", ""),
            os.environ.get("NEXUS_PASSWORD", ""),
        )

    # Check connection
    if args.check or args.all:
        print("\nChecking connection to Nexus repository...")
        if client.check_connection():
            print("✅ Successfully connected to Nexus repository")
        else:
            print("❌ Failed to connect to Nexus repository")
            if args.all:
                return 1

    # Configure pip
    if args.pip or args.all:
        print("\nConfiguring pip to use Nexus repository...")
        if client.configure_pip():
            print("✅ Successfully configured pip to use Nexus repository")
        else:
            print("❌ Failed to configure pip")
            if args.all:
                return 1

    print("\nNexus setup complete!")
    print(f"Repository URL: {client.repository_url}")
    print("\nTo use the Nexus repository in your project, install dependencies with:")
    print("  pip install -r requirements.txt")
    print("\nTo publish packages to Nexus, use:")
    print("  python -m reference_python_project.utils.nexus publish path/to/package.whl")

    return 0


if __name__ == "__main__":
    sys.exit(main())
