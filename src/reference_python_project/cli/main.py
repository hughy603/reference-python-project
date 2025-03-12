"""
Main CLI entry point for reference-python-project.

This module serves as the primary CLI interface, integrating all subcommands
including the automation features for Autosys integration.
"""

import os
import sys

import typer

from reference_python_project.cli import automation
from reference_python_project.utils.logging import configure_logging

# Create the main Typer app
app = typer.Typer(
    name="rpp",
    help="Reference Python Project CLI",
    add_completion=True,
)

# Add the automation commands as a subcommand group
app.add_typer(automation.app, name="automation")


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    log_file: str | None = typer.Option(None, "--log-file", help="Log file path"),
    log_format: str = typer.Option("text", "--log-format", help="Log format (text or json)"),
) -> None:
    """
    Reference Python Project CLI with support for automation systems like Autosys.

    This CLI provides commands for various project operations, with special
    attention to automation capabilities that integrate with job scheduling systems.
    """
    # Configure logging based on command line options
    log_level = "DEBUG" if verbose else "INFO"
    numeric_level = getattr(sys.modules["logging"], log_level, 20)

    configure_logging(
        level=numeric_level,
        json_format=log_format == "json",
        log_file=log_file,
    )


@app.command()
def version() -> None:
    """Display the version of the package."""
    try:
        # Try to get version from package metadata
        from importlib.metadata import version as pkg_version

        version_str = pkg_version("reference-python-project")
    except ImportError:
        # Fallback for older Python versions
        version_str = "Unknown (requires Python 3.11+ for version detection)"

    typer.echo(f"Reference Python Project v{version_str}")


@app.command()
def setup() -> None:
    """
    Set up the project environment.

    This includes configuring environment variables needed for Autosys integration.
    """
    # Check if we're running in an Autosys environment
    autosys_job_id = os.environ.get("AUTOSYS_JOB_ID")
    if autosys_job_id:
        typer.echo(f"Detected Autosys environment with job ID: {autosys_job_id}")
    else:
        typer.echo("No Autosys environment detected")

    # Demo setup process
    typer.echo("Setting up project environment...")

    # Create default status directory if it doesn't exist
    status_dir = os.environ.get("AUTOSYS_STATUS_DIR", os.path.expanduser("~/.rpp/status"))
    if not os.path.exists(status_dir):
        try:
            os.makedirs(status_dir, exist_ok=True)
            typer.echo(f"Created status directory: {status_dir}")
        except OSError as e:
            typer.echo(f"Error creating status directory: {e}", err=True)

    # Create example environment file
    env_file = os.path.join(os.getcwd(), ".env.example")
    with open(env_file, "w") as f:
        f.write("# Example environment file for Autosys integration\n")
        f.write("AUTOSYS_JOB_ID=example_job_001\n")
        f.write("AUTOSYS_EXECUTION_ID=exec_001\n")
        f.write(f"AUTOSYS_STATUS_FILE={os.path.join(status_dir, 'example_job_001.json')}\n")
        f.write("AUTOSYS_LOG_FILE=/path/to/logs/example_job_001.log\n")
        f.write("AUTOSYS_LOG_LEVEL=INFO\n")

    typer.echo(f"Created example environment file: {env_file}")
    typer.echo("Setup complete! Use 'rpp automation run-job' to test Autosys integration.")


if __name__ == "__main__":
    app()
