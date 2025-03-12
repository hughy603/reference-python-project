"""
Compatibility module for Python version differences.

This module provides compatibility layers for Python 3.11, 3.12, and 3.13 to use features
that were introduced in later Python versions, particularly Python 3.11+.
"""

import subprocess
import sys
from builtins import ExceptionGroup
from collections.abc import Callable

# Import all typing-related modules at the top
from typing import (
    Any,
    Generic,
    NotRequired,
    Optional,
    Self,
    TypeAliasType,
    TypeVar,
    Union,
    assert_type,
)

# Define Python version flags for conditional imports
PY_311 = sys.version_info >= (3, 11)
PY_312 = sys.version_info >= (3, 12)
PY_313 = sys.version_info >= (3, 13)

# Conditional implementations based on Python version
if PY_312:
    # For Python 3.12+, use native features
    def create_type_alias(name: str, value: Any) -> Any:
        """Create a named type alias (PEP 695)."""
        return value

    # In Python 3.12, we can define type aliases with a new syntax
    # type Point2D = tuple[float, float]
else:
    # For older Python versions, use typing_extensions
    def create_type_alias(name: str, value: Any) -> Any:
        """Create a type alias with name for older Python versions."""
        return value


def type_alias_syntax_example() -> Any:
    """Demonstrate how to use type alias with compatibility.

    Returns:
        A type alias for a 2D point (tuple of two floats)
    """
    # In Python 3.12+:
    # type Point2D = tuple[float, float]

    # For compatibility:
    Point2D = create_type_alias("Point2D", tuple[float, float])
    return Point2D


def type_parameter_example() -> Any:
    """Show how to use type parameters with compatibility.

    Returns:
        A generic container class that works across Python versions
    """
    # In Python 3.12+:
    # class Container[T]: ...

    # For compatibility with earlier versions:
    T = TypeVar("T")

    class Container(Generic[T]):
        """A generic container class that holds a value of type T."""

        def __init__(self, value: T) -> None:
            """Initialize the container with a value.

            Args:
                value: The value to store in the container
            """
            self.value = value

        def get(self) -> T:
            """Get the stored value.

            Returns:
                The stored value of type T
            """
            return self.value

        def set(self, value: T) -> None:
            """Set a new value in the container.

            Args:
                value: The new value to store
            """
            self.value = value

    return Container


def run_subprocess_compat(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    """Run a subprocess with backward compatibility for different Python versions.

    This demonstrates using different subprocess APIs based on Python version.

    Args:
        cmd: Command to execute as a list of strings
        **kwargs: Additional keyword arguments to pass to subprocess.run

    Returns:
        CompletedProcess instance with execution results
    """
    # In Python 3.12+, the preferred method is subprocess.run with additional features
    return subprocess.run(
        cmd,
        text=True,  # Use text mode instead of universal_newlines (deprecated in 3.12+)
        capture_output=True,  # Capture both stdout and stderr
        **kwargs,
    )


# Export all the public symbols
__all__ = [
    "PY_311",
    "PY_312",
    "PY_313",
    "ExceptionGroup",
    "NotRequired",
    "Self",
    "TypeAliasType",
    "assert_type",
    "create_type_alias",
    "run_subprocess_compat",
    "type_alias_syntax_example",
    "type_parameter_example",
]
