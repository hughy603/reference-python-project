#!/usr/bin/env python3
"""
This script cleans up obsolete files and directories in the repository
based on the completed tasks in the TODO.md file.
"""

import shutil
from pathlib import Path

# Repository root directory
REPO_ROOT = Path(__file__).parent.parent


def get_files_to_remove() -> list[str]:
    """
    Returns a list of files that should be removed from the repository.
    """
    files_to_remove = [
        # Check for Sphinx-specific files
        "docs/sphinx",
        # Check for empty workflow files from TODO.md
        ".github/workflows/docs-generate.yml",
        ".github/workflows/docs-generate-simple.yml",
        ".github/workflows/docs-generate-new.yml",
        ".github/workflows/infrastructure-validation.yml",
        ".github/workflows/ci_backup.yml",
        # Check for duplicate pre-commit config
        ".pre-commit-config-simple.yaml",
        # Check for your_package directory
        "src/your_package",
    ]

    return files_to_remove


def get_references_to_update() -> dict[str, tuple[str, str]]:
    """
    Returns a dictionary of files and the references that should be updated.
    The tuple contains (old_reference, new_reference).
    """
    references = {
        "docs/python/python312-features.md": (
            "src/your_package/",
            "src/enterprise_data_engineering/",
        ),
        "docs/user-guide/multi-version-testing.md": (
            "src/your_package/",
            "src/enterprise_data_engineering/",
        ),
        "docs/user-guide/multi-version-testing.md": (
            "your_package.compat",
            "enterprise_data_engineering.compat",
        ),
        "src/enterprise_data_engineering/examples/version_specific.py": (
            "your_package.compat",
            "enterprise_data_engineering.compat",
        ),
    }

    return references


def clean_up_files(files_to_remove: list[str]) -> None:
    """
    Removes the specified files and directories.
    """
    for file_path in files_to_remove:
        full_path = REPO_ROOT / file_path
        if full_path.exists():
            print(f"Removing: {file_path}")
            if full_path.is_dir():
                shutil.rmtree(full_path)
            else:
                full_path.unlink()
        else:
            print(f"Not found: {file_path}")


def update_references(references: dict[str, tuple[str, str]]) -> None:
    """
    Updates references in files.
    """
    for file_path, (old_ref, new_ref) in references.items():
        full_path = REPO_ROOT / file_path
        if full_path.exists():
            print(f"Updating references in: {file_path}")
            content = full_path.read_text()
            updated_content = content.replace(old_ref, new_ref)
            full_path.write_text(updated_content)
        else:
            print(f"Not found: {file_path}")


def main() -> None:
    """
    Main function to clean up the repository.
    """
    print("Starting repository cleanup...")

    # Get files to remove
    files_to_remove = get_files_to_remove()

    # Get references to update
    references = get_references_to_update()

    # Clean up files
    clean_up_files(files_to_remove)

    # Update references
    update_references(references)

    print("Repository cleanup complete!")


if __name__ == "__main__":
    main()
