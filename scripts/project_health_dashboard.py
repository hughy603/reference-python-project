#!/usr/bin/env python
"""
Project Health Dashboard

A simple utility to display the health status of the project, including
test coverage, linting status, and documentation completeness.
"""

import argparse
import os
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

try:
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


@dataclass
class HealthMetric:
    """A health metric for the project."""

    name: str
    status: str
    details: str
    emoji: str
    success: bool
    actions: list[tuple[str, str, Callable[[], Any]]] = (
        None  # (label, description, action_function)
    )

    def __post_init__(self):
        """Initialize default values."""
        if self.actions is None:
            self.actions = []


class StatusLevel(Enum):
    """Status levels for health metrics."""

    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class ProjectHealthDashboard:
    """Displays the health status of the project."""

    def __init__(self, project_root: Path | None = None):
        """Initialize the dashboard with the project root directory."""
        self.project_root = project_root or Path.cwd()
        self.metrics: list[HealthMetric] = []
        self.console = Console() if RICH_AVAILABLE else None

    def run_command(self, command: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
        """Run a command and return the exit code, stdout, and stderr."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)

    def check_test_coverage(self) -> HealthMetric:
        """Check the test coverage of the project."""
        # Run pytest with coverage
        cmd = [sys.executable, "-m", "pytest", "--cov=src", "--cov-report=term"]
        exit_code, stdout, stderr = self.run_command(cmd)

        if exit_code != 0:
            return HealthMetric(
                name="Test Coverage",
                status="FAIL",
                details="Tests failed to run. See errors below.",
                emoji="❌",
                success=False,
                actions=[
                    (
                        "Run Tests",
                        "Re-run tests with detailed output",
                        lambda: self.run_action_command(["pytest", "-v"]),
                    ),
                    ("Fix Common Issues", "Fix common test issues", self.fix_common_test_issues),
                ],
            )

        # Extract coverage percentage
        coverage_line = ""
        for line in stdout.splitlines():
            if "TOTAL" in line and "%" in line:
                coverage_line = line
                break

        if not coverage_line:
            return HealthMetric(
                name="Test Coverage",
                status="WARN",
                details="Could not extract coverage information.",
                emoji="⚠️",
                success=False,
                actions=[
                    (
                        "Run Coverage",
                        "Generate coverage report",
                        lambda: self.run_action_command(
                            ["pytest", "--cov=src", "--cov-report=html"]
                        ),
                    ),
                ],
            )

        # Parse coverage percentage
        try:
            coverage_parts = coverage_line.split()
            coverage_percent = float(coverage_parts[-1].rstrip("%"))

            # Determine status based on coverage threshold
            actions = []
            if coverage_percent >= 80:
                status = "PASS"
                emoji = "✅"
                success = True
            elif coverage_percent >= 60:
                status = "WARN"
                emoji = "⚠️"
                success = True
                actions.append(
                    (
                        "Increase Coverage",
                        "Find modules with low coverage",
                        lambda: self.run_action_command(
                            ["pytest", "--cov=src", "--cov-report=term-missing"]
                        ),
                    )
                )
            else:
                status = "FAIL"
                emoji = "❌"
                success = False
                actions.append(
                    (
                        "Increase Coverage",
                        "Find modules with low coverage",
                        lambda: self.run_action_command(
                            ["pytest", "--cov=src", "--cov-report=term-missing"]
                        ),
                    )
                )
                actions.append(
                    (
                        "Generate Report",
                        "Create detailed HTML report",
                        lambda: self.run_action_command(
                            ["pytest", "--cov=src", "--cov-report=html"]
                        ),
                    )
                )

            return HealthMetric(
                name="Test Coverage",
                status=status,
                details=f"{coverage_percent:.1f}% coverage",
                emoji=emoji,
                success=success,
                actions=actions,
            )
        except (IndexError, ValueError):
            return HealthMetric(
                name="Test Coverage",
                status="WARN",
                details="Could not parse coverage percentage.",
                emoji="⚠️",
                success=False,
                actions=[
                    (
                        "Run Coverage",
                        "Generate coverage report",
                        lambda: self.run_action_command(
                            ["pytest", "--cov=src", "--cov-report=html"]
                        ),
                    ),
                ],
            )

    def check_linting(self) -> HealthMetric:
        """Check the linting status of the project."""
        cmd = ["ruff", "check", "."]
        exit_code, stdout, stderr = self.run_command(cmd)

        if exit_code == 0:
            return HealthMetric(
                name="Linting",
                status="PASS",
                details="No linting issues found.",
                emoji="✅",
                success=True,
                actions=[
                    (
                        "Format Code",
                        "Run ruff formatter",
                        lambda: self.run_action_command(["ruff", "format", "."]),
                    ),
                ],
            )
        else:
            issue_count = len(stdout.splitlines())
            return HealthMetric(
                name="Linting",
                status="FAIL",
                details=f"{issue_count} linting issues found.",
                emoji="❌",
                success=False,
                actions=[
                    (
                        "Fix Linting",
                        "Auto-fix linting issues",
                        lambda: self.run_action_command(["ruff", "check", "--fix", "."]),
                    ),
                    (
                        "Format Code",
                        "Run ruff formatter",
                        lambda: self.run_action_command(["ruff", "format", "."]),
                    ),
                    (
                        "Show Issues",
                        "Show detailed lint issues",
                        lambda: self.run_action_command(["ruff", "check", "--verbose", "."]),
                    ),
                ],
            )

    def check_pre_commit_hooks(self) -> HealthMetric:
        """Check if pre-commit hooks are installed."""
        pre_commit_config = self.project_root / ".pre-commit-config.yaml"
        git_hooks_dir = self.project_root / ".git" / "hooks"
        pre_commit_hook = git_hooks_dir / "pre-commit"

        if not pre_commit_config.exists():
            return HealthMetric(
                name="Pre-commit Hooks",
                status="FAIL",
                details="Pre-commit configuration not found.",
                emoji="❌",
                success=False,
                actions=[
                    (
                        "Create Config",
                        "Create default pre-commit config",
                        self.create_pre_commit_config,
                    ),
                ],
            )

        if not git_hooks_dir.exists() or not pre_commit_hook.exists():
            return HealthMetric(
                name="Pre-commit Hooks",
                status="WARN",
                details="Pre-commit hooks not installed. Run 'pre-commit install'.",
                emoji="⚠️",
                success=False,
                actions=[
                    (
                        "Install Hooks",
                        "Install pre-commit hooks",
                        lambda: self.run_action_command(["pre-commit", "install"]),
                    ),
                ],
            )

        return HealthMetric(
            name="Pre-commit Hooks",
            status="PASS",
            details="Pre-commit hooks are installed.",
            emoji="✅",
            success=True,
            actions=[
                (
                    "Run Hooks",
                    "Run pre-commit on all files",
                    lambda: self.run_action_command(["pre-commit", "run", "--all-files"]),
                ),
                (
                    "Update Hooks",
                    "Update pre-commit hooks",
                    lambda: self.run_action_command(["pre-commit", "autoupdate"]),
                ),
            ],
        )

    def check_documentation(self) -> HealthMetric:
        """Check if documentation can be built."""
        cmd = ["mkdocs", "build", "--strict"]
        exit_code, stdout, stderr = self.run_command(cmd)

        if exit_code == 0:
            return HealthMetric(
                name="Documentation",
                status="PASS",
                details="Documentation builds successfully.",
                emoji="✅",
                success=True,
                actions=[
                    (
                        "Serve Docs",
                        "Start documentation server",
                        lambda: self.run_action_command(["mkdocs", "serve"]),
                    ),
                    (
                        "Build Site",
                        "Build static documentation site",
                        lambda: self.run_action_command(["mkdocs", "build"]),
                    ),
                ],
            )
        else:
            return HealthMetric(
                name="Documentation",
                status="FAIL",
                details="Documentation build failed.",
                emoji="❌",
                success=False,
                actions=[
                    (
                        "Show Errors",
                        "Show documentation build errors",
                        lambda: self.run_action_command(["mkdocs", "build", "--verbose"]),
                    ),
                    (
                        "Fix Common Issues",
                        "Fix common documentation issues",
                        self.fix_common_doc_issues,
                    ),
                ],
            )

    def check_dependencies(self) -> HealthMetric:
        """Check if dependencies are up-to-date."""
        pyproject_toml = self.project_root / "pyproject.toml"

        if not pyproject_toml.exists():
            return HealthMetric(
                name="Dependencies",
                status="WARN",
                details="pyproject.toml not found.",
                emoji="⚠️",
                success=False,
                actions=[
                    ("Create File", "Create basic pyproject.toml", self.create_basic_pyproject),
                ],
            )

        # Check for outdated packages
        cmd = [sys.executable, "-m", "pip", "list", "--outdated"]
        exit_code, stdout, stderr = self.run_command(cmd)

        if exit_code != 0:
            return HealthMetric(
                name="Dependencies",
                status="WARN",
                details="Failed to check for outdated dependencies.",
                emoji="⚠️",
                success=False,
                actions=[
                    (
                        "Check Dependencies",
                        "Check for package security issues",
                        lambda: self.run_action_command(["pip-audit"]),
                    ),
                ],
            )

        outdated_lines = stdout.splitlines()[2:]  # Skip header lines
        num_outdated = len(outdated_lines)

        if num_outdated == 0:
            return HealthMetric(
                name="Dependencies",
                status="PASS",
                details="All dependencies are up-to-date.",
                emoji="✅",
                success=True,
                actions=[
                    (
                        "Check Security",
                        "Check for package security issues",
                        lambda: self.run_action_command(["pip-audit"]),
                    ),
                ],
            )
        else:
            return HealthMetric(
                name="Dependencies",
                status="WARN",
                details=f"{num_outdated} outdated dependencies found.",
                emoji="⚠️",
                success=True,  # Still a success but with warning
                actions=[
                    (
                        "Show Outdated",
                        "List outdated packages",
                        lambda: self.run_action_command(
                            [sys.executable, "-m", "pip", "list", "--outdated"]
                        ),
                    ),
                    ("Update All", "Update all packages", self.update_all_packages),
                    (
                        "Check Security",
                        "Check for package security issues",
                        lambda: self.run_action_command(["pip-audit"]),
                    ),
                ],
            )

    def check_nexus_connection(self) -> HealthMetric:
        """Check connection to Enterprise Nexus repository."""
        try:
            # Try to import the nexus module
            sys.path.insert(0, str(self.project_root / "src"))
            from enterprise_data_engineering.common_utils import nexus_utils as nexus

            # Initialize a client and check connection
            client = nexus.NexusClient()
            connection_ok = client.check_connection()

            if connection_ok:
                return HealthMetric(
                    name="Enterprise Nexus",
                    status="PASS",
                    details=f"Connected to Nexus at {client.repository_url}",
                    emoji="✅",
                    success=True,
                    actions=[
                        (
                            "Configure Pip",
                            "Configure pip to use Nexus",
                            lambda: client.configure_pip(),
                        ),
                        (
                            "Check Connection",
                            "Verify Nexus connection",
                            lambda: client.check_connection(),
                        ),
                    ],
                )
            else:
                return HealthMetric(
                    name="Enterprise Nexus",
                    status="WARN",
                    details="Could not connect to Nexus repository.",
                    emoji="⚠️",
                    success=False,
                    actions=[
                        (
                            "Setup Nexus",
                            "Configure Nexus environment",
                            lambda: nexus.setup_nexus_environment(),
                        ),
                        ("View Config", "Show Nexus configuration", self.show_nexus_config),
                    ],
                )
        except (ImportError, AttributeError) as e:
            return HealthMetric(
                name="Enterprise Nexus",
                status="FAIL",
                details=f"Nexus support is not properly set up: {e!s}",
                emoji="❌",
                success=False,
                actions=[
                    (
                        "Setup Environment",
                        "Set up Nexus environment variables",
                        self.setup_nexus_env_vars,
                    ),
                    (
                        "Check Requirements",
                        "Check necessary Nexus dependencies",
                        self.check_nexus_requirements,
                    ),
                ],
            )

    def run_all_checks(self) -> list[HealthMetric]:
        """Run all health checks and return the results."""
        self.metrics = [
            self.check_test_coverage(),
            self.check_linting(),
            self.check_pre_commit_hooks(),
            self.check_documentation(),
            self.check_dependencies(),
            self.check_nexus_connection(),
        ]
        return self.metrics

    def display_dashboard(self) -> None:
        """Display the health dashboard in the terminal."""
        if not self.metrics:
            self.run_all_checks()

        if RICH_AVAILABLE and self.console:
            self._display_rich_dashboard()
        else:
            self._display_basic_dashboard()

    def _display_basic_dashboard(self) -> None:
        """Display a basic text-based dashboard."""
        print("\n" + "=" * 60)
        print("📋 PROJECT HEALTH DASHBOARD")
        print("=" * 60)

        reset_color = "\033[0m"
        for metric in self.metrics:
            status_color = "\033[92m" if metric.success else "\033[91m"  # Green or Red
            if metric.status == "WARN":
                status_color = "\033[93m"  # Yellow

            print(f"{metric.emoji} {metric.name}: {status_color}{metric.status}{reset_color}")
            print(f"   {metric.details}")

            # Show available quick actions
            if metric.actions:
                print("   Quick actions:")
                for i, (label, description, _) in enumerate(metric.actions, start=1):
                    print(f"   {i}. {label}: {description}")

            print("-" * 60)

        # Overall status
        all_success = all(metric.success for metric in self.metrics)
        if all_success:
            print(f"\n✅ Overall Status: \033[92mHEALTHY{reset_color}")
        else:
            print(f"\n⚠️ Overall Status: \033[91mNEEDS ATTENTION{reset_color}")

        print("=" * 60)
        print("Run 'python scripts/project_health_dashboard.py --help' for more options.")
        print("Use 'python scripts/project_health_dashboard.py --interactive' to run actions.\n")

    def _display_rich_dashboard(self) -> None:
        """Display a rich formatted dashboard."""
        self.console.print("\n")

        # Create main table
        table = Table(box=box.ROUNDED, title="📋 PROJECT HEALTH DASHBOARD", expand=True)
        table.add_column("Status", style="bold")
        table.add_column("Metric", style="bold")
        table.add_column("Details")
        table.add_column("Quick Actions")

        for metric in self.metrics:
            # Set color based on status
            if metric.status == "PASS":
                status_style = "green"
            elif metric.status == "WARN":
                status_style = "yellow"
            else:
                status_style = "red"

            # Format actions
            actions_text = ""
            if metric.actions:
                actions = []
                for i, (label, description, _) in enumerate(metric.actions, start=1):
                    actions.append(f"{i}. [bold]{label}[/bold]: {description}")
                actions_text = "\n".join(actions)

            table.add_row(
                f"[{status_style}]{metric.emoji} {metric.status}[/{status_style}]",
                metric.name,
                metric.details,
                actions_text or "No actions available",
            )

        self.console.print(table)

        # Overall status panel
        all_success = all(metric.success for metric in self.metrics)
        if all_success:
            panel = Panel(
                "✅ [bold green]HEALTHY[/bold green]", title="Overall Status", expand=False
            )
        else:
            panel = Panel(
                "⚠️ [bold red]NEEDS ATTENTION[/bold red]", title="Overall Status", expand=False
            )

        self.console.print(panel)
        self.console.print(
            "\nRun [bold]python scripts/project_health_dashboard.py --help[/bold] for more options."
        )
        self.console.print(
            "Use [bold]python scripts/project_health_dashboard.py --interactive[/bold] to run actions.\n"
        )

    def get_overall_status(self) -> bool:
        """Get the overall project health status."""
        if not self.metrics:
            self.run_all_checks()
        return all(metric.success for metric in self.metrics)

    def run_interactive_mode(self) -> None:
        """Run the dashboard in interactive mode, allowing action execution."""
        if not self.metrics:
            self.run_all_checks()

        self.display_dashboard()

        while True:
            print(
                "\nEnter 'q' to quit or select an action by specifying the metric number and action number."
            )
            print(
                "Format: <metric_number>.<action_number> (e.g., '1.2' for the second action of the first metric)"
            )

            choice = input("\nChoice: ").strip()

            if choice.lower() == "q":
                break

            try:
                if "." in choice:
                    metric_idx, action_idx = choice.split(".")
                    metric_num = int(metric_idx) - 1
                    action_num = int(action_idx) - 1

                    if 0 <= metric_num < len(self.metrics):
                        metric = self.metrics[metric_num]
                        if 0 <= action_num < len(metric.actions):
                            print(
                                f"\nExecuting: {metric.actions[action_num][0]} - {metric.actions[action_num][1]}"
                            )
                            metric.actions[action_num][2]()

                            # Refresh metrics after action
                            print("\nRefreshing metrics...")
                            self.run_all_checks()
                            self.display_dashboard()
                        else:
                            print(f"Invalid action number for metric {metric_num + 1}")
                    else:
                        print(
                            f"Invalid metric number. Please select a number between 1 and {len(self.metrics)}"
                        )
                else:
                    print("Invalid format. Please use format <metric_number>.<action_number>")
            except ValueError:
                print("Invalid input. Please use format <metric_number>.<action_number>")
            except Exception as e:
                print(f"Error executing action: {e}")

    # Helper methods for actions
    def run_action_command(self, command: list[str]) -> None:
        """Run a command and display the output."""
        print(f"\nRunning command: {' '.join(command)}")
        print("-" * 60)

        try:
            # Use subprocess to run the command, displaying output in real-time
            process = subprocess.Popen(
                command,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    print(line.rstrip())

            exit_code = process.poll()
            print("-" * 60)
            print(f"Command completed with exit code: {exit_code}")
        except Exception as e:
            print(f"Error running command: {e}")

    def fix_common_test_issues(self) -> None:
        """Attempt to fix common test issues."""
        print("\nAttempting to fix common test issues...")

        # Create empty __init__.py files in test directories if missing
        tests_dir = self.project_root / "tests"
        if tests_dir.exists():
            for directory in tests_dir.glob("**"):
                if directory.is_dir():
                    init_file = directory / "__init__.py"
                    if not init_file.exists():
                        init_file.touch()
                        print(f"Created empty __init__.py in {directory}")

        # Make sure pytest.ini or conftest.py exists
        pytest_ini = self.project_root / "pytest.ini"
        conftest_py = self.project_root / "conftest.py"

        if not pytest_ini.exists() and not conftest_py.exists():
            with open(conftest_py, "w") as f:
                f.write(
                    """
"""
                    """
# Basic pytest configuration
import pytest
import sys
import os

# Add the src directory to sys.path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

@pytest.fixture
def sample_fixture():
    \"\"\"A sample fixture for tests.\"\"\"
    return {"test_value": "test"}
"""
                )
            print("Created basic conftest.py with project configuration")

    def fix_common_doc_issues(self) -> None:
        """Attempt to fix common documentation issues."""
        print("\nAttempting to fix common documentation issues...")

        # Check if mkdocs.yml exists
        mkdocs_yml = self.project_root / "mkdocs.yml"
        if not mkdocs_yml.exists():
            print("mkdocs.yml is missing. Cannot fix documentation issues.")
            return

        # Check if the docs directory exists and has index.md
        docs_dir = self.project_root / "docs"
        index_md = docs_dir / "index.md"

        if not docs_dir.exists():
            docs_dir.mkdir()
            print("Created docs directory")

        if not index_md.exists():
            with open(index_md, "w") as f:
                f.write("""# Project Documentation

Welcome to the project documentation.

## Overview

This is the main documentation page for the project.
                """)
            print("Created basic index.md in docs directory")

        # Run the MkDocs build with verbose output to identify issues
        self.run_action_command(["mkdocs", "build", "--verbose"])

    def create_pre_commit_config(self) -> None:
        """Create a basic pre-commit configuration file."""
        pre_commit_config = self.project_root / ".pre-commit-config.yaml"

        if pre_commit_config.exists():
            print("Pre-commit config already exists. Not overwriting.")
            return

        with open(pre_commit_config, "w") as f:
            f.write("""# See https://pre-commit.com for more information
# See https://pre-commit.com/hooks.html for more hooks
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
    -   id: check-toml
    -   id: detect-private-key

-   repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
    -   id: ruff
        args: [--fix, --exit-non-zero-on-fix]
    -   id: ruff-format

-   repo: https://github.com/python-jsonschema/check-jsonschema
    rev: 0.27.0
    hooks:
    -   id: check-github-workflows
    -   id: check-dependabot

-   repo: https://github.com/pre-commit/pygrep-hooks
    rev: v1.10.0
    hooks:
    -   id: python-check-blanket-noqa
    -   id: python-no-eval
    -   id: python-use-type-annotations
""")
        print("Created basic pre-commit configuration file")

        # Install pre-commit if needed
        self.run_action_command([sys.executable, "-m", "pip", "install", "pre-commit"])

        # Install the hooks
        self.run_action_command(["pre-commit", "install"])

    def create_basic_pyproject(self) -> None:
        """Create a basic pyproject.toml file."""
        pyproject_toml = self.project_root / "pyproject.toml"

        if pyproject_toml.exists():
            print("pyproject.toml already exists. Not overwriting.")
            return

        with open(pyproject_toml, "w") as f:
            f.write("""[build-system]
requires = ["hatchling>=1.18.0"]
build-backend = "hatchling.build"

[project]
name = "your-package-name"
version = "0.1.0"
description = "Your project description"
authors = [
    { name = "Your Name", email = "your.email@example.com" },
]
readme = "README.md"
requires-python = ">=3.11"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
]
dependencies = [
    "pydantic>=2.6.1",
]

[project.optional-dependencies]
dev = [
    "pre-commit>=3.6.0",
    "ruff>=0.3.0",
    "pytest>=7.4.4",
    "pytest-cov>=4.1.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"
""")
        print("Created basic pyproject.toml file")

    def update_all_packages(self) -> None:
        """Update all outdated packages."""
        # Get list of outdated packages
        cmd = [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"]
        exit_code, stdout, stderr = self.run_command(cmd)

        if exit_code != 0:
            print("Failed to get outdated packages list.")
            return

        try:
            import json

            outdated = json.loads(stdout)

            if not outdated:
                print("No outdated packages to update.")
                return

            for package in outdated:
                package_name = package["name"]
                print(f"Updating {package_name}...")
                self.run_action_command(
                    [sys.executable, "-m", "pip", "install", "--upgrade", package_name]
                )

            print("All packages updated successfully.")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing outdated packages: {e}")

    def setup_nexus_env_vars(self) -> None:
        """Set up environment variables for Nexus."""
        print("\nSetting up Nexus environment variables...")
        print(
            "These will be set for this session only. For permanent setup, add them to your shell profile."
        )

        nexus_url = input(
            "Enter Nexus repository URL (e.g., https://nexus.example.com/repository/pypi-internal/simple): "
        )
        nexus_username = input("Enter Nexus username (press Enter to skip): ")
        nexus_password = input("Enter Nexus password (press Enter to skip): ")

        if nexus_url:
            os.environ["NEXUS_REPOSITORY_URL"] = nexus_url
            print("Set NEXUS_REPOSITORY_URL environment variable")

        if nexus_username:
            os.environ["NEXUS_USERNAME"] = nexus_username
            print("Set NEXUS_USERNAME environment variable")

        if nexus_password:
            os.environ["NEXUS_PASSWORD"] = nexus_password
            print("Set NEXUS_PASSWORD environment variable")

        print("\nEnvironment variables have been set for this session.")
        print("To make them permanent, add them to your shell profile (~/.bashrc, ~/.zshrc, etc.)")

    def check_nexus_requirements(self) -> None:
        """Check if all required packages for Nexus support are installed."""
        required_packages = ["requests", "tomli", "tomli-w"]
        missing_packages = []

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            print(f"Missing required packages for Nexus support: {', '.join(missing_packages)}")

            install = input("Do you want to install them now? (y/n): ")
            if install.lower() == "y":
                self.run_action_command([sys.executable, "-m", "pip", "install"] + missing_packages)
        else:
            print("All required packages for Nexus support are installed.")

    def show_nexus_config(self) -> None:
        """Show the current Nexus configuration."""
        sys.path.insert(0, str(self.project_root / "src"))

        try:
            from enterprise_data_engineering.common_utils import nexus_utils as nexus

            client = nexus.NexusClient()

            print("\nCurrent Nexus Configuration:")
            print(f"Repository URL: {client.repository_url or 'Not set'}")
            print(f"Username: {client.username or 'Not set'}")
            print(f"Password: {'*****' if client.password else 'Not set'}")
            print(f"Verify SSL: {client.verify_ssl}")
            print("\nConfiguration Source:")
            print(f"Config from pyproject.toml: {bool(client.config)}")
            print("\nEnvironment Variables:")
            print(f"NEXUS_REPOSITORY_URL: {os.environ.get('NEXUS_REPOSITORY_URL', 'Not set')}")
            print(f"NEXUS_USERNAME: {os.environ.get('NEXUS_USERNAME', 'Not set')}")
            print(f"NEXUS_PASSWORD: {'*****' if 'NEXUS_PASSWORD' in os.environ else 'Not set'}")

        except ImportError:
            print(
                "Could not import Nexus client. Make sure the nexus module is installed correctly."
            )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Project Health Dashboard")
    parser.add_argument(
        "--check",
        choices=["coverage", "linting", "hooks", "docs", "deps", "nexus", "all"],
        default="all",
        help="Specific health check to run",
    )
    parser.add_argument(
        "--ci", action="store_true", help="Run in CI mode (exit with non-zero code on failures)"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Run in interactive mode with action execution"
    )
    parser.add_argument(
        "--output",
        choices=["text", "rich"],
        default="rich" if RICH_AVAILABLE else "text",
        help="Output format (rich requires the 'rich' package)",
    )

    return parser.parse_args()


def main():
    """Run the project health dashboard."""
    args = parse_args()
    dashboard = ProjectHealthDashboard()

    if args.interactive:
        dashboard.run_all_checks()
        dashboard.run_interactive_mode()
        return

    if args.check == "all":
        dashboard.run_all_checks()
        dashboard.display_dashboard()
    elif args.check == "coverage":
        metric = dashboard.check_test_coverage()
        print(f"{metric.emoji} {metric.name}: {metric.status}")
        print(f"   {metric.details}")
    elif args.check == "linting":
        metric = dashboard.check_linting()
        print(f"{metric.emoji} {metric.name}: {metric.status}")
        print(f"   {metric.details}")
    elif args.check == "hooks":
        metric = dashboard.check_pre_commit_hooks()
        print(f"{metric.emoji} {metric.name}: {metric.status}")
        print(f"   {metric.details}")
    elif args.check == "docs":
        metric = dashboard.check_documentation()
        print(f"{metric.emoji} {metric.name}: {metric.status}")
        print(f"   {metric.details}")
    elif args.check == "deps":
        metric = dashboard.check_dependencies()
        print(f"{metric.emoji} {metric.name}: {metric.status}")
        print(f"   {metric.details}")
    elif args.check == "nexus":
        metric = dashboard.check_nexus_connection()
        print(f"{metric.emoji} {metric.name}: {metric.status}")
        print(f"   {metric.details}")

    # In CI mode, exit with non-zero code if any checks fail
    if args.ci and not dashboard.get_overall_status():
        sys.exit(1)


if __name__ == "__main__":
    main()
