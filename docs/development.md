# Development Environment

This document provides a comprehensive guide to setting up and using the development environment for
this project.

## Configuration

This project uses a consolidated configuration approach with all settings centralized in
`pyproject.toml`. This includes:

- Package metadata and dependencies
- Build system configuration
- Development dependencies
- Tool configurations (pytest, ruff, mypy, etc.)

This centralized approach simplifies maintenance and provides a single source of truth for project
configuration.

## VS Code Integration

This project comes with extensive Visual Studio Code integration to enhance developer productivity.
This guide explains how to make the most of these features.

### Getting Started with VS Code

1. Open the project folder in VS Code
1. When prompted, install the recommended extensions
1. The workspace settings will be automatically applied

### Available Tasks

VS Code tasks automate common development operations. To run a task:

1. Press `Ctrl+Shift+P` to open the Command Palette
1. Type "Tasks: Run Task" and press Enter
1. Select the task you want to run

#### Core Development Tasks

| Task                       | Description                                                               | Keyboard Shortcut |
| -------------------------- | ------------------------------------------------------------------------- | ----------------- |
| 🔧 Setup Dev Environment   | Set up the development environment with dependencies and pre-commit hooks | -                 |
| 🧪 Run Tests               | Run all project tests with pytest                                         | `Ctrl+Shift+T`    |
| 📊 Run Tests with Coverage | Run tests with coverage report and generate HTML report                   | -                 |
| 🧪 Run Current Test File   | Run the currently active test file                                        | `Ctrl+Shift+R`    |
| 🧹 Format Code             | Run ruff formatter on project files                                       | `Ctrl+Shift+F`    |
| 🔍 Check Linting           | Run linting checks with ruff                                              | `Ctrl+Shift+L`    |
| 🛠️ Fix Linting             | Auto-fix linting issues with ruff                                         | -                 |
| ✅ Run Pre-commit          | Run all pre-commit hooks                                                  | `Ctrl+Shift+P`    |
| 📋 Project Health Check    | Run tests, linting, and build checks                                      | `Ctrl+Shift+H`    |

#### Documentation Tasks

| Task                   | Description                           | Keyboard Shortcut |
| ---------------------- | ------------------------------------- | ----------------- |
| 📖 Serve Documentation | Build and serve project documentation | `Ctrl+Shift+D`    |
| 📖 Build Documentation | Build project documentation           | -                 |

#### Build and Maintenance Tasks

| Task                   | Description                            | Keyboard Shortcut |
| ---------------------- | -------------------------------------- | ----------------- |
| 🏗️ Build Package       | Build Python package                   | -                 |
| ♻️ Clean Project       | Remove build artifacts and cache files | `Ctrl+Shift+C`    |
| 🔄 Update Dependencies | Update project dependencies            | -                 |

#### Docker Tasks

| Task                        | Description                                    | Keyboard Shortcut |
| --------------------------- | ---------------------------------------------- | ----------------- |
| 🐳 Start Docker Environment | Start containers defined in docker-compose.yml | -                 |
| 🐳 Stop Docker Environment  | Stop Docker containers                         | -                 |

### Problem Matchers

Problem matchers help VS Code parse the output of command-line tools to display errors and warnings
in the Problems panel. Our tasks are configured with appropriate problem matchers to help you
quickly identify and fix issues in your code.

When you run linting or test tasks, any issues found will be displayed in the Problems panel
(`Ctrl+Shift+M`). You can click on each issue to navigate directly to the relevant code location.

### Recommended Extensions

The project recommends several VS Code extensions to enhance your development experience:

#### Python Development

- **[Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)**: Modern Python
  linter and formatter
- **[Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)**: Python
  language support
- **[Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)**:
  Language server with rich type information

#### Infrastructure & Docker

- **[Terraform](https://marketplace.visualstudio.com/items?itemName=hashicorp.terraform)**:
  Terraform language support and validation
- **[Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)**:
  Docker container management
- **[CloudFormation Linter](https://marketplace.visualstudio.com/items?itemName=kddejong.vscode-cfn-lint)**:
  AWS CloudFormation validation

#### Documentation & Markdown

- **[Markdown All in One](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one)**:
  Markdown editing tools
- **[markdownlint](https://marketplace.visualstudio.com/items?itemName=davidanson.vscode-markdownlint)**:
  Markdown linting and style checking

#### Code Quality & Collaboration

- **[GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)**: Git
  integration and history visualization
- **[Auto Docstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring)**:
  Generate Python docstrings automatically
- **[Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker)**:
  Catch spelling errors in code and comments

### Customizing Keyboard Shortcuts

You can customize the keyboard shortcuts for tasks in your user keybindings:

1. Press `Ctrl+K Ctrl+S` to open the Keyboard Shortcuts editor
1. Search for "Tasks: Run Task"
1. Click the + icon to add a new keyboard shortcut
1. Enter your preferred shortcut and task name

### Workspace Settings

The project includes preconfigured workspace settings that:

- Set up the Python environment correctly
- Configure linting and formatting tools
- Set appropriate file associations
- Configure testing

You can view or modify these settings in the `.vscode/settings.json` file.

### Troubleshooting

#### Issues with Task Execution

If tasks fail to execute:

1. Make sure you have the correct dependencies installed
1. Check your Python virtual environment is activated
1. Verify that required tools are in your PATH

#### Extension Recommendations Not Showing

If you don't see extension recommendations:

1. Go to Extensions view (`Ctrl+Shift+X`)
1. Type "@recommended" in the search box

#### Problems with Python Integration

If Python features don't work correctly:

1. Check if the Python extension is installed and enabled
1. Verify that VS Code has selected the correct Python interpreter
1. You can set the Python interpreter manually by pressing `Ctrl+Shift+P` and typing "Python: Select
   Interpreter"

## Setting Up the Development Environment

To set up the development environment:

1. Clone the repository
1. Run `python setup.py` to create a virtual environment and install dependencies
1. Activate the virtual environment
1. Run VS Code tasks for further project setup

For more detailed instructions, see the [SETUP.md](../SETUP.md) file.
