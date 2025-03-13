#!/usr/bin/env python3
"""
Template Utilities for Python & Terraform Project Template

This module provides utility functions for working with the template,
including file operations, configuration management, and environment setup.
"""

import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

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


def slugify(text: str) -> str:
    """
    Convert text to a slug format (lowercase, hyphens).

    Args:
        text: Text to convert

    Returns:
        Slugified text

    Example:
        >>> slugify("Hello World")
        "hello-world"
    """
    # Convert to lowercase
    text = text.lower()
    # Replace non-alphanumeric characters with hyphens
    text = re.sub(r"[^a-z0-9]+", "-", text)
    # Remove leading/trailing hyphens
    text = text.strip("-")
    return text


def snake_case(text: str) -> str:
    """
    Convert text to snake_case format (lowercase, underscores).

    Args:
        text: Text to convert

    Returns:
        snake_case text

    Example:
        >>> snake_case("Hello World")
        "hello_world"
    """
    # Convert to lowercase
    text = text.lower()
    # Replace non-alphanumeric characters with underscores
    text = re.sub(r"[^a-z0-9]+", "_", text)
    # Remove leading/trailing underscores
    text = text.strip("_")
    return text


def kebab_case(text: str) -> str:
    """Convert text to kebab-case."""
    # Replace non-alphanumeric characters with hyphens
    s1 = re.sub(r"[^a-zA-Z0-9]", "-", text.strip().lower())
    # Replace consecutive hyphens with a single hyphen
    s2 = re.sub(r"-+", "-", s1)
    # Remove leading/trailing hyphens
    return s2.strip("-")


def title_case(text: str) -> str:
    """Convert snake_case or kebab-case to Title Case."""
    # Replace underscores and hyphens with spaces
    s1 = re.sub(r"[_-]", " ", text)
    # Capitalize each word
    return " ".join(word.capitalize() for word in s1.split())


def camel_case(text: str) -> str:
    """Convert text to camelCase."""
    # First convert to snake_case
    s1 = snake_case(text)
    # Then convert to camelCase
    words = s1.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])


def prompt_for_value(prompt: str, default: str | None = None) -> str:
    """
    Prompt the user for a value with optional default.

    Args:
        prompt: Prompt to display
        default: Default value if user enters nothing

    Returns:
        User input or default value
    """
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "

    try:
        value = input(full_prompt)
        if not value and default:
            return default
        return value
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled by user")
        sys.exit(1)


def substitute_variables(directory: Path, config: dict[str, Any], verbose: bool = False) -> None:
    """
    Substitute template variables in files.

    Args:
        directory: Root directory to search for files
        config: Configuration with variable values
        verbose: Whether to print verbose output
    """
    # Define patterns to search for
    patterns = {
        "jinja": r"{{\s*([A-Z_]+)\s*}}",  # {{ VARIABLE_NAME }}
        "placeholder": r"___([A-Z_]+)___",  # ___VARIABLE_NAME___
    }

    # Create a mapping of variable names to values
    var_map = {
        "PROJECT_NAME": config.get("project_name", ""),
        "PACKAGE_NAME": config.get("package_name", ""),
        "DESCRIPTION": config.get("description", ""),
        "VERSION": config.get("version", "0.1.0"),
        "AUTHOR": config.get("author", ""),
        "AUTHOR_EMAIL": config.get("email", ""),
        "ORGANIZATION": config.get("organization", ""),
    }

    # Files to process
    text_file_extensions = [
        ".py",
        ".md",
        ".rst",
        ".yml",
        ".yaml",
        ".json",
        ".toml",
        ".ini",
        ".cfg",
        ".txt",
        ".html",
        ".css",
        ".js",
        ".sh",
        ".bat",
        ".ps1",
        ".dockerfile",
        ".tf",
        ".hcl",
    ]

    # Find all text files in the directory
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = Path(root) / filename

            # Skip non-text files
            if not any(filepath.name.endswith(ext) for ext in text_file_extensions):
                continue

            # Skip virtual environment directories
            if ".venv" in filepath.parts or "venv" in filepath.parts:
                continue

            # Skip .git directory
            if ".git" in filepath.parts:
                continue

            try:
                # Read file content
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()

                modified = False

                # Replace variables using both patterns
                for pattern_type, pattern in patterns.items():
                    matches = re.findall(pattern, content)

                    for var_name in matches:
                        if var_map.get(var_name):
                            if pattern_type == "jinja":
                                content = re.sub(
                                    r"{{\s*" + var_name + r"\s*}}", str(var_map[var_name]), content
                                )
                            else:  # placeholder
                                content = re.sub(
                                    r"___" + var_name + r"___", str(var_map[var_name]), content
                                )
                            modified = True

                # Write back if modified
                if modified:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)

                    if verbose:
                        print(f"Updated variables in {filepath}")

            except Exception as e:
                if verbose:
                    print(f"Error processing {filepath}: {e}")
                continue


def setup_venv(project_root: Path, verbose: bool = False) -> Path:
    """
    Set up a virtual environment for the project.

    Args:
        project_root: Root directory of the project
        verbose: Whether to print verbose output

    Returns:
        Path to the virtual environment
    """
    venv_dir = project_root / ".venv"

    # Create virtual environment
    if verbose:
        print(f"Creating virtual environment in {venv_dir}")

    try:
        # Check platform for correct activation command
        if sys.platform == "win32":
            # Windows
            venv_cmd = [sys.executable, "-m", "venv", str(venv_dir)]
            pip_cmd = [str(venv_dir / "Scripts" / "pip")]
            activate_script = str(venv_dir / "Scripts" / "activate")
        else:
            # Unix-like (Linux, macOS)
            venv_cmd = [sys.executable, "-m", "venv", str(venv_dir)]
            pip_cmd = [str(venv_dir / "bin" / "pip")]
            activate_script = str(venv_dir / "bin" / "activate")

        # Create virtual environment
        subprocess.run(venv_cmd, check=True, stdout=subprocess.PIPE if not verbose else None)

        # Upgrade pip
        subprocess.run(
            pip_cmd + ["install", "--upgrade", "pip"],
            check=True,
            stdout=subprocess.PIPE if not verbose else None,
        )

        # Install the project in development mode
        subprocess.run(
            pip_cmd + ["install", "-e", "."],
            check=True,
            cwd=project_root,
            stdout=subprocess.PIPE if not verbose else None,
        )

        if verbose:
            print(f"Virtual environment created at {venv_dir}")
            print(f"Activate with: source {activate_script}")

        return venv_dir

    except subprocess.CalledProcessError as e:
        print(f"Error setting up virtual environment: {e}")
        sys.exit(1)


def run_command(cmd: list[str], cwd: str | Path = None, capture_output: bool = False) -> str | None:
    """Run a command and return its output.

    Args:
        cmd: Command to run as a list
        cwd: Working directory
        capture_output: Whether to capture and return the output

    Returns:
        Command output if capture_output is True, otherwise None

    Raises:
        subprocess.CalledProcessError: If the command fails
    """
    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                check=True,
                cwd=cwd or PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            return result.stdout
        else:
            subprocess.run(
                cmd,
                check=True,
                cwd=cwd or PROJECT_ROOT,
            )
            return None
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(cmd)}")
        if e.stdout:
            print_error(f"Output: {e.stdout}")
        if e.stderr:
            print_error(f"Error: {e.stderr}")
        raise


def ensure_directory(path: str | Path) -> Path:
    """Ensure a directory exists.

    Args:
        path: Directory path

    Returns:
        Path object to the directory
    """
    path_obj = Path(path)
    if not path_obj.exists():
        path_obj.mkdir(parents=True)
    return path_obj


def remove_directory(path: str | Path) -> None:
    """Remove a directory and its contents.

    Args:
        path: Directory path
    """
    path_obj = Path(path)
    if path_obj.exists() and path_obj.is_dir():
        shutil.rmtree(path_obj)


def copy_directory(src: str | Path, dst: str | Path, ignore_patterns: list[str] = None) -> None:
    """Copy a directory and its contents.

    Args:
        src: Source directory
        dst: Destination directory
        ignore_patterns: Patterns to ignore
    """
    src_path = Path(src)
    dst_path = Path(dst)

    if not src_path.exists():
        raise FileNotFoundError(f"Source directory does not exist: {src}")

    # Create destination directory if it doesn't exist
    ensure_directory(dst_path)

    # Create ignore function if patterns are provided
    ignore_func = None
    if ignore_patterns:

        def ignore_func(directory, contents):
            ignored = []
            for pattern in ignore_patterns:
                for item in contents:
                    if re.search(pattern, item):
                        ignored.append(item)
            return ignored

    # Copy directory
    shutil.copytree(src_path, dst_path, dirs_exist_ok=True, ignore=ignore_func)


def find_files(path: str | Path, pattern: str) -> list[Path]:
    """Find files matching a pattern.

    Args:
        path: Directory to search
        pattern: Glob pattern to match

    Returns:
        List of matching file paths
    """
    path_obj = Path(path)
    return list(path_obj.glob(pattern))


def replace_in_file(file_path: str | Path, pattern: str, replacement: str) -> bool:
    """Replace text in a file.

    Args:
        file_path: File to modify
        pattern: Regular expression pattern to find
        replacement: Replacement text

    Returns:
        True if any replacements were made, False otherwise
    """
    path_obj = Path(file_path)
    if not path_obj.exists():
        return False

    content = path_obj.read_text()
    new_content = re.sub(pattern, replacement, content)

    if new_content != content:
        path_obj.write_text(new_content)
        return True

    return False


def create_virtual_environment(venv_path: str | Path = ".venv") -> bool:
    """Create a Python virtual environment.

    Args:
        venv_path: Path to create the virtual environment

    Returns:
        True if successful, False otherwise
    """
    venv_dir = Path(venv_path)
    if venv_dir.exists():
        print_info(f"Virtual environment already exists at {venv_dir}")
        return True

    try:
        run_command([sys.executable, "-m", "venv", str(venv_dir)])
        print_info(f"Created virtual environment at {venv_dir}")
        return True
    except Exception as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False


def install_package(package_name: str, venv_path: str | Path = ".venv") -> bool:
    """Install a package in a virtual environment.

    Args:
        package_name: Package to install
        venv_path: Path to the virtual environment

    Returns:
        True if successful, False otherwise
    """
    venv_dir = Path(venv_path)
    if not venv_dir.exists():
        print_error(f"Virtual environment does not exist at {venv_dir}")
        return False

    pip_path = venv_dir / ("Scripts" if IS_WINDOWS else "bin") / "pip"

    try:
        run_command([str(pip_path), "install", package_name])
        print_info(f"Installed {package_name}")
        return True
    except Exception as e:
        print_error(f"Failed to install {package_name}: {e}")
        return False


def install_project_in_dev_mode(venv_path: str | Path = ".venv") -> bool:
    """Install the project in development mode.

    Args:
        venv_path: Path to the virtual environment

    Returns:
        True if successful, False otherwise
    """
    venv_dir = Path(venv_path)
    if not venv_dir.exists():
        print_error(f"Virtual environment does not exist at {venv_dir}")
        return False

    pip_path = venv_dir / ("Scripts" if IS_WINDOWS else "bin") / "pip"

    try:
        run_command([str(pip_path), "install", "-e", "."])
        print_info("Installed project in development mode")
        return True
    except Exception as e:
        print_error(f"Failed to install project: {e}")
        return False


def setup_git_repository(initial_commit_message: str = "Initial commit") -> bool:
    """Initialize a Git repository and create an initial commit.

    Args:
        initial_commit_message: Message for the initial commit

    Returns:
        True if successful, False otherwise
    """
    git_dir = PROJECT_ROOT / ".git"

    # Remove existing Git repository if it exists
    if git_dir.exists():
        try:
            shutil.rmtree(git_dir)
            print_info("Removed existing Git repository")
        except Exception as e:
            print_warning(f"Error removing existing Git repository: {e}")
            return False

    try:
        # Initialize new repository
        run_command(["git", "init"])
        print_info("Initialized Git repository")

        # Create initial commit
        run_command(["git", "add", "."])
        run_command(["git", "commit", "-m", initial_commit_message])
        print_info("Created initial commit")

        return True
    except Exception as e:
        print_error(f"Error setting up Git repository: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    print_info("Template utilities module")
    print_status("Available for import, not for direct execution")
