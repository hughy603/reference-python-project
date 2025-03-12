#!/usr/bin/env python3
"""
Script to identify documentation files that are not referenced in mkdocs.yml.
These files might be candidates for removal or consolidation.
"""

import os
from pathlib import Path
from typing import Any, Union

import yaml

NavItem = Union[list[Any], dict[str, Any], str]


def extract_md_files_from_nav(nav: NavItem, result: set[str] | None = None) -> set[str]:
    """Recursively extract all markdown files referenced in the navigation."""
    if result is None:
        result = set()

    if isinstance(nav, list):
        for item in nav:
            extract_md_files_from_nav(item, result)
    elif isinstance(nav, dict):
        for _, value in nav.items():
            extract_md_files_from_nav(value, result)
    elif isinstance(nav, str) and nav.endswith(".md"):
        result.add(nav)

    return result


def find_all_md_files(base_dir: str | Path) -> set[str]:
    """Find all markdown files in the docs directory."""
    md_files = set()

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".md"):
                rel_path = os.path.relpath(os.path.join(root, file), base_dir)
                rel_path = rel_path.replace("\\", "/")  # Normalize path separators for Windows
                md_files.add(rel_path)

    return md_files


def main() -> None:
    """Main function to find unreferenced markdown files."""
    project_root = Path(__file__).parent.parent.absolute()
    docs_dir = project_root / "docs"
    mkdocs_file = project_root / "mkdocs.yml"

    print(f"Scanning documentation in: {docs_dir}")

    # Load the MkDocs configuration
    with open(mkdocs_file) as f:
        mkdocs_config = yaml.safe_load(f)

    # Extract all referenced markdown files
    nav = mkdocs_config.get("nav", [])
    referenced_files = extract_md_files_from_nav(nav)

    # Find all markdown files in the docs directory
    all_md_files = find_all_md_files(docs_dir)

    # Find unreferenced files
    unreferenced_files = all_md_files - set(referenced_files)

    if unreferenced_files:
        print("\nUnreferenced documentation files:")
        for file in sorted(unreferenced_files):
            full_path = docs_dir / file
            print(f"- {file}")

        print(f"\nFound {len(unreferenced_files)} unreferenced documentation files.")
        print(
            "Consider adding these to the navigation, consolidating with other documents, or removing them."
        )
    else:
        print("\nNo unreferenced documentation files found.")

    # Check for missing files
    missing_files = set(referenced_files) - all_md_files
    if missing_files:
        print("\nWarning: The following files are referenced in mkdocs.yml but don't exist:")
        for file in sorted(missing_files):
            print(f"- {file}")


if __name__ == "__main__":
    main()
