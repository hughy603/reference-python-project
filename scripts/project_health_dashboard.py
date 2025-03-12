#!/usr/bin/env python
"""
Project Health Dashboard

A simple utility to display the health status of the project, including
test coverage, linting status, and documentation completeness.
"""

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class HealthMetric:
    """A health metric for the project."""

    name: str
    status: str
    details: str
    emoji: str
    success: bool


class ProjectHealthDashboard:
    """Displays the health status of the project."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the dashboard with the project root directory."""
        self.project_root = project_root or Path.cwd()
        self.metrics: list[HealthMetric] = []

    def run_command(self, command: list[str], cwd: Optional[Path] = None) -> tuple[int, str, str]:
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
            )

        # Parse coverage percentage
        try:
            coverage_parts = coverage_line.split()
            coverage_percent = float(coverage_parts[-1].rstrip("%"))

            # Determine status based on coverage threshold
            if coverage_percent >= 80:
                status = "PASS"
                emoji = "✅"
                success = True
            elif coverage_percent >= 60:
                status = "WARN"
                emoji = "⚠️"
                success = True
            else:
                status = "FAIL"
                emoji = "❌"
                success = False

            return HealthMetric(
                name="Test Coverage",
                status=status,
                details=f"{coverage_percent:.1f}% coverage",
                emoji=emoji,
                success=success,
            )
        except (IndexError, ValueError):
            return HealthMetric(
                name="Test Coverage",
                status="WARN",
                details="Could not parse coverage percentage.",
                emoji="⚠️",
                success=False,
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
            )
        else:
            issue_count = len(stdout.splitlines())
            return HealthMetric(
                name="Linting",
                status="FAIL",
                details=f"{issue_count} linting issues found.",
                emoji="❌",
                success=False,
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
            )

        if not git_hooks_dir.exists() or not pre_commit_hook.exists():
            return HealthMetric(
                name="Pre-commit Hooks",
                status="WARN",
                details="Pre-commit hooks not installed. Run 'pre-commit install'.",
                emoji="⚠️",
                success=False,
            )

        return HealthMetric(
            name="Pre-commit Hooks",
            status="PASS",
            details="Pre-commit hooks are installed.",
            emoji="✅",
            success=True,
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
            )
        else:
            return HealthMetric(
                name="Documentation",
                status="FAIL",
                details="Documentation build failed.",
                emoji="❌",
                success=False,
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
            )
        else:
            return HealthMetric(
                name="Dependencies",
                status="WARN",
                details=f"{num_outdated} outdated dependencies found.",
                emoji="⚠️",
                success=True,  # Still a success but with warning
            )

    def run_all_checks(self) -> list[HealthMetric]:
        """Run all health checks and return the results."""
        self.metrics = [
            self.check_test_coverage(),
            self.check_linting(),
            self.check_pre_commit_hooks(),
            self.check_documentation(),
            self.check_dependencies(),
        ]
        return self.metrics

    def display_dashboard(self) -> None:
        """Display the health dashboard in the terminal."""
        if not self.metrics:
            self.run_all_checks()

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
            print("-" * 60)

        # Overall status
        all_success = all(metric.success for metric in self.metrics)
        if all_success:
            print(f"\n✅ Overall Status: \033[92mHEALTHY{reset_color}")
        else:
            print(f"\n⚠️ Overall Status: \033[91mNEEDS ATTENTION{reset_color}")

        print("=" * 60)
        print("Run 'python scripts/project_health_dashboard.py --help' for more options.\n")

    def get_overall_status(self) -> bool:
        """Get the overall project health status."""
        if not self.metrics:
            self.run_all_checks()
        return all(metric.success for metric in self.metrics)


def parse_args():
    """Parse command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(description="Project Health Dashboard")
    parser.add_argument(
        "--check",
        choices=["coverage", "linting", "hooks", "docs", "deps", "all"],
        default="all",
        help="Specific health check to run",
    )
    parser.add_argument(
        "--ci", action="store_true", help="Run in CI mode (exit with non-zero code on failures)"
    )

    return parser.parse_args()


def main():
    """Run the project health dashboard."""
    args = parse_args()
    dashboard = ProjectHealthDashboard()

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

    # In CI mode, exit with non-zero code if any checks fail
    if args.ci and not dashboard.get_overall_status():
        sys.exit(1)


if __name__ == "__main__":
    main()
