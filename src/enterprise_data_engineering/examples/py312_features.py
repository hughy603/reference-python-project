"""
Example module showcasing Python 3.12 features.

This module demonstrates key features introduced or improved in Python 3.12
including type alias declarations, exception groups, and improved error diagnostics.
"""

import asyncio
import sys
from collections.abc import Sequence
from dataclasses import dataclass

# PEP 695: Type Parameter Syntax for Type Aliases
type Point2D = tuple[float, float]
type Point3D = tuple[float, float, float]
type CoordinateSystem[T] = dict[str, T]  # Generic type alias

# Type parameter with a bound
type Vector[T: float] = list[T]  # Using bound directly in the type alias


# Class Type Parameters (PEP 695)
class Container[T]:
    """Generic container class using new type syntax."""

    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value


# Exception groups (PEP 654, improved in 3.12)
def demonstrate_exception_groups() -> None:
    """Demonstrate exception groups with except* syntax."""
    try:
        try:
            raise ExceptionGroup(
                "multiple errors",
                [
                    ValueError("invalid value"),
                    TypeError("invalid type"),
                    RuntimeError("runtime error"),
                ],
            )
        except* ValueError as e:
            print(f"Caught ValueError: {e.exceptions}")
        except* TypeError as e:
            print(f"Caught TypeError: {e.exceptions}")
        # Other exceptions will propagate
    except ExceptionGroup as eg:
        print(f"Caught remaining exceptions: {eg}")


# F-string debugging syntax (introduced in 3.8 but worth highlighting)
def debug_example(x: int, y: str) -> None:
    """Demonstrate f-string debugging."""
    print(f"{x=}")  # Shows x=<value>
    print(f"{y=}")  # Shows y=<value>
    print(f"{x + 10=}")  # Shows x + 10=<result>


# Dataclass improvements
@dataclass(slots=True)  # More efficient with slots
class User:
    """User class demonstrating improved dataclasses with slots."""

    name: str
    age: int
    email: str | None = None

    def is_adult(self) -> bool:
        """Check if user is an adult."""
        return self.age >= 18


# Improved async features
async def process_items(items: Sequence[int]) -> list[int]:
    """Process items concurrently using TaskGroup."""
    results = []

    # Using TaskGroup for concurrent tasks (Python 3.11+, improved in 3.12)
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(process_item(item)) for item in items]

    # All tasks are guaranteed to be done here
    return [task.result() for task in tasks]


async def process_item(item: int) -> int:
    """Process a single item."""
    await asyncio.sleep(0.1)  # Simulate some work
    return item * 2


def python_version_check() -> None:
    """Print Python version and verify we're running on 3.12+."""
    print(
        f"Running Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    if sys.version_info < (3, 12):
        print("Warning: This module is designed for Python 3.12+")


def main() -> None:
    """Main function demonstrating Python 3.12 features."""
    python_version_check()

    # Demonstrate type aliases
    coords_2d: Point2D = (10.5, 20.5)
    coords_3d: Point3D = (10.5, 20.5, 30.5)

    coordinate_system: CoordinateSystem[Point3D] = {
        "origin": (0.0, 0.0, 0.0),
        "point_a": (1.0, 1.0, 1.0),
    }

    # Using generic container
    int_container = Container[int](42)
    str_container = Container[str]("Hello Python 3.12")

    print(f"2D coordinates: {coords_2d}")
    print(f"3D coordinates: {coords_3d}")
    print(f"Coordinate system: {coordinate_system}")
    print(f"Integer container value: {int_container.get()}")
    print(f"String container value: {str_container.get()}")

    # Demonstrate debugging features
    debug_example(42, "Python 3.12")

    # Dataclass example
    user = User(name="Jane Doe", age=30, email="jane@example.com")
    print(f"User: {user}")
    print(f"Is adult: {user.is_adult()}")

    # Demonstrate exception groups
    try:
        demonstrate_exception_groups()
    except Exception as e:
        print(f"Caught exception: {e}")

    # Async features - this would normally be run with asyncio.run()
    print("To run async examples, use asyncio.run(process_items([1, 2, 3]))")


if __name__ == "__main__":
    main()
