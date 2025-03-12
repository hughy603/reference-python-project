# Quick Start Guide: Python & Terraform Project Template

This guide will help you quickly initialize a new project using the Python & Terraform Project
Template.

## Prerequisites

- Python 3.8 or higher
- Git

## 1. Basic Project Initialization

The simplest way to create a new project is to run the interactive wizard:

```bash
# Clone the template repository
git clone https://github.com/yourusername/python-terraform-template.git my-new-project
cd my-new-project

# Run the initialization wizard
python scripts/init_project.py
```

Follow the interactive prompts to configure your project.

## 2. Using Presets

For common project types, you can use a preset:

```bash
# Data engineering project
python scripts/init_project.py --preset data_engineering

# Web API project
python scripts/init_project.py --preset web_api

# Machine learning project
python scripts/init_project.py --preset machine_learning

# Minimal Python project (no infrastructure)
python scripts/init_project.py --preset minimal
```

## 3. Using Configuration Files

For repeatable setups, create a YAML configuration file:

```yaml
# my_config.yml
project_name: "my-data-project"
package_name: "my_data_project"
description: "A data processing project"
author: "Your Name"
email: "your.email@example.com"
version: "0.1.0"

components:
  aws: true
  terraform: true
  docker: true
  documentation: true
  testing: true
  ci_cd: true
  data_pipelines: true
  api: false
  ml: false
```

Then initialize with:

```bash
python scripts/init_project.py --config my_config.yml
```

## 4. Quick Mode

For a faster setup with minimal prompting:

```bash
python scripts/init_project.py --quick
```

You'll only be prompted for essential information, with sensible defaults for the rest.

## 5. Non-Interactive Mode

For fully automated setup:

```bash
python scripts/init_project.py --non-interactive --config my_config.yml
```

## 6. After Initialization

Once initialization is complete:

1. Activate the virtual environment:

   ```bash
   # On Linux/Mac
   source .venv/bin/activate

   # On Windows
   .venv\Scripts\activate
   ```

1. Check the generated structure:

   ```bash
   ls -la
   ```

1. Read the generated README.md for project-specific instructions

1. Start developing!

## Common Options

| Option          | Description                                            |
| --------------- | ------------------------------------------------------ |
| `--preset NAME` | Use a predefined configuration preset                  |
| `--config FILE` | Load configuration from YAML or JSON file              |
| `--quick`       | Use defaults for most options with minimal interaction |
| `--keep-git`    | Keep existing Git history (default: start fresh)       |
| `--skip-env`    | Skip virtual environment creation                      |
| `--verbose`     | Show detailed output during initialization             |

## Next Steps

- Check out the full documentation in the `docs/` directory
- Explore the `PROJECT_INIT_DOCUMENTATION.md` file for detailed information
- Run `python scripts/init_project.py --help` to see all available options
