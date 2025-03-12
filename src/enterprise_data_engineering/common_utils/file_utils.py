"""
File utility functions for data engineering tasks.

This module provides common functions for file handling, path operations,
and filesystem management.
"""

import os
import pathlib


def get_file_extension(file_path: str | pathlib.Path) -> str:
    """Get the file extension from a path.

    Args:
        file_path: Path to the file as string or Path object

    Returns:
        File extension (without the dot) or empty string if no extension

    Examples:
        >>> get_file_extension("data/file.csv")
        'csv'
        >>> get_file_extension("data/file")
        ''
    """
    return os.path.splitext(str(file_path))[1].lstrip(".")


def ensure_directory_exists(directory_path: str | pathlib.Path) -> pathlib.Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        directory_path: Path to the directory to ensure exists

    Returns:
        Path object for the directory

    Examples:
        >>> path = ensure_directory_exists("data/processed")
        >>> path.exists()
        True
    """
    path = pathlib.Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_files_with_extension(
    directory: str | pathlib.Path, extension: str, recursive: bool = False
) -> list[pathlib.Path]:
    """List all files with the specified extension in a directory.

    Args:
        directory: Path to the directory to search
        extension: File extension to filter by (without the dot)
        recursive: Whether to search subdirectories recursively

    Returns:
        List of Path objects for matching files

    Examples:
        >>> files = list_files_with_extension("data", "csv")
        >>> len(files)
        3
    """
    directory_path = pathlib.Path(directory)
    if not directory_path.exists() or not directory_path.is_dir():
        return []

    if recursive:
        return list(directory_path.glob(f"**/*.{extension}"))
    else:
        return list(directory_path.glob(f"*.{extension}"))


def safe_file_write(
    file_path: str | pathlib.Path, content: str, create_dirs: bool = True, encoding: str = "utf-8"
) -> None:
    """Safely write content to a file, creating parent directories if needed.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        create_dirs: Whether to create parent directories if they don't exist
        encoding: File encoding to use

    Examples:
        >>> safe_file_write("data/output/results.txt", "Data processing complete")
    """
    path = pathlib.Path(file_path)

    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(content, encoding=encoding)


def read_file_content(
    file_path: str | pathlib.Path, encoding: str = "utf-8", default: str | None = None
) -> str | None:
    """Read content from a file with error handling.

    Args:
        file_path: Path to the file to read
        encoding: File encoding to use
        default: Default value to return if file doesn't exist or can't be read

    Returns:
        File content as string or default value if file can't be read

    Examples:
        >>> content = read_file_content("config.json")
        >>> content is not None
        True
    """
    path = pathlib.Path(file_path)

    if not path.exists():
        return default

    try:
        return path.read_text(encoding=encoding)
    except Exception:
        return default
