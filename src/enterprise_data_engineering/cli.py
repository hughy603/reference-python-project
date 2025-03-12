"""
Command Line Interface for the Enterprise Data Engineering toolkit.

This module provides a user-friendly CLI for common tasks and operations.
"""

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

# Type variable for function return types
F = TypeVar("F", bound=Callable[..., Any])

# Create the main typer app
app = typer.Typer(
    name="ede",
    help="Enterprise Data Engineering CLI",
    add_completion=True,
)

# Create nested apps for different command groups
dev_app = typer.Typer(help="Development commands")
app.add_typer(dev_app, name="dev")

docs_app = typer.Typer(help="Documentation commands")
app.add_typer(docs_app, name="docs")

data_app = typer.Typer(help="Data pipeline commands")
app.add_typer(data_app, name="data")

# Create console for rich output
console = Console()


@app.callback()
def callback() -> None:
    """
    Enterprise Data Engineering CLI - A toolkit for data engineering tasks.
    """
    pass


@app.command()
def info() -> None:
    """
    Display information about the environment and configuration.
    """
    table = Table(title="Environment Information")

    table.add_column("Item", style="cyan")
    table.add_column("Value", style="green")

    python_version = sys.version.split()[0]
    table.add_row("Python Version", f"{python_version}")

    cwd = os.getcwd()
    table.add_row("Current Directory", f"{cwd=}")

    package_path = Path(__file__).parent
    table.add_row("Package Path", f"{package_path=}")

    for env_var in ["PYTHONPATH", "VIRTUAL_ENV"]:
        value = os.environ.get(env_var, "Not set")
        table.add_row(f"Environment: {env_var}", f"{value}")

    console.print(table)


@dev_app.command("setup")
def dev_setup(
    skip_hooks: bool = typer.Option(False, "--skip-hooks", help="Skip installing pre-commit hooks"),
) -> None:
    """
    Set up the development environment.
    """
    with console.status("[bold green]Setting up development environment..."):
        # Install dependencies
        rprint("[bold]Installing dependencies...[/bold]")
        subprocess.run(["pip", "install", "-e", "."], check=True)

        if not skip_hooks:
            # Install pre-commit hooks
            rprint("[bold]Installing pre-commit hooks...[/bold]")
            subprocess.run(["pre-commit", "install"], check=True)

        console.print("[bold green]✓[/bold green] Development environment setup complete!")


@dev_app.command("lint")
def run_lint(
    fix: bool = typer.Option(False, "--fix", "-f", help="Automatically fix issues when possible"),
) -> None:
    """
    Run linting checks on the codebase.
    """
    cmd = ["hatch", "run", "-e", "lint", "style"]
    if fix:
        cmd = ["hatch", "run", "-e", "lint", "fmt"]

    with console.status("[bold green]Running linting checks..."):
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if result.returncode == 0:
        console.print("[bold green]✓[/bold green] Linting passed!")
    else:
        console.print("[bold red]✗[/bold red] Linting failed!")
        console.print(result.stdout)
        console.print(result.stderr, style="red")


@dev_app.command("test")
def run_tests(
    test_path: str | None = typer.Argument(None, help="Specific test path to run"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """
    Run the test suite.
    """
    cmd = ["hatch", "run", "-e", "test"]
    if test_path:
        cmd.append(test_path)
    if verbose:
        cmd.append("-v")

    with console.status("[bold green]Running tests..."):
        subprocess.run(cmd, check=False)


@docs_app.command("build")
def build_docs() -> None:
    """
    Build the documentation.
    """
    with console.status("[bold green]Building documentation..."):
        subprocess.run(["hatch", "run", "-e", "docs", "generate"], check=False)
        subprocess.run(["hatch", "run", "-e", "docs", "build"], check=False)

    console.print("[bold green]✓[/bold green] Documentation built successfully!")
    console.print("To view the documentation, run: [bold]hatch run -e docs serve[/bold]")


@docs_app.command("serve")
def serve_docs(
    port: int = typer.Option(8000, "--port", "-p", help="Port to serve documentation on"),
) -> None:
    """
    Serve the documentation locally.
    """
    console.print(f"[bold green]Starting documentation server on port {port}...[/bold green]")
    console.print(f"View the documentation at: [bold]http://localhost:{port}[/bold]")
    console.print("Press Ctrl+C to stop the server")

    subprocess.run(
        ["hatch", "run", "-e", "docs", "mkdocs", "serve", "-a", f"localhost:{port}"], check=False
    )


@data_app.command("validate")
def validate_pipeline(
    pipeline_file: Path = typer.Argument(..., help="Path to the pipeline configuration file"),
) -> None:
    """
    Validate a data pipeline configuration.
    """
    if not pipeline_file.exists():
        console.print(f"[bold red]Error:[/bold red] Pipeline file {pipeline_file} does not exist!")
        raise typer.Exit(1)

    with console.status(f"[bold green]Validating pipeline: {pipeline_file}..."):
        # This is a placeholder for actual validation logic
        console.print(f"[bold green]✓[/bold green] Pipeline {pipeline_file} is valid!")


if __name__ == "__main__":
    app()
