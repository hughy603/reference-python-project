#!/usr/bin/env python3
"""
Script to identify and delete specific obsolete files based on the completed tasks in TODO.md.
"""

import os
import shutil
from pathlib import Path

# Repository root directory
REPO_ROOT = Path(__file__).parent.parent

# List of files to check for deletion based on completed tasks in TODO.md
OBSOLETE_FILES = [
    # Documentation files that might be obsolete or redundant
    "docs/GETTING_STARTED.md",
    "docs/CODE_COVERAGE.md",
    "docs/enterprise-governance.md",
    "docs/spark_development_guide.md",
    # Files mentioned in TODO.md as completed tasks
    "docs/sphinx",
    ".github/workflows/docs-generate.yml",
    ".github/workflows/docs-generate-simple.yml",
    ".github/workflows/docs-generate-new.yml",
    ".github/workflows/infrastructure-validation.yml",
    ".github/workflows/ci_backup.yml",
    ".pre-commit-config-simple.yaml",
    "src/your_package",
    # Redundant files that have moved to a standard structure
    "QUICKREF.md",
    "SETUP_GUIDE.md",
    "AWS_DEVELOPMENT.md",
]

# Files to be checked if their content is now in the mkdocs structure
POTENTIALLY_OBSOLETE_FILES = [
    "CONTRIBUTING.md",  # moved to docs/contributing.md
    "README.md",  # main content might be in docs/index.md
]


def check_and_delete_file(file_path: str) -> bool:
    """
    Check if a file exists and delete it if found.

    Args:
        file_path: Path to the file to check and delete

    Returns:
        True if the file was found and deleted, False otherwise
    """
    full_path = REPO_ROOT / file_path
    if full_path.exists():
        print(f"Found obsolete file: {file_path}")
        if full_path.is_dir():
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        print(f"Deleted: {file_path}")
        return True
    return False


def validate_potentially_obsolete(file_path: str) -> bool:
    """
    Validate if a file is potentially obsolete by checking if its corresponding
    mkdocs file exists.

    Args:
        file_path: Path to the file to check

    Returns:
        True if the file should be considered obsolete, False otherwise
    """
    # Mapping of potentially obsolete files to their corresponding mkdocs files
    file_mapping = {
        "CONTRIBUTING.md": "docs/contributing.md",
        "README.md": "docs/index.md",
    }

    if file_path not in file_mapping:
        return False

    # Check if the corresponding file exists
    corresponding_file = REPO_ROOT / file_mapping[file_path]
    if corresponding_file.exists():
        # Check if contents are similar (simple check - file size comparison)
        original_file = REPO_ROOT / file_path
        if original_file.exists():
            original_size = original_file.stat().st_size
            corresponding_size = corresponding_file.stat().st_size

            # If the sizes are roughly similar (within 25%), consider it obsolete
            size_ratio = abs(original_size - corresponding_size) / max(
                original_size, corresponding_size
            )
            if size_ratio < 0.25:
                return True

    return False


def main() -> None:
    """
    Main function to identify and delete obsolete files.
    """
    print("Checking for obsolete files...")

    deleted_count = 0

    # Check and delete obsolete files
    for file_path in OBSOLETE_FILES:
        if check_and_delete_file(file_path):
            deleted_count += 1

    # Check potentially obsolete files
    for file_path in POTENTIALLY_OBSOLETE_FILES:
        if validate_potentially_obsolete(file_path):
            if check_and_delete_file(file_path):
                deleted_count += 1
        else:
            print(f"File is still needed: {file_path}")

    if deleted_count > 0:
        print(f"\nDeleted {deleted_count} obsolete files.")
    else:
        print("\nNo obsolete files found that need to be deleted.")


if __name__ == "__main__":
    main()
