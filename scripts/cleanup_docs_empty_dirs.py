#!/usr/bin/env python
"""
Cleanup script for empty directories under docs/.

This script identifies and removes empty directories within the docs/ folder
to simplify documentation maintenance and navigation.
"""

import logging
import os
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DOCS_DIR = PROJECT_ROOT / "docs"

# List of directories to check for removal
# If it's empty or only contains empty directories, it will be removed
DIRECTORIES_TO_CHECK = [
    # Directories we identified as empty
    "examples",
    "infrastructure",
    "user-guide",
    "api",
    "python",
    "windows",
    "architecture/well-architected",
    "development/enterprise",
    "development/python",
    "development/terraform",
    "development/vscode",
    "reference/data_pipelines",
    "reference/examples",
    "reference/spark",
    "reference/common_utils",
    "reference/terraform",
]


def is_dir_empty(path):
    """Check if a directory is empty or contains only empty directories."""
    if not path.is_dir():
        return False

    # Check if directory has no files or subdirectories
    if not os.listdir(path):
        return True

    # Check if it only contains empty directories
    contains_only_empty_dirs = True
    for item in path.iterdir():
        if item.is_file():
            contains_only_empty_dirs = False
            break
        if item.is_dir() and not is_dir_empty(item):
            contains_only_empty_dirs = False
            break

    return contains_only_empty_dirs


def confirm_deletion(path):
    """Ask for confirmation before deleting a path."""
    response = input(f"Delete empty directory {path}? [y/N]: ").lower()
    return response in ["y", "yes"]


def remove_empty_dir(dir_path, dry_run=False, no_confirm=False):
    """Remove directory if it's empty."""
    path = DOCS_DIR / dir_path

    if not path.exists():
        logger.info(f"Directory does not exist: {path}")
        return

    if is_dir_empty(path):
        if dry_run:
            logger.info(f"Would delete empty directory: {path}")
            return

        if no_confirm or confirm_deletion(path):
            try:
                shutil.rmtree(path)
                logger.info(f"Deleted empty directory: {path}")

                # Check if parent directory is now empty
                parent = path.parent
                if parent != DOCS_DIR and is_dir_empty(parent):
                    if no_confirm or confirm_deletion(parent):
                        shutil.rmtree(parent)
                        logger.info(f"Deleted parent directory (now empty): {parent}")

            except Exception as e:
                logger.error(f"Failed to delete {path}: {e}")
    else:
        logger.info(f"Directory is not empty: {path}")


def main(dry_run=False, no_confirm=False):
    """Execute the cleanup process for empty directories."""
    logger.info("Starting cleanup of empty directories in docs/...")

    for dir_path in DIRECTORIES_TO_CHECK:
        remove_empty_dir(dir_path, dry_run, no_confirm)

    # After removing known empty dirs, find any remaining empty dirs
    for root, dirs, files in os.walk(DOCS_DIR, topdown=False):
        root_path = Path(root)
        if root_path != DOCS_DIR and is_dir_empty(root_path):
            relative_path = root_path.relative_to(DOCS_DIR)
            logger.info(f"Found additional empty directory: {relative_path}")
            if no_confirm or confirm_deletion(root_path):
                try:
                    shutil.rmtree(root_path)
                    logger.info(f"Deleted additional empty directory: {root_path}")
                except Exception as e:
                    logger.error(f"Failed to delete {root_path}: {e}")

    logger.info("Cleanup of empty directories in docs/ complete!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clean up empty directories in docs/")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    parser.add_argument("--no-confirm", action="store_true", help="Delete without confirmation")

    args = parser.parse_args()

    main(dry_run=args.dry_run, no_confirm=args.no_confirm)
