#!/usr/bin/env python
"""
Cleanup script to remove unused directories and files from the project.

This script removes directories and files that are no longer needed,
consolidates documentation, and ensures the project structure is clean.
"""

import logging
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

# Directories to be removed
DIRECTORIES_TO_REMOVE = [
    # Build and cache directories that can be regenerated
    "htmlcov",
    "site",
    "docs-venv",
    ".ruff_cache",
    ".pytest_cache",
    # Empty or unused documentation directories
    "docs/examples",  # Content moved to examples directory
]

# Files to be removed (relative to project root)
FILES_TO_REMOVE = [
    # Test coverage files that can be regenerated
    "junit.xml",
    ".coverage",
    "coverage.xml",
]


def confirm_deletion(path):
    """Ask for confirmation before deleting a path."""
    response = input(f"Delete {path}? [y/N]: ").lower()
    return response in ["y", "yes"]


def delete_path(path, dry_run=False):
    """Delete a file or directory."""
    if not path.exists():
        logger.info(f"Path does not exist: {path}")
        return

    if dry_run:
        logger.info(f"Would delete: {path}")
        return

    try:
        if path.is_dir():
            shutil.rmtree(path)
            logger.info(f"Deleted directory: {path}")
        else:
            path.unlink()
            logger.info(f"Deleted file: {path}")
    except Exception as e:
        logger.error(f"Failed to delete {path}: {e}")


def main(dry_run=False, no_confirm=False):
    """Execute the cleanup process."""
    # Delete directories
    for dir_path in DIRECTORIES_TO_REMOVE:
        path = PROJECT_ROOT / dir_path
        if path.exists():
            if dry_run or no_confirm or confirm_deletion(path):
                delete_path(path, dry_run)

    # Delete files
    for file_path in FILES_TO_REMOVE:
        path = PROJECT_ROOT / file_path
        if path.exists():
            if dry_run or no_confirm or confirm_deletion(path):
                delete_path(path, dry_run)

    logger.info("Cleanup complete!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clean up unused project directories and files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    parser.add_argument("--no-confirm", action="store_true", help="Delete without confirmation")

    args = parser.parse_args()

    main(dry_run=args.dry_run, no_confirm=args.no_confirm)
