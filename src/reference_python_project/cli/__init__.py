"""
Command-line interface package for reference-python-project.

This package provides Autosys integration and automation commands.
"""

from reference_python_project.cli.automation import app as automation_app
from reference_python_project.cli.main import app

__all__ = ["app", "automation_app"]
