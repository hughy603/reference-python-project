# Project Initialization System

![Project Initialization Banner](docs/images/project_init_banner.svg)

A robust system for creating enterprise-ready Python and Terraform projects with best practices
built-in.

## Features

- **Template-based project creation**: Generate new projects from customizable templates
- **Configuration-driven**: Use YAML or JSON configuration files to define project settings
- **Variable substitution**: Replace template variables with your project-specific values
- **Package renaming**: Automatically rename packages and update imports
- **Git initialization**: Set up Git repositories with initial commits
- **Virtual environment setup**: Create and configure Python virtual environments
- **Cross-platform support**: Works on Windows, macOS, and Linux

## Installation

Clone this repository and install the required dependencies:

```bash
git clone https://github.com/yourusername/project-initialization-system.git
cd project-initialization-system
pip install -r requirements.txt
```

## Usage

### Basic Usage

To initialize a new project with interactive prompts:

```bash
python scripts/init_project.py
```

### Using Configuration Files

You can provide a configuration file in YAML or JSON format:

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
```

### Command-line Options

```
usage: init_project.py [-h] [--config CONFIG] [--verbose] [--skip-env] [--keep-git] [--manifest MANIFEST]

Initialize a new project from the template.

options:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Path to a configuration file (YAML or JSON)
  --verbose, -v         Enable verbose output
  --skip-env, -s        Skip virtual environment setup
  --keep-git, -k        Keep existing Git repository
  --manifest MANIFEST, -m MANIFEST
                        Path to template manifest file
```

## Creating Custom Templates

You can create your own project templates by:

1. Creating a directory structure with your template files
1. Adding template variables using `{{variable_name}}` syntax
1. Creating a `template_manifest.yml` file to define the template structure

Example manifest file:

```yaml
name: Python Web Application
description: A template for Python web applications
variables:
  - name: project_name
    description: Name of the project
    default: my-web-app
  - name: package_name
    description: Name of the Python package
    default: my_web_app
  - name: description
    description: Project description
    default: A Python web application
files:
  - source: templates/pyproject.toml
    destination: pyproject.toml
  - source: templates/README.md
    destination: README.md
  - source: templates/src
    destination: src/{{package_name}}
```

## Development

### Running Tests

```bash
pytest
```

### Contributing

1. Fork the repository
1. Create a feature branch: `git checkout -b feature/your-feature-name`
1. Commit your changes: `git commit -am 'Add some feature'`
1. Push to the branch: `git push origin feature/your-feature-name`
1. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
