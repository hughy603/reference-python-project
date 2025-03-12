# Installation Guide: Python & Terraform Project Template

This guide walks you through the process of installing and setting up the Python & Terraform Project
Template system.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.11+**: The template system requires Python 3.11 or higher

  - Verify with: `python --version` or `python3 --version`
  - Download from: [python.org](https://www.python.org/downloads/)

- **Git**: Required for repository management

  - Verify with: `git --version`
  - Download from: [git-scm.com](https://git-scm.com/downloads)

- **pip**: Python package installer (usually included with Python)

  - Verify with: `pip --version` or `pip3 --version`
  - Install with: `python -m ensurepip --upgrade`

## Optional Prerequisites

These tools are optional but recommended for specific components:

- **Terraform** (for infrastructure components):

  - Verify with: `terraform --version`
  - Installation: [terraform.io/downloads](https://www.terraform.io/downloads)

- **Docker** (for containerization components):

  - Verify with: `docker --version`
  - Installation: [docs.docker.com/get-docker](https://docs.docker.com/get-docker/)

## Installation Steps

### 1. Clone the Template Repository

First, clone the template repository to your local machine:

```bash
git clone https://github.com/yourusername/python-terraform-template.git my-project-template
cd my-project-template
```

### 2. Install Required Python Packages

The template system requires a few Python packages to function properly:

```bash
# Create a virtual environment (recommended)
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install required packages
pip install pyyaml
```

### 3. Verify the Installation

Run the template processor to verify that it's working correctly:

```bash
python scripts/template_processor.py --info
```

You should see output similar to:

```
Template: Python & Terraform Project Template
Version: 1.0.0
Description: A production-ready Python and Terraform project template for enterprise data engineering
```

### 4. Explore Available Components

List the available components to understand what's included in the template:

```bash
python scripts/template_processor.py --list-components
```

## Initial Configuration

Before initializing projects with the template, you might want to customize certain aspects:

### Customizing Presets

You can modify the built-in presets by editing the `PRESETS` dictionary in
`scripts/init_project.py`:

```python
PRESETS = {
    "custom_preset": {
        "description": "Your custom preset description",
        "components": {
            "aws": True,
            "terraform": True,
            # Configure other components as needed
        },
    },
    # Add more presets as needed
}
```

### Adding New Components

To add a new component to the template:

1. Create the component files in the appropriate directories
1. Add the component to the `template_manifest.yml` file:

```yaml
components:
  # Your new component
  - name: "your_component"
    description: "Description of your component"
    required: false
    files:
      - "path/to/component/files/*"
    dependencies: []
```

3. Update the initialization script if needed

## Platform-Specific Considerations

### Windows

- Use PowerShell or Command Prompt for commands
- Path separators are backslashes (`\`)
- Activate virtual environment with `.venv\Scripts\activate`

### macOS/Linux

- Use Terminal for commands
- Path separators are forward slashes (`/`)
- Activate virtual environment with `source .venv/bin/activate`

### WSL (Windows Subsystem for Linux)

If using WSL on Windows:

- Follow the Linux instructions
- Ensure file permissions are properly set
- Consider using VS Code's Remote WSL extension for seamless integration

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'yaml'**

   - Install pyyaml: `pip install pyyaml`

1. **FileNotFoundError: Manifest file not found**

   - Ensure you're running commands from the project root directory
   - Check that `template_manifest.yml` exists

1. **Permission errors**

   - On Linux/macOS: `chmod +x scripts/*.py` to make scripts executable

1. **Python version issues**

   - Verify you're using Python 3.8+: `python --version`
   - Try using `python3` instead of `python` if needed

### Getting Help

If you encounter issues not covered here:

1. Check the documentation in the `docs/` directory
1. Review the
   [GitHub repository issues](https://github.com/yourusername/python-terraform-template/issues)
1. Open a new issue with details about your problem

## Next Steps

Now that you have installed the template system, you can proceed to:

1. [Initialize your first project](QUICK_START.md)
1. [Learn about the template system architecture](PROJECT_INIT_DOCUMENTATION.md)
1. [Explore the scripts and utilities](scripts/README.md)

## Advanced Installation

### Installing from PyPI (if available)

If the template system is published to PyPI, you can install it directly:

```bash
pip install python-terraform-template
```

### Docker-based Installation

You can also use Docker to run the template system without installing it locally:

```bash
# Build the Docker image
docker build -t python-terraform-template .

# Run the initialization wizard
docker run -it -v $(pwd):/workspace python-terraform-template python scripts/init_project.py
```

## Upgrading

To upgrade to the latest version of the template:

```bash
# Pull the latest changes
git pull origin main

# Install any new dependencies
pip install -r requirements.txt
```
