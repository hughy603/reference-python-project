# Consolidation Plan

This document outlines the consolidation work completed to simplify the project structure and
configuration.

## Completed Consolidation Tasks

### Configuration Consolidation

- [x] Simplified pyproject.toml by removing redundant configurations
  - Consolidated dependency sections to avoid duplication
  - Removed redundant environment configurations
  - Standardized tool configurations
- [x] Consolidated pre-commit configuration
  - Simplified hook configurations
  - Removed redundant comments
  - Ensured consistent formatting
- [x] Removed redundant configuration files
  - Deleted tox.ini (moved configuration to pyproject.toml)
  - Removed setup.py (using pyproject.toml for build configuration)
  - Deleted requirements.txt (using pyproject.toml for dependency management)
  - Removed pyrightconfig.json (using pyproject.toml for type checking configuration)
  - Deleted .bandit (using pyproject.toml for security scanning configuration)

### Testing and CI/CD Improvements

- [x] Simplified test structure
  - Reorganized tests into logical directories (test_enterprise_data_engineering, test_aws,
    test_wizards)
  - Created a shared directory for common test fixtures and utilities
  - Added a README.md to explain the test structure
- [x] Consolidated GitHub Actions workflows
  - Created a single comprehensive CI/CD pipeline workflow
  - Removed redundant workflows
  - Ensured consistent configuration across workflow steps

### Final Cleanup

- [x] Removed redundant files
  - Deleted duplicate configuration files
  - Removed redundant GitHub Actions workflows (iac-ci.yml)
- [x] Updated documentation references
  - Updated README.md to reflect the consolidated structure
  - Updated SETUP.md to reference consolidated configuration
  - Updated docs/development.md to reflect consolidated configuration
  - Updated docs/pre-commit.md to reference pyproject.toml
  - Updated docs/testing.md to reflect the new test structure
  - Created this CONSOLIDATION_PLAN.md to document the consolidation work

## Benefits of Consolidation

1. **Simplified Configuration**: Single source of truth for configuration in pyproject.toml
1. **Reduced Maintenance Overhead**: Fewer files to maintain and update
1. **Improved Developer Experience**: Clearer project structure and configuration
1. **Better CI/CD Pipeline**: Consolidated workflows for faster and more reliable CI/CD
1. **Standardized Testing**: Consistent test structure and organization
1. **Improved Documentation**: Documentation now accurately reflects the consolidated project
   structure

## Next Steps

1. ✅ Delete unused directories and update documentation accordingly
   - Removed `tests/unit/` directory (consolidated into other test directories)
   - Removed `tests/initialization/` directory (replaced by `tests/test_wizards/`)
   - Removed `tests/data_pipelines/` directory (empty/unused)
   - Removed references to non-existent `src/reference_python_project/` from documentation
   - Removed unused/generated directories: `htmlcov/`, `site/`, `docs-venv/`, `.ruff_cache/`,
     `.pytest_cache/`
   - Removed generated files: `junit.xml`, `.coverage`, `coverage.xml`
   - Consolidated docs/examples content into the examples directory
1. ✅ Update documentation to reflect consolidated structure
   - Updated README.md with current project structure
   - Updated mkdocs.yml navigation structure
   - Ensured consistent structure across all documentation files
1. ✅ Remove empty directories under docs/
   - Deleted empty directories: `docs/examples/`, `docs/infrastructure/`, `docs/user-guide/`,
     `docs/api/`, `docs/python/`, `docs/windows/`
   - Deleted empty directory trees: `docs/architecture/`, `docs/development/`, `docs/reference/`
   - Created scripts for automatically identifying and cleaning up empty directories
1. Continue to monitor for any remaining redundancies
1. Ensure all documentation references are updated to reflect the new structure
1. Consider further simplifications as the project evolves
