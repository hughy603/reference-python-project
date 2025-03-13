# Setting Up the Reference Python Project

## Overview

This guide provides comprehensive instructions for setting up and using the Reference Python Project
template. Whether you're starting a new project or contributing to an existing one, this document
covers everything you need to get up and running quickly.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**: Required for all project functionality

  - Verify with: `python --version` or `python3 --version`
  - Download from: [python.org](https://www.python.org/downloads/)

- **Git**: Required for version control

  - Verify with: `git --version`
  - Download from: [git-scm.com](https://git-scm.com/downloads)

### Optional Tools

Depending on your project needs:

- **Terraform** (for infrastructure components):

  - Verify with: `terraform --version`
  - Installation: [terraform.io/downloads](https://www.terraform.io/downloads)

- **Docker** (for containerization):

  - Verify with: `docker --version`
  - Installation: [docs.docker.com/get-docker](https://docs.docker.com/get-docker/)

## Quick Start

For those who want to get started immediately:

```bash
# Clone the repository
git clone https://github.com/yourusername/reference-python-project.git my-project
cd my-project

# Run the setup script
python setup.py

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Run the CLI
python -m enterprise_data_engineering info
```

## Detailed Setup Process

### 1. Clone or Download the Template

Either clone the repository:

```bash
git clone https://github.com/yourusername/reference-python-project.git my-project
cd my-project
```

Or download and extract the ZIP file from the GitHub repository.

### 2. Run the Setup Script

The project includes a unified setup script that works across platforms:

```bash
python setup.py
```

This script will:

- Verify your Python version
- Create a virtual environment
- Install all project dependencies (defined in pyproject.toml)
- Set up pre-commit hooks for development

### 3. Activate the Virtual Environment

Before working with the project, activate the virtual environment:

```bash
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

You'll see the virtual environment name in your prompt when it's activated.

## Project Configuration

All project configuration is consolidated in `pyproject.toml`, including:

- Package metadata and dependencies
- Build system configuration
- Development dependencies
- Tool configurations (pytest, ruff, mypy, etc.)

This centralized approach simplifies maintenance and provides a single source of truth for project
configuration.

## Project Initialization

If you're creating a new project based on this template, you can use the initialization system:

### Using the Interactive Wizard

The interactive wizard provides a user-friendly interface for creating a new project:

```bash
# On Linux/macOS:
./scripts/wizard.sh

# On Windows:
.\scripts\wizard.ps1

# Or directly with Python:
python scripts/run_interactive_wizard.py
```

### Using Configuration Files

For automated setup, you can provide a configuration file:

```bash
python scripts/init_project.py --config my_config.yml
```

Example configuration file (`my_config.yml`):

```yaml
project_name: my-awesome-project
package_name: my_awesome_project
description: A description of my awesome project
author: Your Name
email: your.email@example.com
version: 0.1.0
components:
  aws: true
  terraform: true
  documentation: true
```

## Common Development Tasks

Once set up, you can use these commands for common tasks:

```bash
# Run tests
pytest

# Run linting checks
ruff check .

# Format code
ruff format .

# Build and serve documentation
hatch run docs:serve
```

## Troubleshooting

### Common Issues

1. **Python version issues**

   - Ensure you're using Python 3.11+: `python --version`
   - Try using `python3` instead of `python` if needed

1. **Permission errors**

   - On Linux/macOS: `chmod +x scripts/*.py` to make scripts executable

1. **ModuleNotFoundError**

   - Ensure your virtual environment is activated
   - Check that all dependencies are installed: `pip install -e "."`

1. **Pre-commit hook issues**

   - Reinstall hooks: `pre-commit install`
   - Update hooks: `pre-commit autoupdate`

### Platform-Specific Considerations

#### Windows

- Use PowerShell or Command Prompt for commands
- Path separators are backslashes (`\`)
- Activate virtual environment with `.venv\Scripts\activate`

#### macOS/Linux

- Use Terminal for commands
- Path separators are forward slashes (`/`)
- Activate virtual environment with `source .venv/bin/activate`

#### WSL (Windows Subsystem for Linux)

If using WSL on Windows:

- Follow the Linux instructions
- Consider using VS Code's Remote WSL extension for seamless integration

## Additional Resources

- [Project Documentation](./docs/index.md): Full documentation
- [Contributing Guidelines](./CONTRIBUTING.md): How to contribute to the project
- [Architecture Overview](./docs/architecture.md): System architecture and design
