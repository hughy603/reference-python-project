#!/usr/bin/env python3
"""
Interactive Project Initialization Wizard

A modern, user-friendly interface for initializing new projects from the template.
This script provides an enhanced visual experience with rich text formatting,
interactive prompts, progress tracking, and live documentation.

Features:
- Colorful, formatted terminal UI with collapsible sections
- Interactive component selection with dependency resolution
- Live validation and documentation
- Visual progress tracking
- Project preview generation

Usage:
    python scripts/interactive_wizard.py  # Run the interactive wizard

Note: This wizard uses the existing template processing system but provides
an enhanced user interface. The final configuration is passed to the
init_project.py script for actual project initialization.
"""

import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Add the parent directory to the path to import template utils
sys.path.append(str(Path(__file__).resolve().parent))

# Import utility functions from the existing system
try:
    from template_processor import TemplateProcessor
    from template_utils import (
        print_error,
        print_status,
        print_warning,
        slugify,
        snake_case,
    )
except ImportError as e:
    print(f"Error: Could not import template utilities: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

# Try to import rich for enhanced UI
try:
    from rich import box
    from rich.console import Console
    from rich.live import Live
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
    from rich.prompt import Confirm, Prompt
    from rich.syntax import Syntax
    from rich.table import Table

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' package not available. Using basic console output.")
    print("For an enhanced experience, install rich: pip install rich")

# Try to import yaml for parsing manifest
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("Error: PyYAML is required for the wizard.")
    print("Please install it: pip install pyyaml")
    sys.exit(1)

# Detect platform
PLATFORM = platform.system()
IS_WINDOWS = PLATFORM == "Windows"
IS_WSL = "microsoft-standard" in platform.release().lower() if not IS_WINDOWS else False
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Create rich console for enhanced output
console = Console() if RICH_AVAILABLE else None


# Fallback print functions if rich is not available
def print_rich_panel(title: str, content: str, style: str = "green") -> None:
    """Print a rich panel or fallback to simple text."""
    if RICH_AVAILABLE and console:
        console.print(Panel(content, title=title, style=style))
    else:
        print(f"\n--- {title} ---")
        print(content)
        print("-" * (len(title) + 8))


def print_rich_markdown(content: str) -> None:
    """Print rich markdown or fallback to simple text."""
    if RICH_AVAILABLE and console:
        console.print(Markdown(content))
    else:
        print(content)


def create_component_table(
    components: list[dict[str, Any]], selected: dict[str, bool]
) -> Table | str:
    """Create a table of available components."""
    if RICH_AVAILABLE:
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
        table.add_column("Include")
        table.add_column("Component")
        table.add_column("Description")
        table.add_column("Dependencies")

        for component in components:
            name = component.get("name", "unknown")
            if name == "core":
                continue  # Skip core component as it's always included

            is_selected = "✓" if selected.get(name, False) else " "
            dependencies = ", ".join(component.get("dependencies", []))
            if not dependencies:
                dependencies = "None"

            table.add_row(
                f"[green]{is_selected}[/green]" if is_selected.strip() else is_selected,
                name,
                component.get("description", ""),
                dependencies,
            )
        return table
    else:
        # Fallback simple text table
        result = "Components:\n"
        for component in components:
            name = component.get("name", "unknown")
            if name == "core":
                continue
            is_selected = "[x]" if selected.get(name, False) else "[ ]"
            result += f"{is_selected} {name} - {component.get('description', '')}\n"
        return result


def create_config_summary(config: dict[str, Any]) -> Panel | str:
    """Create a summary of the configuration."""
    if not RICH_AVAILABLE:
        # Fallback simple text summary
        result = "Configuration Summary:\n"
        result += f"- Project name: {config.get('project_name', '')}\n"
        result += f"- Package name: {config.get('package_name', '')}\n"
        result += f"- Description: {config.get('description', '')}\n"
        result += f"- Author: {config.get('author', '')}\n"
        result += f"- Email: {config.get('email', '')}\n"
        result += f"- Organization: {config.get('organization', '')}\n"
        result += f"- Version: {config.get('version', '')}\n"
        result += "- Components:\n"

        for name, enabled in config.get("components", {}).items():
            if enabled:
                result += f"  - {name}\n"
        return result

    # Rich text summary
    table = Table(box=box.SIMPLE)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Project name", config.get("project_name", ""))
    table.add_row("Package name", config.get("package_name", ""))
    table.add_row("Description", config.get("description", ""))
    table.add_row("Author", config.get("author", ""))
    table.add_row("Email", config.get("email", ""))
    table.add_row("Organization", config.get("organization", ""))
    table.add_row("Version", config.get("version", ""))

    # Add component list
    component_list = ""
    for name, enabled in config.get("components", {}).items():
        if enabled:
            component_list += f"• [green]{name}[/green]\n"

    if component_list:
        table.add_row("Components", component_list)
    else:
        table.add_row("Components", "[yellow]None selected[/yellow]")

    return Panel(table, title="Configuration Summary", border_style="green")


def load_manifest() -> dict[str, Any]:
    """Load the template manifest."""
    manifest_path = PROJECT_ROOT / "template_manifest.yml"

    if not manifest_path.exists():
        print_error(f"Template manifest not found at {manifest_path}")
        sys.exit(1)

    try:
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
        return manifest
    except Exception as e:
        print_error(f"Error loading manifest: {e}")
        sys.exit(1)


def welcome_screen() -> None:
    """Display welcome screen with project information."""
    if RICH_AVAILABLE and console:
        console.clear()
        console.print("[bold cyan]Project Initialization Wizard[/bold cyan]", justify="center")
        console.print("[cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/cyan]", justify="center")

        manifest = load_manifest()
        template_info = manifest.get("template", {})

        console.print(
            f"\n[yellow]✨ {template_info.get('name', 'Template')} v{template_info.get('version', '1.0.0')}[/yellow]"
        )
        console.print(f"[dim]{template_info.get('description', '')}[/dim]\n")

        console.print(
            Panel(
                "[bold green]This wizard will guide you through creating a new project based on the template.[/bold green]\n\n"
                "You'll be able to customize:\n"
                "• Project metadata (name, description, etc.)\n"
                "• Components to include\n"
                "• Advanced configuration options\n\n"
                "[dim]Press Ctrl+C at any time to cancel.[/dim]",
                title="Welcome",
                border_style="blue",
                expand=False,
            )
        )
    else:
        print("\n=== Project Initialization Wizard ===\n")
        manifest = load_manifest()
        template_info = manifest.get("template", {})
        print(f"{template_info.get('name', 'Template')} v{template_info.get('version', '1.0.0')}")
        print(f"{template_info.get('description', '')}\n")
        print("This wizard will guide you through creating a new project based on the template.")
        print(
            "You'll be able to customize project metadata, components to include, and configuration options."
        )
        print("\nPress Ctrl+C at any time to cancel.")


def prompt_for_metadata() -> dict[str, Any]:
    """Prompt user for project metadata."""
    print_rich_panel(
        "Project Metadata", "Please provide basic information about your project.", style="blue"
    )

    metadata = {}

    if RICH_AVAILABLE:
        metadata["project_name"] = Prompt.ask(
            "Project name", default="my-project", help="The name of your project (kebab-case)"
        )

        default_package = snake_case(metadata["project_name"])
        metadata["package_name"] = Prompt.ask(
            "Package name", default=default_package, help="The Python package name (snake_case)"
        )

        metadata["description"] = Prompt.ask(
            "Description",
            default="A Python project built with the enterprise template",
            help="A short description of your project",
        )

        metadata["author"] = Prompt.ask(
            "Author", default=os.environ.get("USER", ""), help="Your name"
        )

        metadata["email"] = Prompt.ask("Email", default="", help="Your email address")

        metadata["organization"] = Prompt.ask(
            "Organization", default="", help="Your organization name (optional)"
        )

        metadata["version"] = Prompt.ask(
            "Version", default="0.1.0", help="Initial version number (semver)"
        )
    else:
        # Fallback to basic prompts
        metadata["project_name"] = input("Project name [my-project]: ") or "my-project"
        default_package = snake_case(metadata["project_name"])
        metadata["package_name"] = input(f"Package name [{default_package}]: ") or default_package
        metadata["description"] = input("Description [A Python project]: ") or "A Python project"
        metadata["author"] = input(f"Author [{os.environ.get('USER', '')}]: ") or os.environ.get(
            "USER", ""
        )
        metadata["email"] = input("Email: ") or ""
        metadata["organization"] = input("Organization: ") or ""
        metadata["version"] = input("Version [0.1.0]: ") or "0.1.0"

    return metadata


def prompt_for_components(manifest: dict[str, Any]) -> dict[str, bool]:
    """Prompt user for component selection."""
    print_rich_panel(
        "Component Selection", "Select which components to include in your project.", style="blue"
    )

    # Get available components from manifest
    components = manifest.get("components", [])

    # Initialize all components to False
    selected = {}
    for component in components:
        name = component.get("name", "")
        if name:
            # Set required components to True and make them non-interactive
            selected[name] = component.get("required", False)

    if RICH_AVAILABLE and console:
        # Create an initial component table
        table = create_component_table(components, selected)

        # Interactive component selection with live update
        with Live(table, refresh_per_second=4, console=console) as live:
            for component in components:
                name = component.get("name", "")
                if name == "core" or not name:
                    continue  # Skip core component

                is_required = component.get("required", False)
                if is_required:
                    continue  # Skip required components

                # Get default value - True for common components
                default = name in ["documentation", "testing", "ci_cd"]

                # Ask for confirmation
                result = Confirm.ask(
                    f"Include {name}?", default=default, help=component.get("description", "")
                )

                # Update selection
                selected[name] = result

                # Update the live table
                live.update(create_component_table(components, selected))
    else:
        # Fallback to basic prompts
        for component in components:
            name = component.get("name", "")
            if name == "core" or not name:
                continue  # Skip core component

            is_required = component.get("required", False)
            if is_required:
                continue  # Skip required components

            # Get default value - True for common components
            default = name in ["documentation", "testing", "ci_cd"]
            default_str = "Y/n" if default else "y/N"

            # Ask for confirmation
            prompt_text = f"Include {name}? ({component.get('description', '')}) [{default_str}]: "
            result = input(prompt_text).strip().lower()

            if not result:
                selected[name] = default
            else:
                selected[name] = result.startswith("y")

    # Resolve dependencies
    has_changes = True
    while has_changes:
        has_changes = False
        for component in components:
            name = component.get("name", "")
            if not name or not selected.get(name, False):
                continue

            # Check dependencies
            dependencies = component.get("dependencies", [])
            for dep in dependencies:
                if not selected.get(dep, False):
                    # Enable dependency
                    selected[dep] = True
                    has_changes = True

                    if RICH_AVAILABLE and console:
                        console.print(f"[yellow]Adding required dependency: {dep}[/yellow]")
                    else:
                        print(f"Adding required dependency: {dep}")

    return selected


def initialize_project(config: dict[str, Any]) -> bool:
    """Initialize the project with the given configuration."""
    init_script = PROJECT_ROOT / "scripts" / "init_project.py"

    if not init_script.exists():
        print_error(f"Initialization script not found at {init_script}")
        return False

    # Create a temporary config file
    config_path = PROJECT_ROOT / ".temp_init_config.yml"
    try:
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

        # Build the command
        cmd = [sys.executable, str(init_script), "--config", str(config_path)]

        if RICH_AVAILABLE and console:
            console.print("\n[bold blue]Initializing project...[/bold blue]")

            # Use rich progress display
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("[bold green]{task.fields[status]}"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Processing...", total=100, status="Starting")

                # Update progress at intervals
                progress.update(task, advance=10, status="Loading configuration")

                # Start the process
                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                # Update progress while waiting for completion
                stages = [
                    "Loading configuration",
                    "Processing components",
                    "Creating project structure",
                    "Updating metadata",
                    "Configuring environment",
                    "Finalizing setup",
                ]

                stage_idx = 0
                while process.poll() is None and stage_idx < len(stages):
                    time.sleep(0.5)
                    progress.update(task, advance=5, status=stages[stage_idx])
                    stage_idx = (stage_idx + 1) % len(stages)

                # Complete the progress bar
                progress.update(task, completed=100, status="Complete")

                # Get output
                stdout, stderr = process.communicate()

                # Check if successful
                if process.returncode != 0:
                    console.print("[bold red]Error initializing project:[/bold red]")
                    console.print(stderr)
                    return False

                return True
        else:
            # Fallback to simple execution
            print("\nInitializing project...")
            result = subprocess.run(cmd, check=False)
            return result.returncode == 0

    except Exception as e:
        print_error(f"Error initializing project: {e}")
        return False
    finally:
        # Clean up temporary config file
        if config_path.exists():
            config_path.unlink()

    return True


def main() -> None:
    """Main function to run the interactive wizard."""
    try:
        # Display welcome screen
        welcome_screen()

        # Load manifest
        manifest = load_manifest()

        # Prompt for project metadata
        metadata = prompt_for_metadata()

        # Prompt for component selection
        selected_components = prompt_for_components(manifest)

        # Combine configuration
        config = {**metadata, "components": selected_components}

        # Display configuration summary
        summary = create_config_summary(config)
        if RICH_AVAILABLE and console:
            console.print("\n")
            console.print(summary)
        else:
            print("\nConfiguration Summary:")
            print(summary)

        # Confirm initialization
        proceed = (
            Confirm.ask("\nProceed with initialization?", default=True)
            if RICH_AVAILABLE
            else input("\nProceed with initialization? [Y/n]: ").strip().lower() != "n"
        )

        if not proceed:
            if RICH_AVAILABLE and console:
                console.print("[yellow]Initialization cancelled.[/yellow]")
            else:
                print("Initialization cancelled.")
            return

        # Initialize the project
        if initialize_project(config):
            if RICH_AVAILABLE and console:
                console.print("\n[bold green]✓ Project successfully initialized![/bold green]")
            else:
                print("\n✓ Project successfully initialized!")
        elif RICH_AVAILABLE and console:
            console.print("\n[bold red]✗ Project initialization failed.[/bold red]")
        else:
            print("\n✗ Project initialization failed.")

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        if RICH_AVAILABLE and console:
            console.print("\n[yellow]Initialization cancelled by user.[/yellow]")
        else:
            print("\nInitialization cancelled by user.")
    except Exception as e:
        if RICH_AVAILABLE and console:
            console.print(f"\n[bold red]Error: {e}[/bold red]")
        else:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
