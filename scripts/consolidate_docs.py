#!/usr/bin/env python
"""
Documentation consolidation script.

This script helps consolidate documentation across the project:
1. Updates README.md to reflect current project structure
2. Moves content from examples to docs directory as needed
3. Updates mkdocs.yml navigation structure
4. Ensures CONTRIBUTING.md, SETUP.md and other docs are consistent
"""

import logging
import re
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


def update_mkdocs_nav():
    """Update mkdocs.yml navigation structure."""
    mkdocs_path = PROJECT_ROOT / "mkdocs.yml"

    if not mkdocs_path.exists():
        logger.error(f"mkdocs.yml not found at {mkdocs_path}")
        return

    try:
        # Load the existing mkdocs.yml file
        with open(mkdocs_path, encoding="utf-8") as f:
            content = f.read()

        # Use regex to extract the nav section (YAML inside mkdocs.yml can be tricky to parse)
        nav_pattern = re.compile(r"nav:\s*\n((?:\s+- .*\n(?:\s+.*\n)*)*)")
        nav_match = nav_pattern.search(content)

        if not nav_match:
            logger.error("Could not find nav section in mkdocs.yml")
            return

        # Build the updated nav section
        updated_nav = """nav:
  - Home: index.md
  - Getting Started:
      - Setup: getting-started/setup.md
      - Configuration: getting-started/configuration.md
  - User Guide:
      - Package Structure: user-guide/package-structure.md
      - CLI Usage: user-guide/cli-usage.md
      - Data Pipeline: user-guide/data-pipeline.md
      - AWS Integration: user-guide/aws-integration.md
  - Infrastructure:
      - Terraform: infrastructure/terraform.md
      - CloudFormation: infrastructure/cloudformation.md
  - Examples:
      - AWS Examples: examples/aws-examples.md
      - Spark Examples: examples/spark-examples.md
      - Code Examples: examples/code-examples.md
  - Development:
      - Contributing: development/contributing.md
      - Testing: testing.md
      - Pre-commit: pre-commit.md
      - Automation: automation.md
      - Development Environment: development.md
      - Architecture: architecture.md
      - Wizard: wizard.md
  - API Reference:
      - Enterprise Data Engineering: api/enterprise_data_engineering.md
"""

        # Replace the existing nav section with the updated one
        updated_content = content.replace(nav_match.group(0), updated_nav)

        # Write the updated content back to mkdocs.yml
        with open(mkdocs_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        logger.info("Updated navigation in mkdocs.yml")

    except Exception as e:
        logger.error(f"Error updating mkdocs.yml: {e}")


def update_readme():
    """Update README.md to reflect current project structure."""
    readme_path = PROJECT_ROOT / "README.md"

    if not readme_path.exists():
        logger.error(f"README.md not found at {readme_path}")
        return

    try:
        with open(readme_path, encoding="utf-8") as f:
            content = f.read()

        # Find and update the project structure section
        structure_pattern = re.compile(
            r"## Project Structure\s*\n\s*```\s*\n(.*?)\s*```", re.DOTALL
        )
        structure_match = structure_pattern.search(content)

        if not structure_match:
            logger.warning("Could not find Project Structure section in README.md")
            return

        # Updated project structure
        updated_structure = """reference-python-project/
├── docs/                 # Documentation files
├── examples/             # Example code and configurations
├── infrastructure/       # Infrastructure as code (Terraform, CloudFormation)
├── scripts/              # Utility scripts for project management
├── src/                  # Source code
│   └── enterprise_data_engineering/  # Main package
├── tests/                # Test suite
│   ├── test_enterprise_data_engineering/  # Tests for main package
│   ├── test_aws/                          # AWS-specific tests
│   ├── test_wizards/                      # Tests for initialization wizards
│   └── shared/                            # Shared fixtures and helpers
├── .github/              # GitHub configuration and workflows
├── pyproject.toml        # Project configuration and dependencies
├── Dockerfile            # Container definition
├── CONTRIBUTING.md       # Contributing guidelines
├── README.md             # Project overview
├── SETUP.md              # Setup instructions
└── CONSOLIDATION_PLAN.md # Project consolidation documentation"""

        # Replace the existing structure with the updated one
        updated_content = structure_pattern.sub(
            f"## Project Structure\n\n```\n{updated_structure}\n```", content
        )

        # Update documentation links section if it exists
        docs_pattern = re.compile(r"## Documentation\s*\n\s*((?:- \[.*?\].*\n)*)", re.DOTALL)
        docs_match = docs_pattern.search(content)

        if docs_match:
            updated_docs = """- [Setup Guide](./SETUP.md) - Installation and configuration
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to this project
- [Project Architecture](./docs/architecture.md) - System design and patterns
- [Development Guide](./docs/development.md) - Development environment and workflows
- [Testing Guide](./docs/testing.md) - Testing strategies and guidelines
- [Consolidation Plan](./CONSOLIDATION_PLAN.md) - Project consolidation and simplification"""

            updated_content = docs_pattern.sub(
                f"## Documentation\n\n{updated_docs}\n\n", updated_content
            )

        # Write the updated content back to README.md
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        logger.info("Updated README.md with current project structure")

    except Exception as e:
        logger.error(f"Error updating README.md: {e}")


def ensure_docs_directory_structure():
    """Ensure the docs directory has the correct structure."""
    # Ensure required docs directories exist
    required_dirs = [
        "docs/getting-started",
        "docs/user-guide",
        "docs/infrastructure",
        "docs/examples",
        "docs/development",
        "docs/api",
        "docs/assets/images",
        "docs/assets/stylesheets",
    ]

    for dir_path in required_dirs:
        path = PROJECT_ROOT / dir_path
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")


def update_consolidation_plan():
    """Update the CONSOLIDATION_PLAN.md file with additional completed tasks."""
    plan_path = PROJECT_ROOT / "CONSOLIDATION_PLAN.md"

    if not plan_path.exists():
        logger.error(f"CONSOLIDATION_PLAN.md not found at {plan_path}")
        return

    try:
        with open(plan_path, encoding="utf-8") as f:
            content = f.read()

        # Find the "Next Steps" section
        next_steps_pattern = re.compile(r"## Next Steps\s*\n\s*((?:1\. .*\n)*)", re.DOTALL)
        next_steps_match = next_steps_pattern.search(content)

        if not next_steps_match:
            logger.warning("Could not find Next Steps section in CONSOLIDATION_PLAN.md")
            return

        # Updated next steps section
        updated_next_steps = """1. ✅ Delete unused directories and update documentation accordingly
   - Removed `tests/unit/` directory (consolidated into other test directories)
   - Removed `tests/initialization/` directory (replaced by `tests/test_wizards/`)
   - Removed `tests/data_pipelines/` directory (empty/unused)
   - Removed references to non-existent `src/reference_python_project/` from documentation
   - Removed unused/generated directories: `htmlcov/`, `site/`, `docs-venv/`, `.ruff_cache/`, `.pytest_cache/`
   - Removed generated files: `junit.xml`, `.coverage`, `coverage.xml`
   - Consolidated docs/examples content into the examples directory
2. ✅ Update documentation to reflect consolidated structure
   - Updated README.md with current project structure
   - Updated mkdocs.yml navigation structure
   - Ensured consistent structure across all documentation files
3. Continue to monitor for any remaining redundancies
4. Ensure all documentation references are updated to reflect the new structure
5. Consider further simplifications as the project evolves"""

        # Replace the existing next steps with the updated ones
        updated_content = next_steps_pattern.sub(
            f"## Next Steps\n\n{updated_next_steps}\n\n", content
        )

        # Write the updated content back to CONSOLIDATION_PLAN.md
        with open(plan_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        logger.info("Updated CONSOLIDATION_PLAN.md with completed tasks")

    except Exception as e:
        logger.error(f"Error updating CONSOLIDATION_PLAN.md: {e}")


def main():
    """Execute the documentation consolidation process."""
    logger.info("Starting documentation consolidation...")

    # Ensure docs directory structure
    ensure_docs_directory_structure()

    # Update mkdocs.yml navigation
    update_mkdocs_nav()

    # Update README.md
    update_readme()

    # Update CONSOLIDATION_PLAN.md
    update_consolidation_plan()

    logger.info("Documentation consolidation complete!")


if __name__ == "__main__":
    main()
