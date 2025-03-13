# Contributing Guide

Thank you for your interest in contributing to our project! This document provides guidelines and
instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Branching Strategy](#branching-strategy)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)
- [Documentation Standards](#documentation-standards)

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We strive to
maintain a welcoming environment for all contributors regardless of background or experience level.

## Getting Started

1. **Fork the repository** to your GitHub account
1. **Clone your fork** to your local machine
1. **Set up your development environment** (see [Development Environment](#development-environment))
1. **Create a branch** for your work
1. **Make your changes**, following our [Code Style Guidelines](#code-style-guidelines)
1. **Write tests** for your changes, following our [Testing Guidelines](#testing-guidelines)
1. **Submit a pull request** (see [Pull Request Process](#pull-request-process))

## Pre-commit Hooks

**⚠️ IMPORTANT: You MUST run `pre-commit install` before making any commits to this repository.**

Our project relies on pre-commit hooks to ensure code quality, security, and consistency. These
hooks run automatic checks before each commit to prevent issues from being introduced into the
codebase.

### Why Pre-commit is Required

- **Prevents broken builds** by catching issues before they reach CI
- **Saves review time** by fixing common issues automatically
- **Ensures consistent code style** across all contributors
- **Catches security issues** early in the development process

### Setting Up Pre-commit

To set up pre-commit hooks:

```bash
# Install pre-commit if not already installed
pip install pre-commit

# Install the git hooks
pre-commit install
```

You can also run pre-commit manually on all files:

```bash
pre-commit run --all-files
```

**Note**: Pull requests that don't conform to the standards enforced by pre-commit will fail CI
checks and require fixes before they can be merged.

## Development Environment

### Prerequisites

- Python 3.10+
- Git
- VS Code or your preferred editor
- No administrator privileges required

### Setup

The setup process has been simplified. Just run:

```bash
# For all platforms (Windows, Linux, macOS)
python setup.py
```

This script will:

1. Check your Python version (3.10+ required)
1. Create a virtual environment
1. Install all dependencies
1. Set up pre-commit hooks
1. Provide guidance on next steps

For detailed setup options or troubleshooting, see:

- [Windows Setup Guide](WINDOWS_SETUP.md) for Windows-specific instructions
- README.md for general setup information

### VS Code Extensions

We recommend installing the following VS Code extensions:

- Ruff (charliermarsh.ruff)
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- HashiCorp Terraform (hashicorp.terraform)
- YAML (redhat.vscode-yaml)

## Branching Strategy

- `main` - Stable release branch
- `develop` - Development branch (merge your features here)
- `feature/[feature-name]` - Feature branches
- `bugfix/[bug-name]` - Bug fix branches
- `release/[version]` - Release preparation branches

## Code Style Guidelines

### Python

We use Ruff for code linting and formatting. Our code style follows these principles:

1. **Readability** - Code should be readable and self-documenting
1. **Consistency** - Follow established patterns
1. **Simplicity** - Prefer simple, focused functions and classes
1. **Type Annotations** - Use type hints for all public functions and methods

To check your code:

```powershell
ruff check .
ruff format --check .
```

To fix issues automatically:

```powershell
ruff check --fix .
ruff format .
```

### Terraform

For Terraform, we follow HashiCorp's style conventions:

1. 2-space indentation
1. Align `=` for variable declarations
1. Group related blocks together
1. Use lowercase resource names with underscores

To format Terraform code:

```powershell
terraform fmt -recursive
```

## Testing Guidelines

### Python Tests

- Write tests for all new features and bug fixes
- Aim for at least 90% code coverage
- Use pytest for all tests
- Group tests by feature area and type (unit, integration)

Test Structure:

- `tests/unit/` - Unit tests that don't require external dependencies
- `tests/integration/` - Tests that interact with external services

To run tests:

```powershell
# Run all tests
pytest

# Run specific tests
pytest tests/unit/
pytest tests/unit/test_specific_module.py

# Run with coverage
pytest --cov=src
```

### Terraform Tests

For Terraform:

- Use terraform-validate for syntax checking
- Use tflint for extended linting
- For complex modules, write example configurations

### Testing Structure

Tests are organized by type and module:

- `tests/test_enterprise_data_engineering/` - Tests for the core package functionality
- `tests/test_aws/` - Tests for AWS-related functionality
- `tests/test_wizards/` - Tests for project initialization and wizards
- `tests/common_utils/` - Tests for common utilities
- `tests/shared/` - Shared test fixtures and helpers

### Running Tests

To run all tests:

```bash
hatch run test:run
```

To run a specific test directory:

```bash
pytest tests/test_aws/
pytest tests/test_enterprise_data_engineering/test_specific_module.py
```

## Pull Request Process

1. **Create a pull request** from your branch to the `develop` branch
1. **Fill out the PR template** with details about your changes
1. **Ensure all tests pass** and code meets style guidelines
1. **Request a review** from at least one maintainer
1. **Address any feedback** from reviewers
1. Once approved, a maintainer will merge your PR

## Documentation

This project uses a documentation-first approach, emphasizing thorough and clear documentation. All
features should be documented before being considered complete.

### Documentation Tools

We use the following documentation tools:

1. **MkDocs**: For user guides, conceptual documentation, and general information (written in
   Markdown)

## Documentation Standards

### Docstrings

All public modules, functions, classes, and methods should have docstrings. We follow the
[Google docstring style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
for Python code:

```python
def example_function(param1, param2):
    """Summary of what the function does.

    More detailed description of the function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: If param1 is invalid

    Examples:
        >>> example_function(1, 2)
        3
    """
    return param1 + param2
```

### Documentation Types

We use MkDocs for user guides, tutorials, and general documentation (written in Markdown)

### Building Documentation

To build the documentation locally:

```bash
# MkDocs
hatch run docs:mkdocs-build    # Build
hatch run docs:mkdocs-serve    # Serve with auto-rebuild
```

### Documentation Linting

We use pre-commit hooks to ensure documentation quality:

- **doc8**: For reStructuredText (RST) linting
- **mdformat**: For Markdown linting
- **interrogate**: For checking docstring coverage

You can run these checks manually:

```bash
pre-commit run doc8 --all-files
pre-commit run mdformat --all-files
pre-commit run interrogate --all-files
```

When submitting a PR, ensure your code has appropriate docstring coverage (at least 80%).

## Thank You

Thank you for contributing to our project! Your efforts help make this template better for everyone.
