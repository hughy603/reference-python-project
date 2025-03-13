#!/usr/bin/env python3
"""
Fix pre-commit issues in the repository.

This script addresses common pre-commit issues and makes it easier to run pre-commit:
1. Fixes end-of-file issues
2. Ensures required tools are installed
3. Updates pre-commit hooks to latest versions
4. Runs specific pre-commit hooks that are likely to succeed
5. Provides guidance on fixing other pre-commit errors
"""

import os
import shutil
import subprocess
import sys

import yaml


def run_command(command: list[str], verbose: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a command and return its output."""
    if verbose:
        print(f"Running: {' '.join(command)}")

    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if verbose:
        if result.returncode != 0:
            print(f"Command failed with exit code {result.returncode}:")
            if result.stderr:
                print(result.stderr)
        else:
            print("Command succeeded.")

    return result


def fix_end_of_file_issues():
    """Fix end-of-file issues automatically."""
    print("\n=== Fixing end-of-file issues ===")

    # Get a list of all files in the repository
    result = run_command(["git", "ls-files"], verbose=False)
    files = result.stdout.strip().split("\n")

    count = 0
    for file_path in files:
        # Skip binary files and certain file types
        if not os.path.isfile(file_path) or file_path.endswith((".png", ".jpg", ".gif", ".pyc")):
            continue

        try:
            with open(file_path, "rb") as f:
                content = f.read()

            # Check if file doesn't end with a newline
            if content and not content.endswith(b"\n"):
                with open(file_path, "ab") as f:
                    f.write(b"\n")
                print(f"Fixed end-of-file newline in: {file_path}")
                count += 1
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"Fixed {count} files with end-of-file issues.")


def check_required_tools():
    """Check if required tools are installed and install if needed."""
    print("\n=== Checking required tools ===")

    # Check pre-commit
    if shutil.which("pre-commit") is None:
        print("pre-commit not found. Installing...")
        run_command(["pip", "install", "pre-commit"])
    else:
        print("✓ pre-commit is installed")

    # Try to parse pre-commit config
    config_file = ".pre-commit-config.yaml"
    if not os.path.exists(config_file):
        print(f"Error: {config_file} not found")
        return

    try:
        with open(config_file) as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error parsing {config_file}: {e}")
        return

    # Check for local hooks
    local_hooks = []
    for repo in config.get("repos", []):
        if repo.get("repo") == "local":
            for hook in repo.get("hooks", []):
                tool = hook.get("entry")
                if tool and tool != "pytest":  # Skip pytest as it's a Python package
                    local_hooks.append(tool)

    # Check if local hooks are installed
    for tool in local_hooks:
        if shutil.which(tool) is None:
            print(f"{tool} not found. This may cause pre-commit to fail.")

            # Suggest installation methods
            if tool == "pyright":
                print("  To install pyright: npm install -g pyright")
            elif tool == "radon":
                print("  To install radon: pip install radon")
            else:
                print(f"  Please install {tool} to enable the pre-commit hook")
        else:
            print(f"✓ {tool} is installed")


def update_hooks():
    """Update pre-commit hooks to latest versions."""
    print("\n=== Updating pre-commit hooks ===")
    run_command(["pre-commit", "autoupdate"])


def run_safe_hooks():
    """Run pre-commit hooks that are likely to succeed."""
    print("\n=== Running safe pre-commit hooks ===")

    # List of hooks that are likely to succeed or automatically fix issues
    safe_hooks = [
        "trailing-whitespace",
        "end-of-file-fixer",
        "mixed-line-ending",
        "check-merge-conflict",
    ]

    for hook in safe_hooks:
        print(f"\nRunning {hook}...")
        result = run_command(["pre-commit", "run", "--hook-stage", "commit", hook], verbose=False)
        if "Failed" in result.stdout:
            print(result.stdout)
        else:
            print(f"✓ {hook} passed or fixed issues")


def run_with_skip_hooks():
    """Run pre-commit with specific hooks skipped."""
    print("\n=== Running basic pre-commit hooks individually ===")

    # List of basic hooks that are likely to succeed
    basic_hooks = [
        "check-yaml",
        "check-json",
        "check-toml",
        "check-added-large-files",
        "trailing-whitespace",
        "end-of-file-fixer",
        "mixed-line-ending",
        "check-merge-conflict",
        "detect-private-key",
        "debug-statements",
    ]

    for hook in basic_hooks:
        print(f"\nRunning {hook}...")
        result = run_command(["pre-commit", "run", hook, "--all-files"], verbose=False)
        if "Failed" in result.stdout:
            print(result.stdout)
        else:
            print(f"✓ {hook} passed")


def reinstall_hooks():
    """Reinstall pre-commit hooks."""
    print("\n=== Reinstalling pre-commit hooks ===")
    run_command(["pre-commit", "uninstall"])
    run_command(["pre-commit", "install"])
    # Install commit-msg hook specifically for commitizen
    run_command(["pre-commit", "install", "--hook-type", "commit-msg"])


def check_hook_configs():
    """Check for common issues in pre-commit configuration."""
    print("\n=== Checking pre-commit configuration ===")

    config_file = ".pre-commit-config.yaml"
    if not os.path.exists(config_file):
        print(f"Error: {config_file} not found")
        return

    try:
        with open(config_file) as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error parsing {config_file}: {e}")
        return

    # Check for problematic hooks
    problematic_hooks = []

    for repo in config.get("repos", []):
        repo_url = repo.get("repo", "")

        # Check terraform hooks
        if "antonbabenko/pre-commit-terraform" in repo_url:
            terraform_cmd = shutil.which("terraform")
            if not terraform_cmd:
                print("Warning: terraform not found, terraform hooks will fail")
                for hook in repo.get("hooks", []):
                    problematic_hooks.append(hook.get("id", "unknown"))

    if problematic_hooks:
        print(f"Found potentially problematic hooks: {', '.join(problematic_hooks)}")
        print("You may want to remove these hooks or install the required tools")
    else:
        print("✓ No obvious configuration issues found")


def provide_guidance():
    """Provide guidance on fixing other pre-commit errors."""
    print("\n=== Guidance for fixing other pre-commit issues ===")
    print(
        """
Common pre-commit issues and how to fix them:

1. YAML check failures:
   - If they're CloudFormation files with !Ref tags, modify .pre-commit-config.yaml
     to exclude those files from the check-yaml hook.

2. JSON check failures:
   - Ensure JSON files are valid or exclude specific problematic files.

3. Ruff linting issues:
   - Run 'pre-commit run ruff --files <file>' to see specific issues
   - Fix the reported style issues in your code

4. Missing tools:
   - Install missing tools reported in errors
   - Or remove those hooks from .pre-commit-config.yaml

5. Running specific hooks:
   - You can run pre-commit with specific hooks:
     pre-commit run check-yaml --all-files
     pre-commit run check-json --all-files

6. Running on specific files:
   - You can run pre-commit on specific files:
     pre-commit run --files file1.py file2.py

7. Ignoring specific hooks:
   - Add SKIP=hook-id to skip specific hooks:
     SKIP=terraform_validate pre-commit run --all-files

8. Adding exclusions patterns:
   - Modify .pre-commit-config.yaml to add exclude patterns for problematic files:
     exclude: ^path/to/problematic/files/.*$

9. Common tool installations:
   - pyright: npm install -g pyright
   - terraform: Install from https://www.terraform.io/downloads.html
   - radon: pip install radon
   - gitleaks: Install from https://github.com/gitleaks/gitleaks
   - tfcheckov: pip install checkov

To run all pre-commit checks:
  pre-commit run --all-files

To run checks on specific files:
  pre-commit run --files <file1> <file2>

To run a specific hook:
  pre-commit run <hook-id> --files <file>
"""
    )


def main():
    """Main function."""
    print("Pre-commit Fixer Tool")
    print("====================")

    # Perform fixes
    fix_end_of_file_issues()
    check_required_tools()
    check_hook_configs()
    update_hooks()
    run_safe_hooks()
    run_with_skip_hooks()
    reinstall_hooks()
    provide_guidance()

    print("\n=== All done! ===")
    print("Your pre-commit setup should be working better now.")
    print("Try running 'pre-commit run --all-files' to see if there are any remaining issues.")
    print(
        "For specific hooks that fail, consider adding them to .pre-commit-config.yaml's ci.skip section."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
