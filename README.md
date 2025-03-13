# Reference Python Project

A robust template for enterprise-ready Python projects with best practices built-in.

## Overview

This project template provides a standardized structure and toolset for creating professional-grade
Python applications, with particular focus on data engineering workflows. It incorporates industry
best practices for development, testing, and deployment.

## Key Features

- ✅ **Modern Python Structure**: Optimized package layout using latest Python features
- ✅ **Consolidated Configuration**: Single source of truth in pyproject.toml
- ✅ **Developer Experience**: Comprehensive VS Code integration and pre-commit hooks
- ✅ **Testing Framework**: Ready-to-use pytest configuration with coverage reports
- ✅ **Quality Controls**: Static analysis with ruff, mypy, and bandit
- ✅ **Documentation**: MkDocs with Material theme for beautiful documentation
- ✅ **CI/CD Integration**: GitHub Actions workflows for testing and deployment
- ✅ **Infrastructure**: Templates for AWS resources and Terraform configurations
- ✅ **Enterprise Ready**: Security scanning, dependency management, and compliance

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- [Hatch](https://hatch.pypa.io/latest/) - Python package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/reference-python-project.git
cd reference-python-project

# Install hatch if not already installed
pip install hatch

# Create hatch environment and install dependencies
hatch env create

# Activate the hatch environment (interactive shell)
hatch shell

# Alternatively, you can run commands directly using hatch
hatch run lint:style  # Run linting checks
hatch run test:run    # Run tests
```

For more detailed setup instructions, including platform-specific guidance, see the
[Setup Guide](./SETUP.md).

### Running the CLI

The project includes a CLI for common tasks:

```bash
# Using hatch to run the CLI
hatch run python -m enterprise_data_engineering info

# Or, if in a hatch shell:
python -m enterprise_data_engineering info
```

### Development Tasks

```bash
# Format code
hatch run lint:fmt

# Run type checking
hatch run lint:type

# Run tests with coverage
hatch run test:cov

# Build and serve documentation
hatch run docs:serve
```

## Project Structure

```
reference-python-project/
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
└── CONSOLIDATION_PLAN.md # Project consolidation documentation
```

## Documentation

- [Setup Guide](./SETUP.md) - Installation and configuration
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to this project
- [Project Architecture](./docs/architecture.md) - System design and patterns
- [Development Guide](./docs/development.md) - Development environment and workflows
- [Testing Guide](./docs/testing.md) - Testing strategies and guidelines
- [Consolidation Plan](./CONSOLIDATION_PLAN.md) - Project consolidation and simplification

## License

This project is licensed under the MIT License - see the LICENSE file for details.
