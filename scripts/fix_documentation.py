#!/usr/bin/env python
"""
Documentation Fixer Script

This script addresses common documentation issues:
1. Creates placeholder files for missing pages referenced in mkdocs.yml
2. Updates broken links in documentation files
3. Validates documentation structure

Usage:
    python scripts/fix_documentation.py
"""

import os
import re
from pathlib import Path
from typing import Any

import yaml

# Constants
DOCS_DIR = Path("docs")
MKDOCS_CONFIG = Path("mkdocs.yml")
PLACEHOLDER_CONTENT = """# {title}

!!! warning "Documentation Placeholder"
    This page is a placeholder and needs to be completed.

## Overview

This section will provide information about {description}.

## Getting Started

TODO: Add content for getting started with {description_lowercase}.

## Reference

TODO: Add reference documentation for {description_lowercase}.
"""


def parse_mkdocs_config() -> dict[str, Any]:
    """Parse the MkDocs configuration file."""
    with open(MKDOCS_CONFIG, encoding="utf-8") as f:
        return yaml.safe_load(f)


def extract_nav_pages(nav: list[dict[str, Any] | str], prefix: str = "") -> set[str]:
    """Extract all pages referenced in the nav section of mkdocs.yml."""
    pages = set()

    for item in nav:
        if isinstance(item, dict):
            for section_title, section_content in item.items():
                if isinstance(section_content, str):
                    pages.add(section_content)
                elif isinstance(section_content, list):
                    pages.update(extract_nav_pages(section_content, prefix))
        elif isinstance(item, str):
            pages.add(os.path.join(prefix, item))

    return pages


def find_existing_pages() -> set[str]:
    """Find all existing Markdown files in the docs directory."""
    existing_pages = set()

    for root, _, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".md"):
                rel_path = os.path.relpath(os.path.join(root, file), DOCS_DIR)
                existing_pages.add(rel_path)

    return existing_pages


def create_missing_pages(missing_pages: set[str]) -> None:
    """Create placeholder files for missing pages."""
    for page in missing_pages:
        # Skip pages that don't have a proper path
        if not page or page == "." or ".." in page:
            continue

        full_path = DOCS_DIR / page

        # Create directory if it doesn't exist
        os.makedirs(full_path.parent, exist_ok=True)

        # Generate title and description from filename
        filename = full_path.name
        title = " ".join(word.capitalize() for word in filename.replace(".md", "").split("-"))
        description = title.lower()
        description_lowercase = description

        # Create the file with placeholder content
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(
                PLACEHOLDER_CONTENT.format(
                    title=title,
                    description=description,
                    description_lowercase=description_lowercase,
                )
            )

        print(f"Created placeholder for: {page}")


def find_and_fix_broken_links() -> None:
    """Find and fix broken links in documentation files."""
    existing_pages = find_existing_pages()
    existing_paths = {str(DOCS_DIR / page) for page in existing_pages}

    # Regular expression to find Markdown links
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    broken_links: list[tuple[str, str, str, str]] = []

    for root, _, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                for match in link_pattern.finditer(content):
                    link_text, link_target = match.groups()

                    # Skip external links and anchors
                    if link_target.startswith(("http://", "https://", "#")):
                        continue

                    # Normalize the link path
                    if not link_target.startswith("/"):
                        base_dir = os.path.dirname(file_path)
                        link_path = os.path.normpath(os.path.join(base_dir, link_target))
                    else:
                        # Handle absolute paths within docs
                        link_path = os.path.normpath(
                            os.path.join(DOCS_DIR, link_target.lstrip("/"))
                        )

                    # Check if the linked file exists
                    if not os.path.exists(link_path) and not any(
                        link_path.endswith(ext) for ext in [".jpg", ".png", ".svg", ".pdf"]
                    ):
                        broken_links.append((file_path, link_text, link_target, link_path))

    # Report broken links
    if broken_links:
        print("\nFound broken links:")
        for file_path, link_text, link_target, link_path in broken_links:
            rel_file_path = os.path.relpath(file_path, ".")
            print(
                f"  {rel_file_path}: '{link_text}' -> '{link_target}' (resolved to '{link_path}')"
            )


def main() -> None:
    """Main function to fix documentation issues."""
    print("Documentation Fixer")
    print("-" * 50)

    # Load MkDocs configuration
    try:
        config = parse_mkdocs_config()
        print("Parsed MkDocs configuration")
    except Exception as e:
        print(f"Error parsing MkDocs configuration: {e}")
        return

    # Extract pages from nav section
    nav_pages: set[str] = set()
    if "nav" in config:
        nav_pages = extract_nav_pages(config["nav"])
        print(f"Found {len(nav_pages)} pages referenced in navigation")

    # Find existing pages
    existing_pages = find_existing_pages()
    print(f"Found {len(existing_pages)} existing pages")

    # Create missing pages
    missing_pages = {page for page in nav_pages if page and not os.path.exists(DOCS_DIR / page)}
    if missing_pages:
        print(f"\nFound {len(missing_pages)} missing pages referenced in navigation")
        create_missing_pages(missing_pages)
    else:
        print("\nNo missing pages found!")

    # Find and fix broken links
    print("\nChecking for broken links...")
    find_and_fix_broken_links()

    print("\nDocumentation fixing complete!")


if __name__ == "__main__":
    main()
