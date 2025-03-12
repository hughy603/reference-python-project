# Project Initialization System Documentation

![Project Initialization System](docs/images/project_init_banner.png)

## 📋 Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Using the Initialization System](#using-the-initialization-system)
  - [Interactive Mode](#interactive-mode)
  - [Quick Start Mode](#quick-start-mode)
  - [Configuration File Mode](#configuration-file-mode)
  - [Preset Mode](#preset-mode)
- [Step-by-Step Guide](#step-by-step-guide)
- [Component Reference](#component-reference)
- [Templates and Variables](#templates-and-variables)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)

## Overview

The Project Initialization System is a powerful tool for creating new Python and Terraform projects
based on our enterprise-ready template. It provides:

- **🧩 Modular Components**: Choose which features to include in your project
- **🎯 Customization**: Configure project metadata and dependencies
- **🔄 Dependency Management**: Automatic resolution of component dependencies
- **🔧 Environment Setup**: Automated creation of development environment
- **📚 Best Practices**: Enforcement of coding standards and project structure

## Getting Started

### Prerequisites

Before using the Project Initialization System, ensure you have:

- Python 3.11 or higher
- Git
- pip (Python package manager)

### Installation

The initialization system is included in the template repository, so no separate installation is
required. Simply clone the repository:

```bash
git clone https://github.com/your-org/reference-python-project.git
cd reference-python-project
```

## Using the Initialization System

There are multiple ways to use the initialization system, depending on your needs and preferences.

### Interactive Mode

The interactive mode guides you through the initialization process with step-by-step prompts.

```bash
python scripts/init_project.py
```

### Quick Start Mode

Quick start mode uses sensible defaults with minimal prompting:

```bash
python scripts/init_project.py --quick
```

### Configuration File Mode

You can specify all options in a YAML configuration file:

```bash
python scripts/init_project.py --config my_config.yml
```

See [sample_config.yml](sample_config.yml) for an example configuration file.

### Preset Mode

Use predefined configurations for common project types:

```bash
python scripts/init_project.py --preset data_engineering
```

Available presets:

- `data_engineering`: AWS-based data engineering project
- `web_api`: Web API with documentation and testing
- `machine_learning`: ML project with pipeline components
- `minimal`: Minimal project with core components only

## Step-by-Step Guide

Follow this step-by-step guide to initialize a new project:

### Step 1: Clone the Template Repository 🔄

```bash
git clone https://github.com/your-org/reference-python-project.git my-new-project
cd my-new-project
```

### Step 2: Run the Initialization Script 🚀

```bash
python scripts/init_project.py
```

### Step 3: Enter Project Information 📝

You'll be prompted for project metadata:

```
Project name [my-project]: my-awesome-project
Package name [my_awesome_project]:
Description: A description of my awesome project
Author: Your Name
Email: your.email@example.com
Organization: Your Organization
```

### Step 4: Select Components ✅

Choose which components to include in your project:

```
Select components to include:
[x] aws            - AWS integration
[x] terraform      - Terraform infrastructure as code
[ ] cloudformation - CloudFormation templates
[x] docker         - Docker containerization
[x] documentation  - MkDocs documentation
[x] testing        - Pytest testing framework
[x] ci_cd          - GitHub Actions CI/CD
[ ] data_pipelines - Data pipeline components
[ ] api            - API development components
[ ] ml             - Machine learning components
```

### Step 5: Confirm and Initialize ✨

Review your selections and confirm:

```
Initializing project with the following configuration:
- Project name: my-awesome-project
- Package name: my_awesome_project
- Components: aws, terraform, docker, documentation, testing, ci_cd

Proceed? [Y/n]: Y
```

### Step 6: Project Setup 🔧

The system will now:

1. Process template components
1. Substitute template variables
1. Rename the package
1. Initialize Git repository
1. Set up virtual environment

When complete, you'll see:

```
Project successfully initialized!

Next steps:
1. Activate the virtual environment:
   source .venv/bin/activate
2. Install development dependencies:
   pip install -e ".[dev]"
3. Run the tests:
   pytest
```

## Component Reference

The template includes the following components:

| Component      | Description                      | Dependencies   |
| -------------- | -------------------------------- | -------------- |
| core           | Core Python project structure    | Required       |
| aws            | AWS utilities and integration    | None           |
| terraform      | Terraform infrastructure as code | None           |
| cloudformation | CloudFormation templates         | aws            |
| docker         | Docker containerization          | None           |
| documentation  | MkDocs documentation             | None           |
| testing        | Pytest testing framework         | None           |
| ci_cd          | GitHub Actions CI/CD             | None           |
| data_pipelines | Data pipeline components         | aws            |
| api            | API development components       | None           |
| ml             | Machine learning components      | data_pipelines |

## Templates and Variables

The initialization system uses template variables to customize files. Variables can be referenced in
two ways:

1. Jinja-style: `{{ VARIABLE_NAME }}`
1. Placeholder style: `___VARIABLE_NAME___`

Available variables:

| Variable     | Description         | Example                      |
| ------------ | ------------------- | ---------------------------- |
| PROJECT_NAME | Name of the project | my-awesome-project           |
| PACKAGE_NAME | Python package name | my_awesome_project           |
| DESCRIPTION  | Project description | A description of the project |
| VERSION      | Project version     | 0.1.0                        |
| AUTHOR       | Author name         | Your Name                    |
| AUTHOR_EMAIL | Author email        | <your.email@example.com>     |
| ORGANIZATION | Organization name   | Your Organization            |

## Troubleshooting

### Common Issues

#### Initialization fails with "Manifest file not found"

**Problem**: The system cannot find the template manifest file.

**Solution**: Make sure you're running the script from the root directory of the template
repository. If the file is missing, you can regenerate it with:

```bash
python scripts/template_utils.py --generate-manifest
```

#### Virtual environment creation fails

**Problem**: Virtual environment creation fails due to missing Python version or permissions.

**Solution**:

- Ensure Python 3.11 or higher is installed and in your PATH

- For permission issues on Unix systems, use `sudo` or fix permissions:

  ```bash
  sudo chown -R $(whoami) .
  ```

- Try creating the virtual environment manually:

  ```bash
  python -m venv .venv
  source .venv/bin/activate  # On Unix
  # OR
  .venv\Scripts\activate     # On Windows
  ```

#### Package renaming fails

**Problem**: The system fails to rename the package directories.

**Solution**: Check if any processes are using files in the directory. Close IDEs or file explorers,
then try again. If it still fails, rename the directories manually:

```bash
mv src/reference_python_project src/your_package_name
```

### Platform-Specific Issues

<details>
<summary><b>Windows Issues</b></summary>

#### Path Length Limitations

**Problem**: Windows has a 260-character path limit that may cause issues with deep directory
structures.

**Solution**: Enable long path support in Windows 10/11:

1. Run `regedit` as administrator
1. Navigate to `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
1. Set `LongPathsEnabled` to `1`
1. Restart your computer

#### Permission Denied on Script Execution

**Problem**: PowerShell security policies may prevent script execution.

**Solution**: Run PowerShell as administrator and set execution policy:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

</details>

<details>
<summary><b>Linux Issues</b></summary>

#### Locale Issues

**Problem**: Some systems may have locale configuration issues affecting Python.

**Solution**: Set UTF-8 encoding environment variables:

```bash
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

#### Missing System Dependencies

**Problem**: Some Python packages require system libraries to install.

**Solution**: Install required system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev build-essential libssl-dev libffi-dev

# RHEL/CentOS
sudo yum install python3-devel gcc openssl-devel libffi-devel
```

</details>

<details>
<summary><b>macOS Issues</b></summary>

#### OpenSSL Issues

**Problem**: macOS may have issues with OpenSSL when installing certain packages.

**Solution**: Install OpenSSL via Homebrew:

```bash
brew install openssl
export CFLAGS="-I$(brew --prefix openssl)/include"
export LDFLAGS="-L$(brew --prefix openssl)/lib"
```

#### Command Line Tools Missing

**Problem**: Xcode command line tools may not be installed.

**Solution**: Install command line tools:

```bash
xcode-select --install
```

</details>

## Advanced Usage

### Non-Interactive Mode

Run in non-interactive mode using a configuration file:

```bash
python scripts/init_project.py --non-interactive --config my_config.yml
```

### Skip Virtual Environment

Skip virtual environment creation:

```bash
python scripts/init_project.py --skip-env
```

### Keep Git History

Keep the template's Git history instead of starting fresh:

```bash
python scripts/init_project.py --keep-git
```

### Verbose Output

Enable verbose output for debugging:

```bash
python scripts/init_project.py --verbose
```

### Custom Manifest

Use a custom template manifest file:

```bash
python scripts/init_project.py --manifest custom_manifest.yml
```

## API Reference

The Project Initialization System consists of the following key modules:

### `init_project.py`

The main entry point for the initialization system.

```python
def initialize_project(config, skip_env=False, keep_git=False, verbose=False):
    """Initialize a project with the given configuration."""
    # ...
```

### `template_processor.py`

Handles template component processing and variable substitution.

```python
class TemplateProcessor:
    def __init__(self, manifest_path, verbose=False):
        """Initialize with the template manifest file."""
        # ...

    def process_template(self, config):
        """Process the template with the given configuration."""
        # ...
```

### `template_utils.py`

Utilities for working with templates.

```python
def generate_manifest(output_path):
    """Generate a manifest file from the template structure."""
    # ...
```

## Expected Output Examples

Below are examples of expected output for common operations.

### Successful Initialization

```
Project Initialization System v1.0.0

Step 1: Project Configuration
✅ Loaded configuration from config.yml

Step 2: Component Processing
✅ Enabled components: core, aws, terraform, docker, documentation, testing, ci_cd
✅ Resolved dependencies: No additional dependencies needed

Step 3: Template Processing
✅ Updated 12 files with template variables
✅ Removed 5 files from unused components
✅ Renamed package from reference_python_project to my_awesome_project

Step 4: Environment Setup
✅ Created new virtual environment in .venv
✅ Installed project in development mode
✅ Initialized Git repository

Initialization completed successfully!

Next steps:
1. Activate the virtual environment:
   source .venv/bin/activate
2. Install development dependencies:
   pip install -e ".[dev]"
3. Run the tests:
   pytest
```

### File Not Found Error

```
Project Initialization System v1.0.0

Step 1: Project Configuration
❌ Error: Configuration file not found: non_existent_config.yml

Please verify that the file exists and is readable.
```

### Invalid Configuration

```
Project Initialization System v1.0.0

Step 1: Project Configuration
❌ Error: Invalid configuration format in config.yml

The configuration file must be a valid YAML or JSON file.
Parse error: Expected a mapping node but found a scalar node at line 3, column 1
```
