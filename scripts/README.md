# Project Initialization Scripts

This directory contains scripts for setting up and initializing projects from the template.

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
