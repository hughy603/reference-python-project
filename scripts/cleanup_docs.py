#!/usr/bin/env python3
"""
This script identifies and optionally removes documentation files that are not
referenced in the mkdocs.yml configuration.
"""

import os
from pathlib import Path
from typing import Any

import yaml

# Repository root directory
REPO_ROOT = Path(__file__).parent.parent


def read_mkdocs_config(config_file: str | Path) -> dict[str, Any]:
    """
    Reads the mkdocs.yml configuration file.

    Args:
        config_file: Path to the mkdocs.yml file

    Returns:
        The parsed configuration as a dictionary
    """
    with open(config_file) as f:
        return yaml.safe_load(f)


def extract_referenced_files(
    nav: Any, base_path: str = "docs", result: set[str] | None = None
) -> set[str]:
    """
    Recursively extracts files referenced in the mkdocs navigation.

    Args:
        nav: The navigation section from mkdocs.yml
        base_path: The base path for documentation files
        result: Set to collect referenced files

    Returns:
        Set of referenced files
    """
    if result is None:
        result = set()

    if isinstance(nav, list):
        for item in nav:
            extract_referenced_files(item, base_path, result)
    elif isinstance(nav, dict):
        for key, value in nav.items():
            if isinstance(value, str) and value.endswith(".md"):
                # Add the file path with base_path prefix
                file_path = os.path.join(base_path, value)
                result.add(file_path)
            else:
                extract_referenced_files(value, base_path, result)

    return result


def find_md_files(directory: str | Path) -> set[str]:
    """
    Finds all markdown files in the specified directory and its subdirectories.

    Args:
        directory: Directory to search for markdown files

    Returns:
        Set of markdown file paths
    """
    directory = Path(directory)
    files = set()

    for root, _, filenames in os.walk(directory):
        root_path = Path(root)
        for filename in filenames:
            if filename.endswith(".md"):
                file_path = str(root_path / filename)
                files.add(file_path)

    return files


def find_obsolete_files(all_files: set[str], referenced_files: set[str]) -> set[str]:
    """
    Identifies files that are not referenced in the mkdocs configuration.

    Args:
        all_files: Set of all markdown files
        referenced_files: Set of files referenced in mkdocs.yml

    Returns:
        Set of unreferenced files
    """
    return all_files - referenced_files


def main() -> None:
    """
    Main function to clean up unreferenced documentation files.
    """
    print("Checking for unreferenced documentation files...")

    # Read mkdocs configuration
    config_file = REPO_ROOT / "mkdocs.yml"
    config = read_mkdocs_config(config_file)

    # Extract referenced files
    referenced_files = extract_referenced_files(config.get("nav", []))
    print(f"Found {len(referenced_files)} referenced files in mkdocs.yml")

    # Find all markdown files
    docs_dir = REPO_ROOT / "docs"
    all_md_files = find_md_files(docs_dir)
    print(f"Found {len(all_md_files)} total markdown files in docs/")

    # Find obsolete files
    obsolete_files = find_obsolete_files(all_md_files, referenced_files)
    print(f"Found {len(obsolete_files)} unreferenced documentation files")

    if obsolete_files:
        print("\nUnreferenced files:")
        for file_path in sorted(obsolete_files):
            print(f"  - {os.path.relpath(file_path, REPO_ROOT)}")

        # Ask user if they want to delete these files
        choice = input("\nDo you want to delete these unreferenced files? (y/N): ").strip().lower()

        if choice == "y":
            for file_path in obsolete_files:
                print(f"Deleting: {os.path.relpath(file_path, REPO_ROOT)}")
                os.remove(file_path)
            print("\nDeletion complete!")
        else:
            print("\nNo files were deleted.")
    else:
        print("No unreferenced documentation files found.")

    # Print a summary of referenced files for debugging
    print("\nReferenced files in mkdocs.yml:")
    for file_path in sorted(referenced_files):
        print(f"  - {os.path.relpath(file_path, REPO_ROOT)}")


if __name__ == "__main__":
    main()
