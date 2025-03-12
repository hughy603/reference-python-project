"""
Main entry point for the Enterprise Data Engineering package.

This module allows running the package directly with:
python -m enterprise_data_engineering
"""

from enterprise_data_engineering.cli import app


def main() -> None:
    """Execute the CLI application."""
    app()


if __name__ == "__main__":
    main()
