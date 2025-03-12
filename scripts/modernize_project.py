#!/usr/bin/env python3
"""
Script to modernize the project structure by identifying potentially redundant
files and suggesting updates based on modern Python project practices.
"""

from pathlib import Path

# Repository root directory
REPO_ROOT = Path(__file__).parent.parent

# Files that may be redundant in modern Python projects
POTENTIALLY_REDUNDANT_FILES = [
    # Modern Python projects use pyproject.toml as the single source of truth
    # setup.py is kept for backward compatibility but can be simplified
    ("setup.py", "Check if setup.py is needed or can be simplified"),
    # Files that might be redundant if their functionality is in pyproject.toml
    ("tox.ini", "Check if tox configuration has been moved to pyproject.toml"),
    ("requirements.txt", "Check if requirements.txt is just a reference to pyproject.toml"),
    # Directory that should be cleaned up
    (".venv", "Consider if this venv directory should be deleted (developer-specific)"),
    ("docs-venv", "Consider if this venv directory should be deleted (developer-specific)"),
    # Obsolete workflow files that might still exist
    (".github/workflows/docs-generate.yml", "Remove if obsolete"),
    (".github/workflows/docs-generate-simple.yml", "Remove if obsolete"),
    (".github/workflows/docs-generate-new.yml", "Remove if obsolete"),
    (".github/workflows/infrastructure-validation.yml", "Remove if obsolete"),
    (".github/workflows/ci_backup.yml", "Remove if obsolete"),
]


def check_pyproject_toml() -> None:
    """
    Check if pyproject.toml contains all necessary configuration and suggest improvements.
    """
    pyproject_path = REPO_ROOT / "pyproject.toml"
    if not pyproject_path.exists():
        print("ERROR: pyproject.toml not found!")
        return

    # Check if all standard sections are present
    required_sections = ["[build-system]", "[project]", "[tool.ruff]", "[tool.mypy]"]

    content = pyproject_path.read_text()

    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)

    if missing_sections:
        print("\nWarning: Missing sections in pyproject.toml:")
        for section in missing_sections:
            print(f"  - {section}")


def check_redundant_files() -> None:
    """
    Check for redundant files and suggest actions.
    """
    print("\nChecking for potentially redundant files:")

    for file_path, suggestion in POTENTIALLY_REDUNDANT_FILES:
        full_path = REPO_ROOT / file_path
        if full_path.exists():
            print(f"  - {file_path}: {suggestion}")


def check_github_workflows() -> None:
    """
    Check GitHub workflows for consolidation opportunities.
    """
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    if not workflows_dir.exists():
        return

    workflow_files = list(workflows_dir.glob("*.yml"))

    if len(workflow_files) > 5:
        print(
            f"\nConsider consolidating GitHub workflows - found {len(workflow_files)} workflow files."
        )
        print("Modern practice suggests fewer, more comprehensive workflows.")


def main() -> None:
    """
    Main function to check for modernization opportunities.
    """
    print("Checking for modernization opportunities...")

    # Check pyproject.toml
    check_pyproject_toml()

    # Check redundant files
    check_redundant_files()

    # Check GitHub workflows
    check_github_workflows()

    print("\nCompleted modernization check. Review the suggestions above.")
    print("Note: No files have been modified. This is just an analysis.")


if __name__ == "__main__":
    main()
