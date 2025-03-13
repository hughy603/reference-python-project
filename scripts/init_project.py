#!/usr/bin/env python3
"""
Project Initialization Script for Python & Terraform Template

This script provides an interactive wizard to customize the template
for specific project needs. It handles:
- Project metadata customization
- Package renaming
- Component inclusion/exclusion
- Environment setup
- Git repository initialization

Usage:
    python scripts/init_project.py                    # Interactive wizard
    python scripts/init_project.py --quick            # Use defaults with minimal prompting
    python scripts/init_project.py --config my_config.yml  # Use configuration from file
    python scripts/init_project.py --preset data_engineering  # Use a predefined preset

Options:
    --non-interactive  Run in non-interactive mode using defaults or config file
    --config FILE      Load configuration from YAML file
    --preset NAME      Use a predefined configuration preset
    --quick            Use defaults for most options with minimal interaction
    --keep-git         Keep existing Git history (default: start fresh)
    --skip-env         Skip virtual environment creation
    --verbose          Show detailed output during initialization
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# Import utility functions early
from template_utils import (
    print_success,
    prompt_for_value,
    setup_venv,
    slugify,
    substitute_variables,
)

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Try to import template processor
try:
    from template_processor import TemplateProcessor

    TEMPLATE_PROCESSOR_AVAILABLE = True
except ImportError:
    TEMPLATE_PROCESSOR_AVAILABLE = False

# Detect platform
PLATFORM = platform.system()
IS_WINDOWS = PLATFORM == "Windows"
IS_WSL = "microsoft-standard" in platform.release().lower() if not IS_WINDOWS else False
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Console colors
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
BOLD = "\033[1m"
NC = "\033[0m"  # No Color

# Disable colors if not supported
if IS_WINDOWS and "WT_SESSION" not in os.environ:
    GREEN = YELLOW = RED = BLUE = BOLD = NC = ""

# Default configuration
DEFAULT_CONFIG = {
    "project_name": "reference-python-project",
    "package_name": "reference_python_project",
    "description": "A reference Python project with best practices",
    "author": "Your Name",
    "email": "your.email@example.com",
    "organization": "",
    "version": "0.1.0",
    "components": {
        "aws": True,
        "terraform": True,
        "cloudformation": False,
        "docker": True,
        "documentation": True,
        "ci_cd": True,
        "testing": True,
        "data_pipelines": False,
        "api": False,
        "ml": False,
    },
}

# Predefined presets for common project types
PRESETS = {
    "data_engineering": {
        "description": "Data engineering project with AWS infrastructure",
        "components": {
            "aws": True,
            "terraform": True,
            "cloudformation": False,
            "docker": True,
            "documentation": True,
            "ci_cd": True,
            "testing": True,
            "data_pipelines": True,
            "api": False,
            "ml": False,
        },
    },
    "web_api": {
        "description": "Web API project with AWS infrastructure",
        "components": {
            "aws": True,
            "terraform": True,
            "cloudformation": False,
            "docker": True,
            "documentation": True,
            "ci_cd": True,
            "testing": True,
            "data_pipelines": False,
            "ml": False,
            "api": True,
        },
    },
    "machine_learning": {
        "description": "Machine learning project with AWS infrastructure",
        "components": {
            "aws": True,
            "terraform": True,
            "cloudformation": False,
            "docker": True,
            "documentation": True,
            "ci_cd": True,
            "testing": True,
            "data_pipelines": True,
            "ml": True,
            "api": True,
        },
    },
    "minimal": {
        "description": "Minimal Python project without infrastructure components",
        "components": {
            "aws": False,
            "terraform": False,
            "cloudformation": False,
            "docker": False,
            "documentation": True,
            "ci_cd": True,
            "testing": True,
            "data_pipelines": False,
            "ml": False,
            "api": False,
        },
    },
}

# Type definitions
ConfigDict = dict[str, Any]


def print_status(message: str) -> None:
    """Print a status message with a green checkmark."""
    print(f"{GREEN}✓ {message}{NC}")


def print_step(message: str) -> None:
    """Print a step message with a blue bullet."""
    print(f"{BLUE}● {message}{NC}")


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"{BLUE}i {message}{NC}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"{YELLOW}⚠ {message}{NC}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"{RED}✗ {message}{NC}")


def prompt(message: str, default: Any = None) -> str:
    """Prompt the user for input with a default value."""
    default_str = f" [{default}]" if default else ""
    user_input = input(f"{message}{default_str}: ")
    return user_input.strip() if user_input else default


def prompt_boolean(message: str, default: bool = False) -> bool:
    """Prompt the user for a yes/no answer."""
    default_str = "Y/n" if default else "y/N"
    user_input = input(f"{message} [{default_str}]: ").strip().lower()

    if not user_input:
        return default

    return user_input.startswith("y")


def snake_case(text: str) -> str:
    """Convert text to snake_case."""
    # Replace non-alphanumeric characters with underscores
    s1 = re.sub(r"[^a-zA-Z0-9]", "_", text.strip().lower())
    # Replace consecutive underscores with a single underscore
    s2 = re.sub(r"_+", "_", s1)
    # Remove leading/trailing underscores
    return s2.strip("_")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Initialize a new project from the template.")

    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run in non-interactive mode using defaults or config file",
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Load configuration from YAML or JSON file",
    )

    parser.add_argument(
        "--preset",
        type=str,
        choices=list(PRESETS.keys()),
        help="Use a predefined configuration preset",
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Use defaults for most options with minimal interaction",
    )

    parser.add_argument(
        "--keep-git",
        action="store_true",
        help="Keep existing Git history (default: start fresh)",
    )

    parser.add_argument(
        "--skip-env",
        action="store_true",
        help="Skip virtual environment creation",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output during initialization",
    )

    parser.add_argument(
        "--manifest",
        type=str,
        default=str(PROJECT_ROOT / "template_manifest.yml"),
        help="Path to template manifest file",
    )

    return parser.parse_args()


def load_config_file(args_or_path: str | Any) -> dict[str, Any]:
    """Load configuration from a YAML or JSON file.

    Args:
        args_or_path: Path to the configuration file or args object with config attribute

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If the configuration file does not exist
        ValueError: If the configuration file format is unsupported
    """
    # Get file path from args object or use directly if string
    if isinstance(args_or_path, str):
        file_path = args_or_path
    else:
        file_path = args_or_path.config

    path = Path(file_path)

    if not path.exists():
        print_error(f"Configuration file not found: {file_path}")
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    try:
        if path.suffix.lower() in [".yml", ".yaml"]:
            if not YAML_AVAILABLE:
                print_error("YAML support requires PyYAML. Install with: pip install pyyaml")
                raise ImportError("YAML support requires PyYAML")
            with open(path) as f:
                return yaml.safe_load(f)
        elif path.suffix.lower() == ".json":
            with open(path) as f:
                return json.load(f)
        else:
            print_error(f"Unsupported configuration file format: {path.suffix}")
            raise ValueError(f"Unsupported configuration file format: {path.suffix}")
    except Exception as e:
        if not isinstance(e, (FileNotFoundError, ImportError, ValueError)):
            print_error(f"Error loading configuration file: {e}")
            raise ValueError(f"Error loading configuration file: {e}")
        raise


def apply_preset(preset_name: str, config: dict[str, Any]) -> dict[str, Any]:
    """Apply a predefined preset to the configuration."""
    if preset_name not in PRESETS:
        print_error(
            f"Preset '{preset_name}' not found. Available presets: {', '.join(PRESETS.keys())}"
        )
        return config

    preset = PRESETS[preset_name]

    # Merge the preset with current config
    for key, value in preset.items():
        if isinstance(value, dict) and key in config and isinstance(config[key], dict):
            # For nested dictionaries, merge them
            config[key].update(value)
        else:
            # For other values, replace them
            config[key] = value

    return config


def get_available_components(manifest_path: str) -> list[dict[str, Any]]:
    """Get a list of available components from the manifest."""
    if not TEMPLATE_PROCESSOR_AVAILABLE:
        # Fall back to default components if template processor is not available
        return [
            {"name": name, "description": "", "required": False}
            for name in DEFAULT_CONFIG["components"]
        ]

    try:
        from template_processor import TemplateProcessor

        processor = TemplateProcessor(manifest_path)
        return processor.list_components()
    except Exception as e:
        print_warning(f"Error loading components from manifest: {e}")
        # Fall back to default components
        return [
            {"name": name, "description": "", "required": False}
            for name in DEFAULT_CONFIG["components"]
        ]


def interactive_wizard(defaults: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    """Run the interactive wizard to collect project configuration."""
    config = defaults.copy()
    quick_mode = args.quick
    manifest_path = args.manifest

    # Print welcome message
    print(f"\n{BOLD}Project Initialization Wizard{NC}")
    print("This wizard will help you set up a new project from the template.")
    print("Press Ctrl+C at any time to cancel.\n")

    # Basic project information
    print(f"{BOLD}=== Project Information ==={NC}")
    config["project_name"] = prompt("Project name", defaults["project_name"])
    config["package_name"] = prompt(
        "Package name (Python import name)",
        defaults["package_name"] or snake_case(config["project_name"]),
    )
    config["description"] = prompt("Project description", defaults["description"])

    if not quick_mode:
        config["author"] = prompt("Author name", defaults["author"])
        config["email"] = prompt("Author email", defaults["email"])
        config["organization"] = prompt("Organization", defaults["organization"])

    config["version"] = prompt("Initial version", defaults["version"])

    # Component selection
    print(f"\n{BOLD}=== Component Selection ==={NC}")
    print("Select which components to include in your project:")

    components = config["components"]
    available_components = get_available_components(manifest_path)

    # Group components by type for better organization
    component_groups = {
        "Infrastructure": ["aws", "terraform", "cloudformation"],
        "Development": ["docker", "documentation", "testing", "ci_cd"],
        "Features": ["data_pipelines", "api", "ml"],
    }

    # Create a mapping of component names to their details
    component_details = {comp["name"]: comp for comp in available_components}

    # Process components by group
    for group_name, group_components in component_groups.items():
        if group_name:
            print(f"\n{group_name}:")

        for comp_name in group_components:
            # Skip if component not in manifest
            if comp_name not in components:
                continue

            # Get component details from manifest if available
            comp_details = component_details.get(comp_name, {})
            description = comp_details.get("description", "")
            required = comp_details.get("required", False)

            # If component is required, show it as enabled but don't prompt
            if required:
                components[comp_name] = True
                print(f"  - {comp_name.replace('_', ' ').title()}: {GREEN}Enabled{NC} (Required)")
                continue

            # Add description if available
            prompt_text = f"Include {comp_name.replace('_', ' ')} support?"
            if description and not quick_mode:
                prompt_text = f"Include {comp_name.replace('_', ' ')} support? ({description})"

            # Prompt for component
            if comp_name == "aws" or not quick_mode or comp_name in ["data_pipelines", "api", "ml"]:
                components[comp_name] = prompt_boolean(prompt_text, components[comp_name])

    # Handle component dependencies
    handle_component_dependencies(components)

    # Advanced configuration
    if not quick_mode and prompt_boolean("Configure advanced settings?", False):
        # Advanced configuration could go here
        pass

    # Review and confirm
    print(f"\n{BOLD}=== Configuration Summary ==={NC}")
    print_config_summary(config)

    if not prompt_boolean("Proceed with this configuration?", True):
        print("Restarting wizard...")
        return interactive_wizard(defaults, args)

    return config


def handle_component_dependencies(components: dict[str, bool]) -> None:
    """Handle component dependencies and conflicts."""
    # If AWS is disabled, disable dependent components
    if not components.get("aws", False):
        if components.get("terraform", False):
            print_warning("Disabling Terraform support because AWS is disabled")
            components["terraform"] = False

        if components.get("cloudformation", False):
            print_warning("Disabling CloudFormation support because AWS is disabled")
            components["cloudformation"] = False


def print_config_summary(config: dict[str, Any]) -> None:
    """Print a summary of the configuration."""
    print(f"Project Name: {BOLD}{config['project_name']}{NC}")
    print(f"Package Name: {BOLD}{config['package_name']}{NC}")
    print(f"Description: {config['description']}")
    print(f"Version: {config['version']}")

    if config.get("author"):
        print(f"Author: {config['author']} <{config['email']}>")

    if config.get("organization"):
        print(f"Organization: {config['organization']}")

    print("\nComponents:")
    for component, enabled in config["components"].items():
        status = f"{GREEN}Enabled{NC}" if enabled else f"{YELLOW}Disabled{NC}"
        print(f"  - {component.replace('_', ' ').title()}: {status}")


def initialize_project(config: dict[str, Any], args: argparse.Namespace) -> None:
    """Execute the project initialization based on the configuration."""
    steps = [
        ("Validating configuration", validate_configuration),
        ("Creating basic structure", create_basic_structure),
        ("Updating metadata", update_metadata),
        ("Renaming packages", rename_packages),
    ]

    # Process template components if template processor is available
    if TEMPLATE_PROCESSOR_AVAILABLE and Path(args.manifest).exists():
        steps.append(
            (
                "Processing template components",
                lambda c: process_template_components(c, args.manifest, args.verbose),
            )
        )
    else:
        # Fall back to basic component configuration
        steps.append(("Configuring components", configure_components))

    steps.extend(
        [
            ("Cleaning up template artifacts", cleanup_template),
        ]
    )

    if not args.skip_env:
        steps.append(("Setting up environment", setup_environment))

    if not args.keep_git:
        steps.append(("Initializing git repository", initialize_git))

    for step_name, step_function in steps:
        print_step(step_name)
        try:
            step_function(config)
            print_status("Done")
        except Exception as e:
            print_error(f"Error during {step_name.lower()}: {e}")
            if args.verbose:
                import traceback

                traceback.print_exc()
            sys.exit(1)


def process_template_components(
    config: dict[str, Any], manifest_path: str, verbose: bool = False
) -> None:
    """Process template components using the TemplateProcessor."""
    try:
        from template_processor import TemplateProcessor

        processor = TemplateProcessor(manifest_path, verbose=verbose)
        processor.process_template(config)
    except Exception as e:
        print_warning(f"Error processing template components: {e}")
        print_info("Falling back to basic component configuration")
        configure_components(config)


def validate_configuration(config: dict[str, Any]) -> None:
    """Validate the configuration for consistency and correctness."""
    # Validate project name
    if not config.get("project_name"):
        raise ValueError("Project name cannot be empty")

    # Validate package name
    if not config.get("package_name"):
        raise ValueError("Package name cannot be empty")

    if not re.match(r"^[a-z][a-z0-9_]*$", config["package_name"]):
        raise ValueError(
            "Package name must start with a lowercase letter and "
            "contain only lowercase letters, numbers, and underscores"
        )

    # Ensure component configuration is consistent
    handle_component_dependencies(config["components"])


def create_basic_structure(config: dict[str, Any]) -> None:
    """Create or verify the basic project structure."""
    # Ensure src directory exists
    src_dir = PROJECT_ROOT / "src"
    if not src_dir.exists():
        src_dir.mkdir(parents=True)

    # Ensure tests directory exists
    tests_dir = PROJECT_ROOT / "tests"
    if not tests_dir.exists():
        tests_dir.mkdir(parents=True)
        # Create an empty __init__.py file
        (tests_dir / "__init__.py").touch()


def update_metadata(config: dict[str, Any]) -> None:
    """Update project metadata in key files."""
    # Update pyproject.toml
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        # Replace project name, version, description, etc.
        content = re.sub(r'name = ".*"', f'name = "{config["package_name"]}"', content)
        content = re.sub(r'version = ".*"', f'version = "{config["version"]}"', content)
        content = re.sub(r'description = ".*"', f'description = "{config["description"]}"', content)

        if config.get("author") and config.get("email"):
            author_pattern = r"authors = \[.*\]"
            author_replacement = f'authors = ["{config["author"]} <{config["email"]}>"]'
            if re.search(author_pattern, content):
                content = re.sub(author_pattern, author_replacement, content)

        pyproject_path.write_text(content)
        print_info("Updated metadata in pyproject.toml")

    # Update setup.py if it exists
    setup_path = PROJECT_ROOT / "setup.py"
    if setup_path.exists():
        content = setup_path.read_text()

        # Replace name
        content = re.sub(r'name=".*"', f'name="{config["package_name"]}"', content)

        # Replace version
        content = re.sub(r'version=".*"', f'version="{config["version"]}"', content)

        # Replace description
        content = re.sub(r'description=".*"', f'description="{config["description"]}"', content)

        # Update author info if provided
        if config.get("author"):
            content = re.sub(r'author=".*"', f'author="{config["author"]}"', content)

        if config.get("email"):
            content = re.sub(r'author_email=".*"', f'author_email="{config["email"]}"', content)

        setup_path.write_text(content)
        print_info("Updated metadata in setup.py")

    # Update README.md
    readme_path = PROJECT_ROOT / "README.md"
    if readme_path.exists():
        content = readme_path.read_text()
        # Replace the title and description
        lines = content.split("\n")
        if lines and lines[0].startswith("# "):
            lines[0] = f"# {config['project_name']}"

            # Try to find and replace the description paragraph
            for i, line in enumerate(lines[1:15], 1):
                if line and not line.startswith("#") and not line.startswith("<"):
                    lines[i] = config["description"]
                    break

        readme_path.write_text("\n".join(lines))
        print_info("Updated project information in README.md")


def rename_packages(project_root: Path, package_name: str | None = None) -> None:
    """Rename the default package to the specified name.

    Args:
        project_root: Root directory of the project
        package_name: New package name (snake_case)
    """
    if not package_name:
        return

    # Original package names to rename
    original_packages = ["reference_python_project", "reference-python-project"]

    # Find all Python files
    python_files = list(project_root.glob("**/*.py"))
    python_files.extend(project_root.glob("**/*.md"))
    python_files.extend(project_root.glob("**/pyproject.toml"))
    python_files.extend(project_root.glob("**/setup.py"))
    python_files.extend(project_root.glob("**/setup.cfg"))
    python_files.extend(project_root.glob("**/.env*"))

    # Update imports in all Python files
    for file_path in python_files:
        if not file_path.exists():
            continue

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Replace all occurrences of the original package name
            modified = False
            for original in original_packages:
                if original in content:
                    content = content.replace(original, package_name)
                    modified = True

            if modified:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

        except Exception as e:
            print(f"Error updating imports in {file_path}: {e}")

    # Rename the actual package directory if it exists
    for original in original_packages:
        original_dir = project_root / original.replace("-", "_")
        if original_dir.exists() and original_dir.is_dir():
            new_dir = project_root / package_name
            try:
                shutil.move(str(original_dir), str(new_dir))
                print(f"Renamed package directory from {original_dir} to {new_dir}")
            except Exception as e:
                print(f"Error renaming package directory: {e}")


def configure_components(config: dict[str, Any]) -> None:
    """Enable or disable specific components based on user selection."""
    components = config["components"]

    # Configure AWS components
    if not components["aws"]:
        # Remove AWS-specific files and directories
        aws_patterns = [
            "infrastructure/terraform/aws",
            "src/**/aws",
            ".env.aws.template",
        ]

        for pattern in aws_patterns:
            remove_matching_files(pattern)

    # Configure Terraform
    if not components["terraform"]:
        terraform_dir = PROJECT_ROOT / "infrastructure" / "terraform"
        if terraform_dir.exists():
            shutil.rmtree(terraform_dir)
            print_info("Removed Terraform configuration")

    # Configure CloudFormation
    if not components["cloudformation"]:
        cf_dir = PROJECT_ROOT / "infrastructure" / "cloudformation"
        if cf_dir.exists():
            shutil.rmtree(cf_dir)
            print_info("Removed CloudFormation configuration")

    # Configure Docker
    if not components["docker"]:
        docker_files = ["Dockerfile", "docker-compose.yml"]
        for file in docker_files:
            file_path = PROJECT_ROOT / file
            if file_path.exists():
                file_path.unlink()
                print_info(f"Removed {file}")

    # Configure documentation
    if not components["documentation"]:
        docs_dir = PROJECT_ROOT / "docs"
        if docs_dir.exists():
            # Keep minimal docs
            for item in docs_dir.glob("*"):
                if item.name not in ["README.md", "index.md"]:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
            print_info("Simplified documentation structure")

    # Configure testing
    if not components["testing"]:
        testing_files = [
            "tests/conftest.py",
            "tests/test_*.py",
            "pytest.ini",
        ]

        for pattern in testing_files:
            remove_matching_files(pattern)

        print_info("Removed testing configuration")

    # Configure CI/CD
    if not components["ci_cd"]:
        github_dir = PROJECT_ROOT / ".github"
        if github_dir.exists():
            shutil.rmtree(github_dir)
            print_info("Removed GitHub Actions workflows")

    # Configure data pipelines
    if not components["data_pipelines"]:
        data_pipeline_patterns = [
            "src/**/pipeline",
            "src/**/etl",
            "src/**/data",
        ]

        for pattern in data_pipeline_patterns:
            remove_matching_files(pattern)

        print_info("Removed data pipeline components")

    # Configure API
    if not components["api"]:
        api_patterns = [
            "src/**/api",
            "src/**/rest",
            "src/**/graphql",
        ]

        for pattern in api_patterns:
            remove_matching_files(pattern)

        print_info("Removed API components")

    # Configure ML
    if not components["ml"]:
        ml_patterns = [
            "src/**/ml",
            "src/**/models",
            "src/**/train",
        ]

        for pattern in ml_patterns:
            remove_matching_files(pattern)

        print_info("Removed machine learning components")


def remove_matching_files(pattern: str) -> None:
    """Remove files or directories matching a glob pattern."""
    paths = list(PROJECT_ROOT.glob(pattern))
    for path in paths:
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        except Exception as e:
            print_warning(f"Error removing {path}: {e}")


def cleanup_template(config: dict[str, Any]) -> None:
    """Clean up template-specific files and artifacts."""
    # Files to be removed from the template
    template_files = [
        "TODO.md",  # Template TODO list
        ".template_version",  # Template version file
    ]

    for file in template_files:
        file_path = PROJECT_ROOT / file
        if file_path.exists():
            try:
                file_path.unlink()
                print_info(f"Removed template file: {file}")
            except Exception as e:
                print_warning(f"Error removing {file}: {e}")


def setup_environment(config: dict[str, Any]) -> None:
    """Set up the project environment based on configuration."""
    # Generate appropriate .env files
    generate_env_files(config)

    # Set up pre-commit hooks
    setup_precommit_hooks()

    # Create a virtual environment if it doesn't exist
    if not (PROJECT_ROOT / ".venv").exists():
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", ".venv"],
                check=True,
                cwd=PROJECT_ROOT,
            )
            print_info("Created virtual environment in .venv")
        except subprocess.CalledProcessError as e:
            print_warning(f"Error creating virtual environment: {e}")

    # Install dependencies
    try:
        pip_command = [
            ".venv/bin/pip" if not IS_WINDOWS else r".venv\Scripts\pip",
            "install",
            "-e",
            ".",
        ]

        subprocess.run(
            pip_command,
            check=True,
            cwd=PROJECT_ROOT,
        )
        print_info("Installed project dependencies")
    except subprocess.CalledProcessError as e:
        print_warning(f"Error installing dependencies: {e}")


def generate_env_files(config: dict[str, Any]) -> None:
    """Generate environment files based on configuration."""
    env_template = ["# Environment variables for {}\n".format(config["project_name"])]

    # Add core environment variables
    env_template.append("# Core settings")
    env_template.append("DEBUG=True")
    env_template.append("LOG_LEVEL=INFO")

    # Add AWS environment variables if AWS is enabled
    if config["components"]["aws"]:
        env_template.append("\n# AWS settings")
        env_template.append("AWS_REGION=us-east-1")
        env_template.append("AWS_PROFILE=default")

    # Add database variables if data pipelines are enabled
    if config["components"]["data_pipelines"]:
        env_template.append("\n# Database settings")
        env_template.append("DB_HOST=localhost")
        env_template.append("DB_PORT=5432")
        env_template.append("DB_NAME=development")
        env_template.append("DB_USER=postgres")
        env_template.append("DB_PASSWORD=change_me_in_production")

    # Add API variables if API is enabled
    if config["components"]["api"]:
        env_template.append("\n# API settings")
        env_template.append("API_HOST=0.0.0.0")
        env_template.append("API_PORT=8000")
        env_template.append("API_DEBUG=True")

    # Write the template file
    env_template_path = PROJECT_ROOT / ".env.template"
    env_template_path.write_text("\n".join(env_template))

    # Create a .env file from the template
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        shutil.copy(env_template_path, env_path)

    print_info("Created .env and .env.template files")


def setup_precommit_hooks() -> None:
    """Set up pre-commit hooks for the project."""
    try:
        # Check if pre-commit is available
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "pre-commit"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print_info("Installing pre-commit...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pre-commit"],
                check=True,
            )

        # Install pre-commit hooks
        subprocess.run(
            [sys.executable, "-m", "pre_commit", "install"],
            check=True,
            cwd=PROJECT_ROOT,
        )
        print_info("Installed pre-commit hooks")
    except subprocess.CalledProcessError as e:
        print_warning(f"Error setting up pre-commit hooks: {e}")


def initialize_git(project_root: Path, config: dict[str, Any] | None = None) -> None:
    """Initialize a fresh Git repository.

    Args:
        project_root: Project root directory
        config: Configuration dictionary (optional)
    """
    git_dir = project_root / ".git"

    project_name = "new-project"
    if config and "project_name" in config:
        project_name = config["project_name"]

    if git_dir.exists():
        try:
            shutil.rmtree(git_dir)
            print_info("Removed existing Git repository")
        except Exception as e:
            print_warning(f"Error removing existing Git repository: {e}")

    try:
        subprocess.run(
            ["git", "init"],
            check=True,
            cwd=project_root,
        )
        print_info("Initialized fresh Git repository")

        # Create initial commit
        subprocess.run(
            ["git", "add", "."],
            check=True,
            cwd=project_root,
        )

        subprocess.run(
            ["git", "commit", "-m", f"Initial commit for {project_name}"],
            check=True,
            cwd=project_root,
        )

        print_info("Created initial commit")
    except subprocess.CalledProcessError as e:
        print_warning(f"Git initialization failed: {e}")
    except Exception as e:
        print_warning(f"Error during Git initialization: {e}")


def print_welcome() -> None:
    """Print a welcome message."""
    welcome_text = [
        f"{BOLD}╔════════════════════════════════════════════════════════════╗{NC}",
        f"{BOLD}║                                                            ║{NC}",
        f"{BOLD}║  {BLUE}Project Initialization Wizard{NC}{BOLD}                          ║{NC}",
        f"{BOLD}║  {GREEN}Python & Terraform Template{NC}{BOLD}                           ║{NC}",
        f"{BOLD}║                                                            ║{NC}",
        f"{BOLD}╚════════════════════════════════════════════════════════════╝{NC}",
    ]

    print("\n" + "\n".join(welcome_text) + "\n")


def print_success_message(config: dict[str, Any]) -> None:
    """Print a success message."""
    print("\n" + "=" * 80)
    print(f"{GREEN}{BOLD}Project initialized successfully!{NC}\n")
    print(f"Project: {BOLD}{config['project_name']}{NC}")
    print(f"Package: {BOLD}{config['package_name']}{NC}")

    print("\nNext steps:")
    print(f"  1. {BOLD}Explore your new project structure{NC}")
    print(f"  2. {BOLD}Review the generated files and customize as needed{NC}")
    print(f"  3. {BOLD}Activate the virtual environment:{NC}")
    if IS_WINDOWS:
        print(f"     {BLUE}.venv\\Scripts\\activate{NC}")
    else:
        print(f"     {BLUE}source .venv/bin/activate{NC}")
    print(f"  4. {BOLD}Start coding!{NC}")

    print("\nUseful commands:")
    print(f"  {BLUE}make test{NC}       Run tests")
    print(f"  {BLUE}make format{NC}     Format code")
    print(f"  {BLUE}make lint{NC}       Check linting")
    print(f"  {BLUE}make docs{NC}       Build documentation")

    print("\n" + "=" * 80)


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Initialize a new project from the template.")
    parser.add_argument(
        "--config",
        "-c",
        help="Path to a configuration file (YAML or JSON)",
        type=str,
    )
    parser.add_argument(
        "--verbose",
        "-v",
        help="Enable verbose output",
        action="store_true",
    )
    parser.add_argument(
        "--skip-env",
        "-s",
        help="Skip virtual environment setup",
        action="store_true",
    )
    parser.add_argument(
        "--keep-git",
        "-k",
        help="Keep existing Git repository",
        action="store_true",
    )
    parser.add_argument(
        "--manifest",
        "-m",
        help="Path to template manifest file",
        type=str,
        default="template_manifest.yml",
    )

    args = parser.parse_args()

    # Initialize the project
    success = initialize_project_with_config(args)

    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

# Export necessary functions for testing
__all__ = [
    "initialize_git",
    "initialize_project_with_config",
    "load_config_file",
    "prompt_for_value",
    "rename_packages",
    "setup_venv",
    "slugify",
    "snake_case",
    "substitute_variables",
]


def initialize_project_with_config(args: Any) -> bool:
    """Initialize a project using the given arguments.

    This is a wrapper function that handles configuration loading and project
    initialization based on command line arguments.

    Args:
        args: Command line arguments containing configuration options

    Returns:
        bool: True if initialization was successful, False otherwise
    """
    try:
        # Load configuration from file if specified
        config: ConfigDict = DEFAULT_CONFIG.copy()
        if hasattr(args, "config") and args.config:
            loaded_config = load_config_file(args.config)
            if isinstance(loaded_config, dict):
                config.update(loaded_config)

        # Process the template with the configuration
        if TEMPLATE_PROCESSOR_AVAILABLE and "TemplateProcessor" in globals():
            manifest_path = (
                args.manifest
                if hasattr(args, "manifest") and args.manifest
                else "template_manifest.yml"
            )
            processor = TemplateProcessor(
                manifest_path, verbose=args.verbose if hasattr(args, "verbose") else False
            )
            result = processor.process_template(config)
            if not result:
                print_error("Template processing failed")
                return False

        # Substitute variables in files
        if "template_utils" in sys.modules and "substitute_variables" in globals():
            # If we've imported template_utils, use its functions
            substitute_variables(
                PROJECT_ROOT, config, verbose=args.verbose if hasattr(args, "verbose") else False
            )

        # Rename packages
        package_name = config.get("package_name")
        if package_name and isinstance(package_name, str):
            rename_packages(PROJECT_ROOT, package_name)

        # Set up virtual environment if not skipped
        if not (hasattr(args, "skip_env") and args.skip_env):
            if "template_utils" in sys.modules and "setup_venv" in globals():
                setup_venv(
                    PROJECT_ROOT, verbose=args.verbose if hasattr(args, "verbose") else False
                )

        # Initialize Git repository if not keeping existing one
        if not (hasattr(args, "keep_git") and args.keep_git):
            initialize_git(PROJECT_ROOT, config)

        print_success("Project initialization complete!")
        return True

    except Exception as e:
        print_error(f"Project initialization failed: {e}")
        if hasattr(args, "verbose") and args.verbose:
            import traceback

            traceback.print_exc()
        return False
