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

from enterprise_data_engineering.cli import data

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

# Add the data commands from the data module
app.add_typer(data.app, name="data")

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

    table.add_row("Python Version", sys.version.split()[0])
    table.add_row("Working Directory", os.getcwd())
    table.add_row("Package Location", str(Path(__file__).parent.parent.absolute()))

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


if __name__ == "__main__":
    app()
