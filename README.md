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

See the [Setup Guide](./SETUP.md) for comprehensive instructions on installing and using this
template.

Quick start:

```bash
# Clone the repository
git clone https://github.com/yourusername/reference-python-project.git my-project
cd my-project

# Run the setup script
python setup.py
```

## Project Structure

```
reference-python-project/
├── docs/                 # Documentation files
├── infrastructure/       # Infrastructure as code (Terraform, CloudFormation)
├── scripts/              # Utility scripts for project management
├── src/                  # Source code
│   ├── enterprise_data_engineering/  # Main package
│   └── reference_python_project/     # Reference implementation
├── tests/                # Test suite
│   ├── test_enterprise_data_engineering/  # Tests for main package
│   ├── test_aws/                      # AWS-specific tests
│   ├── test_wizards/                  # Tests for initialization wizards
│   ├── common_utils/                  # Shared test utilities
│   └── shared/                        # Shared fixtures and helpers
├── .github/              # GitHub configuration and workflows
├── pyproject.toml        # Project configuration and dependencies
├── Dockerfile            # Container definition
└── setup.py              # Unified setup script
```

## Documentation

- [Setup Guide](./SETUP.md) - Installation and configuration
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to this project
- [Project Architecture](./docs/architecture.md) - System design and patterns
- [Development Guide](./docs/development.md) - Development environment and workflows
- [Consolidation Plan](./CONSOLIDATION_PLAN.md) - Project consolidation and simplification

## License

This project is licensed under the MIT License - see the LICENSE file for details.
