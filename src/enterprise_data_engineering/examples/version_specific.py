"""
Version-Specific Code Example

This module demonstrates how to write code that uses Python 3.12 features
when available, but falls back to compatible alternatives on older versions.
"""

import subprocess
import sys
from subprocess import PIPE
from typing import Any

# Import from our compatibility module
from enterprise_data_engineering.compat import PY_310, PY_311, PY_312, Generic, TypeVar

# Example 1: Type Alias - Different syntax based on Python version
if PY_312:
    # Python 3.12 syntax
    type Point2D = tuple[float, float]
else:
    # Older Python syntax
    Point2D = tuple[float, float]


# Example 2: Class Definition with Type Parameters
# Use different class names for each version to avoid shadowing
T = TypeVar("T")  # Define TypeVar outside of conditionals for use in both versions

if PY_312:
    # Python 3.12 syntax for generic classes
    class Container312[T]:
        """Generic container using Python 3.12 syntax."""

        def __init__(self, value: T) -> None:
            self.value = value

        def get(self) -> T:
            return self.value

        def set(self, value: T) -> None:
            self.value = value
else:
    # Compatible syntax for earlier Python versions
    class Container312(Generic[T]):
        """Generic container using pre-3.12 syntax."""

        def __init__(self, value: T) -> None:
            self.value = value

        def get(self) -> T:
            return self.value

        def set(self, value: T) -> None:
            self.value = value


# Example 3: Self type - Added in Python 3.11
class LinkedNode:
    """Linked node using Self type (compatible across versions)."""

    def __init__(self, value: Any) -> None:
        self.value = value
        self.next: LinkedNode | None = None

    def set_next(self, node: "LinkedNode") -> None:
        """Set the next node."""
        self.next = node

    def create_next(self, value: Any) -> "LinkedNode":
        """Create and return a new next node."""
        node = LinkedNode(value)
        self.next = node
        return node


# Example 4: Using different standard library APIs by version
def create_process():
    """Create a process using different APIs based on Python version."""
    # Parameters that work in all versions
    command = ["echo", "Hello"]

    if PY_312:
        # In Python 3.12, you might use new features (for demonstration)
        # For this example, we'll just add an encoding parameter which is available in all versions
        # but imagine there was a new parameter only in 3.12
        return subprocess.Popen(command, text=True, stdout=PIPE, stderr=PIPE, encoding="utf-8")
    else:
        # Compatible version for older Python
        return subprocess.Popen(command, text=True, stdout=PIPE, stderr=PIPE)


def main():
    """Demonstrate the version-specific features."""
    print(
        f"Running Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )

    # Test type aliases
    coord: Point2D = (1.0, 2.0)
    print(f"2D coordinates: {coord}")

    # Test container class
    int_container = Container312[int](42)
    str_container = Container312[str]("Hello")
    print(f"Integer container: {int_container.get()}")
    print(f"String container: {str_container.get()}")

    # Test LinkedNode with Self type
    root = LinkedNode("root")
    child = LinkedNode("child")
    root.set_next(child)
    grandchild = child.create_next("grandchild")
    print(f"Linked List: {root.value} -> ", end="")
    if root.next:
        print(f"{root.next.value} -> ", end="")
        if grandchild:
            print(f"{grandchild.value}")
        else:
            print("None")
    else:
        print("None")

    # Test process creation
    proc = create_process()
    stdout, stderr = proc.communicate()
    print(f"Process output: {stdout}")

    print(f"\nPython version flags: 3.10+ = {PY_310}, 3.11+ = {PY_311}, 3.12+ = {PY_312}")
    print("Compatibility layer successfully demonstrated!")


if __name__ == "__main__":
    main()
