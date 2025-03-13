# Interactive Project Initialization Wizard

![Wizard Banner](images/wizard_banner.png)

The Interactive Project Initialization Wizard provides a user-friendly interface for setting up new
projects based on our enterprise-ready template. It guides you through the entire setup process with
a modern, interactive terminal UI.

## Features

- 🎨 **Beautiful UI**: Colorful, formatted terminal interface with progress tracking
- 🧩 **Component Selection**: Easily choose which components to include in your project
- 🔄 **Dependency Resolution**: Automatic handling of component dependencies
- 📝 **Live Documentation**: Context-sensitive help and documentation
- 👁️ **Live Preview**: See your choices reflected in real-time
- 🛠️ **Graceful Fallback**: Works even without the Rich library, using basic terminal output

## Installation

The wizard is included with the template, so no separate installation is needed. However, for the
best experience, we recommend installing the `rich` library:

```bash
pip install rich
```

The wizard will attempt to install `rich` automatically if it's not present, but you can prevent
this with the `--no-install` option.

## Usage

### Basic Usage

Run the wizard from the root of the cloned template repository:

```bash
python scripts/run_interactive_wizard.py
```

This will launch the interactive wizard and guide you through the initialization process.

### Options

The following command-line options are available:

- `--no-install`: Prevents the wizard from automatically installing missing dependencies

## Walkthrough

### 1. Launch the Wizard

Start by running the wizard script:

```bash
python scripts/run_interactive_wizard.py
```

You'll be greeted with a welcome screen that provides an overview of the template and the
initialization process.

![Welcome Screen](images/wizard_welcome.png)

### 2. Project Metadata

The first section allows you to specify basic project information:

- **Project name**: The name of your project (kebab-case)
- **Package name**: The Python package name (snake_case)
- **Description**: A short description of your project
- **Author**: Your name
- **Email**: Your email address
- **Organization**: Your organization name (optional)
- **Version**: Initial version number (semver)

![Project Metadata](images/wizard_metadata.png)

### 3. Component Selection

Next, you'll select which components to include in your project. The wizard presents a table of
available components with descriptions and dependencies.

As you select components, their dependencies are automatically included, and the table updates in
real-time to reflect your choices.

![Component Selection](images/wizard_components.png)

### 4. Configuration Summary

After making your selections, you'll see a summary of your configuration. Review this to ensure
everything is as expected before proceeding.

![Configuration Summary](images/wizard_summary.png)

### 5. Project Initialization

Once you confirm, the wizard will initialize your project with the selected configuration. A
progress indicator shows the status of the initialization process.

![Initialization Progress](images/wizard_progress.png)

### 6. Completion

When the initialization is complete, the wizard will display a success message with next steps.

![Completion](images/wizard_complete.png)

## Component Reference

The following components are available for inclusion in your project:

| Component      | Description                      | Dependencies   |
| -------------- | -------------------------------- | -------------- |
| core           | Core Python project structure    | *Required*     |
| aws            | AWS integration utilities        | None           |
| terraform      | Terraform infrastructure as code | None           |
| cloudformation | CloudFormation templates         | aws            |
| docker         | Docker containerization          | None           |
| documentation  | MkDocs documentation             | None           |
| testing        | Pytest testing framework         | None           |
| ci_cd          | GitHub Actions CI/CD             | None           |
| data_pipelines | Data pipeline components         | None           |
| api            | API development components       | None           |
| ml             | Machine learning components      | data_pipelines |

## Testing the Wizard

The wizard comes with a comprehensive test suite to ensure its functionality and reliability.

### Running Tests

To run the test suite:

```bash
python tests/run_wizard_tests.py
```

You can also run specific test categories:

```bash
# Run only unit tests
python tests/run_wizard_tests.py --unit

# Run only integration tests
python tests/run_wizard_tests.py --integration

# Run with verbose output
python tests/run_wizard_tests.py -v
```

### Test Structure

The tests are organized into:

- **Unit Tests**: Testing individual components and functions
- **Integration Tests**: Testing the interaction between components, including shell scripts

For more information about testing, see the [Testing Documentation](testing.md).

## Troubleshooting

### Rich Library Not Available

If the `rich` library is not installed, the wizard will fall back to basic terminal output. While
not as visually appealing, all functionality is still available.

To install the `rich` library:

```bash
pip install rich
```

### PyYAML Not Available

The PyYAML library is required for the wizard to function. If it's not installed, the wizard will
attempt to install it automatically. If the installation fails, you'll need to install it manually:

```bash
pip install pyyaml
```

### Wizard Fails to Launch

If the wizard fails to launch, ensure you're running it from the root directory of the template
repository:

```bash
cd reference-python-project
python scripts/run_interactive_wizard.py
```

### Initialization Errors

If you encounter errors during initialization, check the error message for specific issues. Common
problems include:

- **Permission denied**: Ensure you have write permissions to the directory
- **Missing dependencies**: Ensure all required dependencies are installed
- **Git conflicts**: If initializing in an existing Git repository, ensure there are no conflicts

## Advanced Usage

### Combining with Existing Scripts

The interactive wizard can be used alongside the existing initialization scripts:

```bash
# Run interactive wizard first to create configuration
python scripts/run_interactive_wizard.py

# Then use the configuration with other scripts
python scripts/init_project.py --config my_config.yml
```

### Programmatic Usage

You can also use the wizard components programmatically in your own scripts:

```python
from scripts.interactive_wizard import (
    prompt_for_metadata,
    prompt_for_components,
    load_manifest,
)

# Load the template manifest
manifest = load_manifest()

# Prompt for project metadata
metadata = prompt_for_metadata()

# Prompt for component selection
components = prompt_for_components(manifest)

# Use the configuration as needed
config = {**metadata, "components": components}
```

## Contributing

If you have ideas for improving the wizard or find any issues, please contribute by:

1. Opening an issue describing the problem or enhancement
1. Submitting a pull request with your improvements

Be sure to include tests for any new functionality or bug fixes.

## Future Enhancements

Planned enhancements for future versions:

- **Template Preview**: Live preview of the project structure based on your selections
- **Config Export/Import**: Save and load wizard configurations
- **Custom Templates**: Support for custom template repositories
- **Web Interface**: Optional web-based UI for the initialization process
- **Multiple Project Types**: Support for different types of project templates
