#!/usr/bin/env python3
"""
Update VS Code Settings for Python & Terraform Project Template

This script updates VS Code settings for the project, including:
- Task definitions
- Launch configurations
- Workspace settings
- Extensions recommendations

The settings are tailored based on the project configuration and enabled components.
"""

import json
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path to import template_utils
sys.path.append(str(Path(__file__).resolve().parent))
try:
    from template_utils import (
        ensure_directory,
        print_error,
        print_info,
        print_status,
    )
except ImportError:
    sys.stderr.write(
        "Error: Could not import template_utils. Make sure it exists in the scripts directory.\n"
    )
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VSCODE_DIR = PROJECT_ROOT / ".vscode"


def update_vscode_settings(config: dict[str, Any]) -> None:
    """Update VS Code settings for the project.

    Args:
        config: Project configuration
    """
    # Ensure .vscode directory exists
    ensure_directory(VSCODE_DIR)

    # Update settings
    update_settings_json(config)
    update_tasks_json(config)
    update_launch_json(config)
    update_extensions_json(config)

    print_status("VS Code settings updated successfully")


def update_settings_json(config: dict[str, Any]) -> None:
    """Update VS Code settings.json file.

    Args:
        config: Project configuration
    """
    settings_path = VSCODE_DIR / "settings.json"
    settings = {}

    # Load existing settings if they exist
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text())
        except Exception as e:
            print_error(f"Error loading settings.json: {e}")
            settings = {}

    # Python settings
    settings.update(
        {
            "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
            "python.analysis.typeCheckingMode": "basic",
            "python.terminal.activateEnvironment": True,
            "python.formatting.provider": "ruff",
            "python.linting.enabled": True,
            "python.linting.lintOnSave": True,
            "python.testing.pytestEnabled": True,
            "python.testing.unittestEnabled": False,
            "python.testing.nosetestsEnabled": False,
            "python.testing.pytestArgs": ["tests"],
            "python.languageServer": "Pylance",
            "editor.codeActionsOnSave": {
                "source.organizeImports": True,
            },
            "editor.formatOnSave": True,
            "editor.formatOnType": True,
            "editor.rulers": [100],
            "files.trimTrailingWhitespace": True,
            "files.insertFinalNewline": True,
            "files.trimFinalNewlines": True,
            "[python]": {
                "editor.formatOnSave": True,
                "editor.formatOnPaste": True,
                "editor.defaultFormatter": "charliermarsh.ruff",
                "editor.codeActionsOnSave": {"source.fixAll": True, "source.organizeImports": True},
            },
        }
    )

    # Terraform settings
    if config["components"].get("terraform", False):
        settings.update(
            {
                "terraform.languageServer.enable": True,
                "terraform.format.enable": True,
                "terraform.format.formatOnSave": True,
                "terraform.validate.enable": True,
            }
        )

    # Write settings to file
    settings_path.write_text(json.dumps(settings, indent=4) + "\n")
    print_info("Updated settings.json")


def update_tasks_json(config: dict[str, Any]) -> None:
    """Update VS Code tasks.json file.

    Args:
        config: Project configuration
    """
    tasks_path = VSCODE_DIR / "tasks.json"
    tasks_data = {"version": "2.0.0", "tasks": []}

    # Load existing tasks if they exist
    if tasks_path.exists():
        try:
            tasks_data = json.loads(tasks_path.read_text())
        except Exception as e:
            print_error(f"Error loading tasks.json: {e}")
            tasks_data = {"version": "2.0.0", "tasks": []}

    # Basic Python tasks
    tasks = [
        {
            "label": "🔧 Setup Dev Environment",
            "type": "shell",
            "command": "python scripts/unified_setup.py",
            "group": "build",
            "presentation": {"reveal": "always", "panel": "new"},
        },
        {
            "label": "🧪 Run Tests",
            "type": "shell",
            "command": "pytest",
            "group": {"kind": "test", "isDefault": True},
            "presentation": {"reveal": "always", "panel": "dedicated"},
        },
        {
            "label": "📊 Run Tests with Coverage",
            "type": "shell",
            "command": "pytest --cov=src --cov-report=html",
            "group": "test",
            "presentation": {"reveal": "always", "panel": "dedicated"},
        },
        {
            "label": "🧹 Format Code",
            "type": "shell",
            "command": "ruff format .",
            "group": "build",
            "presentation": {"reveal": "silent", "panel": "dedicated"},
        },
        {
            "label": "🔍 Check Linting",
            "type": "shell",
            "command": "ruff check .",
            "group": "build",
            "presentation": {"reveal": "always", "panel": "dedicated"},
            "problemMatcher": {
                "owner": "python",
                "fileLocation": ["relative", "${workspaceFolder}"],
                "pattern": {
                    "regexp": "^(.+):(\\d+):(\\d+): (.+)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "message": 4,
                },
            },
        },
        {
            "label": "🛠️ Fix Linting",
            "type": "shell",
            "command": "ruff check --fix .",
            "group": "build",
            "presentation": {"reveal": "silent", "panel": "dedicated"},
        },
        {
            "label": "✅ Run Pre-commit",
            "type": "shell",
            "command": "pre-commit run --all-files",
            "group": "build",
            "presentation": {"reveal": "always", "panel": "dedicated"},
        },
        {
            "label": "♻️ Clean Project",
            "type": "shell",
            "command": "python scripts/tasks.py clean",
            "group": "build",
            "presentation": {"reveal": "always", "panel": "dedicated"},
        },
        {
            "label": "📋 Project Health Check",
            "type": "shell",
            "command": "python scripts/project_health_dashboard.py",
            "group": "build",
            "presentation": {"reveal": "always", "panel": "dedicated"},
        },
    ]

    # Documentation tasks
    if config["components"].get("documentation", False):
        tasks.extend(
            [
                {
                    "label": "📖 Serve Documentation",
                    "type": "shell",
                    "command": "hatch run docs:serve",
                    "group": "build",
                    "presentation": {"reveal": "always", "panel": "dedicated"},
                },
                {
                    "label": "📖 Build Documentation",
                    "type": "shell",
                    "command": "hatch run docs:build",
                    "group": "build",
                    "presentation": {"reveal": "always", "panel": "dedicated"},
                },
            ]
        )

    # Docker tasks
    if config["components"].get("docker", False):
        tasks.extend(
            [
                {
                    "label": "🐳 Start Docker Environment",
                    "type": "shell",
                    "command": "docker-compose up -d",
                    "group": "build",
                    "presentation": {"reveal": "always", "panel": "dedicated"},
                },
                {
                    "label": "🐳 Stop Docker Environment",
                    "type": "shell",
                    "command": "docker-compose down",
                    "group": "build",
                    "presentation": {"reveal": "always", "panel": "dedicated"},
                },
            ]
        )

    # Terraform tasks
    if config["components"].get("terraform", False):
        tasks.extend(
            [
                {
                    "label": "🏗️ Terraform Init",
                    "type": "shell",
                    "command": "cd infrastructure/terraform && terraform init",
                    "group": "build",
                    "presentation": {"reveal": "always", "panel": "dedicated"},
                },
                {
                    "label": "🏗️ Terraform Plan",
                    "type": "shell",
                    "command": "cd infrastructure/terraform && terraform plan",
                    "group": "build",
                    "presentation": {"reveal": "always", "panel": "dedicated"},
                },
                {
                    "label": "🏗️ Terraform Validate",
                    "type": "shell",
                    "command": "cd infrastructure/terraform && terraform validate",
                    "group": "build",
                    "presentation": {"reveal": "always", "panel": "dedicated"},
                },
            ]
        )

    # Update tasks in tasks_data
    tasks_data["tasks"] = tasks

    # Write tasks to file
    tasks_path.write_text(json.dumps(tasks_data, indent=4) + "\n")
    print_info("Updated tasks.json")


def update_launch_json(config: dict[str, Any]) -> None:
    """Update VS Code launch.json file.

    Args:
        config: Project configuration
    """
    launch_path = VSCODE_DIR / "launch.json"
    launch_data = {"version": "0.2.0", "configurations": []}

    # Load existing launch configurations if they exist
    if launch_path.exists():
        try:
            launch_data = json.loads(launch_path.read_text())
        except Exception as e:
            print_error(f"Error loading launch.json: {e}")
            launch_data = {"version": "0.2.0", "configurations": []}

    # Basic Python launch configurations
    configurations = [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": True,
        },
        {
            "name": "Python: Debug Tests",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "purpose": ["debug-test"],
            "console": "integratedTerminal",
            "justMyCode": False,
        },
    ]

    # Package launch configuration
    package_name = config.get("package_name", "")
    if package_name:
        configurations.append(
            {
                "name": f"Python: {package_name}",
                "type": "python",
                "request": "launch",
                "module": f"{package_name}",
                "console": "integratedTerminal",
                "justMyCode": True,
            }
        )

    # API launch configuration
    if config["components"].get("api", False):
        configurations.append(
            {
                "name": "Python: API Server",
                "type": "python",
                "request": "launch",
                "module": f"{package_name}.api.main",
                "console": "integratedTerminal",
                "justMyCode": True,
                "env": {"DEBUG": "1"},
            }
        )

    # Update configurations in launch_data
    launch_data["configurations"] = configurations

    # Write launch configurations to file
    launch_path.write_text(json.dumps(launch_data, indent=4) + "\n")
    print_info("Updated launch.json")


def update_extensions_json(config: dict[str, Any]) -> None:
    """Update VS Code extensions.json file.

    Args:
        config: Project configuration
    """
    extensions_path = VSCODE_DIR / "extensions.json"
    extensions_data = {"recommendations": [], "unwantedRecommendations": []}

    # Load existing extensions if they exist
    if extensions_path.exists():
        try:
            extensions_data = json.loads(extensions_path.read_text())
        except Exception as e:
            print_error(f"Error loading extensions.json: {e}")
            extensions_data = {"recommendations": [], "unwantedRecommendations": []}

    # Basic extensions
    recommendations = [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff",
        "streetsidesoftware.code-spell-checker",
        "njpwerner.autodocstring",
        "mhutchie.git-graph",
        "eamodio.gitlens",
        "yzhang.markdown-all-in-one",
    ]

    # Terraform extensions
    if config["components"].get("terraform", False):
        recommendations.extend(["hashicorp.terraform", "4ops.terraform", "tfsec.tfsec"])

    # Docker extensions
    if config["components"].get("docker", False):
        recommendations.extend(["ms-azuretools.vscode-docker"])

    # Documentation extensions
    if config["components"].get("documentation", False):
        recommendations.extend(["bierner.markdown-preview-github-styles", "tomoki1207.pdf"])

    # Update recommendations in extensions_data
    extensions_data["recommendations"] = list(set(recommendations))

    # Write extensions to file
    extensions_path.write_text(json.dumps(extensions_data, indent=4) + "\n")
    print_info("Updated extensions.json")


def main() -> None:
    """Main entry point for the script."""
    # Get configuration from command line argument or use defaults
    if len(sys.argv) > 1 and sys.argv[1].endswith((".json", ".yml", ".yaml")):
        config_path = sys.argv[1]
        try:
            if config_path.endswith(".json"):
                import json

                with open(config_path) as f:
                    config = json.load(f)
            else:
                import yaml

                with open(config_path) as f:
                    config = yaml.safe_load(f)
            print_info(f"Loaded configuration from {config_path}")
        except Exception as e:
            print_error(f"Error loading configuration: {e}")
            sys.exit(1)
    else:
        # Use default configuration
        config = {
            "project_name": "my-project",
            "package_name": "my_project",
            "components": {"terraform": True, "docker": True, "documentation": True, "api": False},
        }

    # Update VS Code settings
    update_vscode_settings(config)


if __name__ == "__main__":
    main()
