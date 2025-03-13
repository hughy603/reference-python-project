# Project Scripts

This directory contains utility scripts for setting up, managing, and working with the project.

## Project Initialization

### Interactive Wizard

The interactive wizard provides a user-friendly interface for initializing new projects from the
template.

- `interactive_wizard.py` - Main implementation of the interactive wizard
- `run_interactive_wizard.py` - Runner script that handles dependencies and launches the wizard

Usage:

```bash
python scripts/run_interactive_wizard.py
```

![Wizard Screenshot](../docs/images/wizard_welcome.png)

For detailed information, see the [Wizard Documentation](../docs/wizard.md).

### Standard Initialization

The standard initialization script provides command-line options for different initialization
methods.

- `init_project.py` - Main project initialization script with various modes
- `template_processor.py` - Core logic for processing template components
- `template_utils.py` - Utility functions for the template system

Usage:

```bash
# Interactive mode
python scripts/init_project.py

# Quick start mode
python scripts/init_project.py --quick

# Configuration file mode
python scripts/init_project.py --config my_config.yml

# Preset mode
python scripts/init_project.py --preset data_engineering
```

## Development Setup

These scripts help set up the development environment for different platforms:

- `setup.sh` - Basic setup script for Unix-based systems
- `wsl_setup.sh` - Setup script for Windows Subsystem for Linux
- `windows_setup.ps1` - Setup script for Windows
- `non_admin_setup.ps1` - Windows setup script that doesn't require admin privileges
- `setup_podman.ps1` - Script to set up Podman as an alternative to Docker on Windows
- `unified_setup.py` - Cross-platform setup script that works on any OS

## Documentation

Scripts for managing project documentation:

- `docs.sh` - Script to build and serve documentation
- `generate_docs.sh` - Script to generate documentation from source code
- `generate_api_docs.py` - Script to generate API documentation
- `fix_documentation.py` - Script to fix common documentation issues
- `find_obsolete_docs.py` - Script to identify outdated or obsolete documentation
- `cleanup_docs.py` - Script to clean up documentation

## Testing and Quality

Scripts for testing and maintaining code quality:

- `run_tox_tests.sh` - Script to run Tox tests on Unix-based systems
- `run_tox_tests.ps1` - Script to run Tox tests on Windows
- `run_optimized.ps1` - Script to run optimized Python code on Windows
- `run_precommit.py` - Script to run pre-commit hooks manually
- `setup_precommit.py` - Script to set up pre-commit hooks
- `fix_precommit.py` - Script to fix common pre-commit hook issues
- `project_health_dashboard.py` - Script to generate a dashboard of project health metrics

## AWS and Terraform

Scripts for working with AWS services and Terraform:

- `run_glue_job_local.py` - Script to run AWS Glue jobs locally
- `test_lambda_local.py` - Script to test AWS Lambda functions locally
- `generate_terraform_docs.py` - Script to generate documentation for Terraform modules

## Maintenance and Utilities

Scripts for general project maintenance and utility tasks:

- `cleanup_repository.py` - Script to clean up the repository
- `delete_obsolete_files.py` - Script to identify and delete obsolete files
- `diagnostics.py` - Script to run diagnostics on the project
- `modernize_project.py` - Script to update the project to use modern practices
- `optimize_py312.py` - Script to optimize code for Python 3.12
- `setup_nexus.py` - Script to configure Nexus repository access
- `tasks.py` - Invoke tasks for common operations
- `update_vscode_settings.py` - Script to update VS Code settings

## Windows Integration

Scripts for improved Windows integration:

- `open_in_vscode.bat` - Batch file to open the project in VS Code on Windows

## Developer Onboarding

Scripts to help new developers get started:

- `onboard_developer.sh` - Script to set up the project for a new developer

## Key Scripts

### Project Initialization

- **`init_project.py`**: Main script for initializing a new project from the template
- **`template_processor.py`**: Processes the template manifest and handles component configuration
- **`template_utils.py`**: Utility functions for template processing

### Environment Setup

- **`unified_setup.py`**: Sets up the development environment across platforms
- **`tasks.py`**: Python-based task runner for common development tasks

## Using the Project Initialization Wizard

### Basic Usage

```bash
# Run the interactive wizard
python scripts/init_project.py

# Use a predefined preset
python scripts/init_project.py --preset data_engineering

# Use a configuration file
python scripts/init_project.py --config sample_config.yml

# Quick setup with minimal prompts
python scripts/init_project.py --quick
```

### Available Presets

- **`data_engineering`**: Data engineering project with AWS infrastructure
- **`web_api`**: Web API project with AWS infrastructure
- **`machine_learning`**: Machine learning project with AWS infrastructure and ML components
- **`minimal`**: Minimal Python project without infrastructure components

### Command Line Options

| Option              | Description                                               |
| ------------------- | --------------------------------------------------------- |
| `--non-interactive` | Run in non-interactive mode using defaults or config file |
| `--config FILE`     | Load configuration from YAML or JSON file                 |
| `--preset NAME`     | Use a predefined configuration preset                     |
| `--quick`           | Use defaults for most options with minimal interaction    |
| `--keep-git`        | Keep existing Git history (default: start fresh)          |
| `--skip-env`        | Skip virtual environment creation                         |
| `--verbose`         | Show detailed output during initialization                |
| `--manifest`        | Path to template manifest file                            |

## Template Manifest

The template manifest (`template_manifest.yml`) defines the components available in the template and
their relationships. You can use the template processor to inspect the manifest:

```bash
# Show template information
python scripts/template_processor.py --info

# List available components
python scripts/template_processor.py --list-components

# Show information about a specific component
python scripts/template_processor.py --component terraform

# Generate a component dependency graph
python scripts/template_processor.py --graph
```

## VS Code Integration

To configure VS Code settings for your project:

```bash
# Update VS Code settings based on your project configuration
python scripts/update_vscode_settings.py sample_config.yml
```

This will update:

- `settings.json`: Editor and language settings
- `tasks.json`: Common development tasks
- `launch.json`: Debug configurations
- `extensions.json`: Recommended extensions

## Creating a Custom Project Template

1. Initialize a new project using the wizard
1. Customize the project as needed
1. Create a new template manifest based on your customizations
1. Share your custom template with others

## Adding New Components

To add a new component to the template:

1. Create the component files in the appropriate directories
1. Add the component to the template manifest
1. Update the initialization scripts to handle the new component

## Troubleshooting

If you encounter issues during initialization:

1. Run with `--verbose` to see detailed output
1. Check for errors in the console
1. Verify that your configuration file is valid
1. Ensure all dependencies are installed

For more help, see the [Contributing Guide](../CONTRIBUTING.md).

## Available Scripts

| Script                        | Description                                  | Usage                                               |
| ----------------------------- | -------------------------------------------- | --------------------------------------------------- |
| `init_project.py`             | Main project initialization wizard           | `python scripts/init_project.py [options]`          |
| `template_processor.py`       | Template manifest processor                  | `python scripts/template_processor.py [options]`    |
| `template_utils.py`           | Utilities for template processing            | Import in other scripts                             |
| `update_vscode_settings.py`   | Update VS Code settings for project          | `python scripts/update_vscode_settings.py [config]` |
| `unified_setup.py`            | Cross-platform development environment setup | `python scripts/unified_setup.py`                   |
| `tasks.py`                    | Project task runner                          | `python scripts/tasks.py [task]`                    |
| `project_health_dashboard.py` | Project health metrics dashboard             | `python scripts/project_health_dashboard.py`        |

## Project Configuration

### Configuration Format

Configuration files can be in YAML or JSON format with the following structure:

```yaml
# Project Information
project_name: "my-project"
package_name: "my_package"
description: "Project description"
author: "Author Name"
email: "author@example.com"
organization: "Organization Name"
version: "0.1.0"

# Components to include
components:
  aws: true
  terraform: true
  cloudformation: false
  docker: true
  documentation: true
  testing: true
  ci_cd: true
  data_pipelines: false
  api: false
  ml: false

# Advanced configuration (optional)
advanced:
  python_version: "3.12"
  linting:
    strict: false
  testing:
    coverage_threshold: 80
```

### Sample Configurations

Several sample configuration files are provided:

- `sample_config.yml`: General-purpose configuration
- Sample presets can be viewed using the `--preset` option

## How the Template System Works

### Component-Based Architecture

The template uses a component-based architecture where:

1. **Components** are defined in the template manifest
1. Each component has associated **files** and **dependencies**
1. Components can be **enabled** or **disabled** based on project needs
1. **Dependencies** ensure required components are included

### Template Processing Flow

1. **Configuration** is collected from user input or config files
1. **Component resolution** determines which components to include
1. **Variable substitution** replaces placeholders in template files
1. **Cleanup** removes unused components and template artifacts
1. **Environment setup** creates a virtual environment and installs dependencies
1. **Git initialization** sets up a fresh repository

### Template Variables

Template variables are placeholders in files that get replaced during initialization:

- Jinja-style: `{{ VARIABLE_NAME }}`
- Placeholder style: `___VARIABLE_NAME___`

Variables are defined in the manifest and populated from the configuration.

## Best Practices

1. **Start with a preset** and customize as needed
1. **Use configuration files** for repeatable setups
1. **Create custom presets** for common project types
1. **Keep the template updated** with the latest best practices
1. **Document custom components** thoroughly

## Contributing

Contributions to improve the template are welcome! See the [Contributing Guide](../CONTRIBUTING.md)
for details.

## License

This template is licensed under the MIT License. See the LICENSE file for details.
