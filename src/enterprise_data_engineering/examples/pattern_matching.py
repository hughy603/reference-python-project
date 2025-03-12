"""
Pattern Matching Examples for Python 3.12.

This module demonstrates structural pattern matching features available in Python 3.12,
which builds upon pattern matching introduced in Python 3.10.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Generic, NamedTuple, NotRequired, Self, TypedDict, TypeVar


# Dataclasses for use in pattern matching
@dataclass
class Point:
    """A 2D point with x and y coordinates.

    Attributes:
        x: The x-coordinate (horizontal position)
        y: The y-coordinate (vertical position)
    """

    x: float
    y: float

    def __add__(self, other: Self) -> Self:
        """Add two points by adding their coordinates.

        Args:
            other: Another Point object to add to this one

        Returns:
            A new Point with the sum of coordinates

        Raises:
            TypeError: If the other object is not a Point
        """
        if not isinstance(other, Point):
            return NotImplemented
        return Point(self.x + other.x, self.y + other.y)  # type: ignore


@dataclass
class Circle:
    """A circle with a center point and radius.

    Attributes:
        center: The center point of the circle
        radius: The radius of the circle (distance from center to edge)
    """

    center: Point
    radius: float


@dataclass
class Rectangle:
    """A rectangle defined by top-left and bottom-right points.

    Attributes:
        top_left: The top-left corner point
        bottom_right: The bottom-right corner point
    """

    top_left: Point
    bottom_right: Point


class Color(Enum):
    """Color enumeration.

    Attributes:
        RED: Red color
        GREEN: Green color
        BLUE: Blue color
        YELLOW: Yellow color
    """

    RED = auto()
    GREEN = auto()
    BLUE = auto()
    YELLOW = auto()


class Person(TypedDict):
    """Person typed dictionary.

    Attributes:
        name: Full name of the person
        age: Age in years
        email: Optional email address
    """

    name: str
    age: int
    email: NotRequired[str]


T = TypeVar("T")


@dataclass
class Container(Generic[T]):
    """A generic container that can hold any type of data.

    Attributes:
        value: The contained value of type T
    """

    value: T


class Coordinate(NamedTuple):
    """A named tuple representing geographic coordinates.

    Attributes:
        latitude: The latitude value (North/South position)
        longitude: The longitude value (East/West position)
    """

    latitude: float
    longitude: float


def match_type_demonstration(obj: Any) -> str:
    """Demonstrate basic type pattern matching.

    Args:
        obj: Any Python object to match against different types

    Returns:
        A string describing the matched pattern
    """
    match obj:
        case int():
            return f"Matched an integer: {obj}"
        case str():
            return f"Matched a string of length {len(obj)}: '{obj}'"
        case bool():
            return f"Matched a boolean: {obj}"
        case float():
            return f"Matched a float: {obj}"
        case list():
            return f"Matched a list with {len(obj)} elements"
        case tuple():
            return f"Matched a tuple with {len(obj)} elements"
        case dict():
            return f"Matched a dictionary with {len(obj)} keys"
        case set():
            return f"Matched a set with {len(obj)} elements"
        case Point():
            return f"Matched a Point at ({obj.x}, {obj.y})"
        case Circle():
            return f"Matched a Circle at ({obj.center.x}, {obj.center.y}) with radius {obj.radius}"
        case Rectangle():
            return f"Matched a Rectangle from ({obj.top_left.x}, {obj.top_left.y}) to ({obj.bottom_right.x}, {obj.bottom_right.y})"
        case _:
            return f"No pattern matched for object of type {type(obj).__name__}"


def match_structure_demonstration(obj: Any) -> str:
    """
    Demonstrate structural pattern matching.

    Args:
        obj: Object to match against various structures

    Returns:
        A string describing the matched structure
    """
    match obj:
        # Match specific list patterns
        case []:
            return "Empty list"
        case [x]:
            return f"Single-element list containing {x}"
        case [x, y]:
            return f"Two-element list containing {x} and {y}"
        case [x, y, *rest]:
            return f"List with at least two elements: {x}, {y}, and {len(rest)} more"

        # Match specific dictionary patterns
        case {"name": name, "age": age}:
            return f"Person named {name} who is {age} years old"
        case {"type": "point", "x": x, "y": y}:
            return f"Point at ({x}, {y})"

        # Match classes
        case Point(x=x, y=y):
            return f"Point instance at ({x}, {y})"
        case Circle(center=Point(x=x, y=y), radius=r):
            return f"Circle with center at ({x}, {y}) and radius {r}"
        case Rectangle(top_left=Point(x=x1, y=y1), bottom_right=Point(x=x2, y=y2)):
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            return f"Rectangle with width {width} and height {height}"

        # Default case
        case _:
            return "No matching pattern found"


def match_guards_demonstration(obj: Any) -> str:
    """
    Demonstrate pattern matching with guard conditions.

    Args:
        obj: Object to match with additional guard conditions

    Returns:
        A string describing the matched pattern with guard
    """
    match obj:
        case int(x) if x < 0:
            return f"Negative integer: {x}"
        case int(x) if x == 0:
            return "Zero"
        case int(x) if x > 0:
            return f"Positive integer: {x}"

        case float(x) if x < 0:
            return f"Negative float: {x}"
        case float(x) if x == 0:
            return "Zero (float)"
        case float(x) if x > 0:
            return f"Positive float: {x}"

        case Point(x=x, y=y) if x == 0 and y == 0:
            return "Point at origin"
        case Point(x=x, y=y) if x == 0:
            return f"Point on y-axis at y={y}"
        case Point(x=x, y=y) if y == 0:
            return f"Point on x-axis at x={x}"
        case Point(x=x, y=y) if x == y:
            return f"Point on diagonal at ({x}, {y})"

        case _:
            return "No matching pattern with guard found"


def advanced_pattern_matching(obj: Any) -> str:
    """
    Demonstrate more advanced pattern matching features.

    Args:
        obj: Object to match against various complex patterns

    Returns:
        A string describing the matched pattern
    """
    match obj:
        # OR patterns (| operator)
        case int() | float():
            return f"Number: {obj}"
        case str() | bytes():
            return f"String-like: {obj}"

        # Named sub-patterns using 'as'
        case [*items] as full_list if len(full_list) > 5:
            return f"Long list with {len(items)} items"
        case {"items": [*items]} as full_dict if len(items) > 3:
            return f"Dictionary with many items: {len(items)}"

        # Class hierarchy matching
        case Color.RED:
            return "Red color"
        case Color.GREEN | Color.BLUE:
            return "Green or blue color"
        case Color():
            return f"Other color: {obj.name}"

        # Container matching
        case Container(value=int(x)):
            return f"Container holding integer: {x}"
        case Container(value=str(s)):
            return f"Container holding string: {s}"
        case Container():
            return f"Container holding: {obj.value}"

        # TypedDict matching
        case {"name": str(name), "age": int(age), "email": str(email)}:
            return f"Complete person record: {name}, {age}, {email}"
        case {"name": str(name), "age": int(age)}:
            return f"Basic person record: {name}, {age}"

        # Named tuple matching
        case Coordinate(latitude=lat, longitude=lon) if -90 <= lat <= 90 and -180 <= lon <= 180:
            return f"Valid coordinates: {lat}°, {lon}°"
        case Coordinate():
            return "Invalid coordinates"

        case _:
            return "No advanced pattern matched"


def process_data(data: Any) -> str:
    """
    Process data using pattern matching to determine appropriate handling.

    This is a realistic example of how pattern matching can simplify complex
    conditional logic in data processing.

    Args:
        data: The data to process

    Returns:
        Result of processing the data
    """
    match data:
        # Configuration cases
        case {"config": {"debug": bool(debug_mode), "verbose": bool(verbose)}}:
            config_result = f"Config with debug={debug_mode}, verbose={verbose}"
            if debug_mode and verbose:
                return f"{config_result} (full logging enabled)"
            return config_result

        # Geometric shape cases
        case Circle(center=Point(x=x, y=y), radius=r) if r > 0:
            area = 3.14159 * r * r
            return f"Valid circle at ({x}, {y}) with area {area:.2f}"

        case Rectangle(top_left=Point(x=x1, y=y1), bottom_right=Point(x=x2, y=y2)):
            if x1 < x2 and y1 < y2:
                width, height = x2 - x1, y2 - y1
                area = width * height
                return f"Valid rectangle with area {area:.2f}"
            return "Invalid rectangle coordinates"

        # Command processing cases
        case {"command": "create", "type": str(type_), "data": dict(payload)}:
            return f"Creating {type_} with {len(payload)} properties"

        case {"command": "update", "id": str(id_), "changes": dict(changes)}:
            return f"Updating object {id_} with {len(changes)} changes"

        case {"command": "delete", "id": str(id_)}:
            return f"Deleting object {id_}"

        # Data structure cases
        case [{"name": str(name), "value": value} as entry, *rest]:
            total_entries = len(rest) + 1
            return f"Processing {total_entries} entries, starting with {name}={value}"

        # Error or unrecognized cases
        case {"error": str(message)}:
            return f"Error occurred: {message}"

        case _:
            return "Unrecognized data format"


def main() -> None:
    """Run examples of pattern matching."""
    # Simple type matching
    print("Type Matching Examples:")
    print(match_type_demonstration(42))
    print(match_type_demonstration(3.14))
    print(match_type_demonstration("hello"))
    print(match_type_demonstration([1, 2, 3]))
    print(match_type_demonstration({"a": 1, "b": 2}))
    print()

    # Structure matching
    print("Structure Matching Examples:")
    print(match_structure_demonstration([]))
    print(match_structure_demonstration([1]))
    print(match_structure_demonstration([1, 2]))
    print(match_structure_demonstration([1, 2, 3, 4]))
    print(match_structure_demonstration({"name": "Alice", "age": 30}))
    print(match_structure_demonstration({"type": "point", "x": 10, "y": 20}))
    print(match_structure_demonstration(Point(x=5, y=10)))
    print(match_structure_demonstration(Circle(center=Point(0, 0), radius=5)))
    print(
        match_structure_demonstration(Rectangle(top_left=Point(0, 0), bottom_right=Point(10, 20)))
    )
    print()

    # Guard conditions
    print("Guard Condition Examples:")
    print(match_guards_demonstration(-5))
    print(match_guards_demonstration(0))
    print(match_guards_demonstration(10))
    print(match_guards_demonstration(-3.14))
    print(match_guards_demonstration(2.71))
    print(match_guards_demonstration(Point(0, 0)))
    print(match_guards_demonstration(Point(0, 5)))
    print(match_guards_demonstration(Point(5, 0)))
    print(match_guards_demonstration(Point(7, 7)))
    print()

    # Advanced pattern matching
    print("Advanced Pattern Matching Examples:")
    print(advanced_pattern_matching(42.5))
    print(advanced_pattern_matching("text"))
    print(advanced_pattern_matching([1, 2, 3, 4, 5, 6]))
    print(advanced_pattern_matching({"items": [1, 2, 3, 4]}))
    print(advanced_pattern_matching(Color.RED))
    print(advanced_pattern_matching(Color.BLUE))
    print(advanced_pattern_matching(Color.YELLOW))
    print(advanced_pattern_matching(Container(42)))
    print(advanced_pattern_matching(Container("hello")))
    print(advanced_pattern_matching({"name": "Bob", "age": 25, "email": "bob@example.com"}))
    print(advanced_pattern_matching({"name": "Alice", "age": 30}))
    print(advanced_pattern_matching(Coordinate(37.7749, -122.4194)))  # San Francisco
    print()

    # Realistic example
    print("Realistic Data Processing Examples:")
    print(process_data({"config": {"debug": True, "verbose": True}}))
    print(process_data(Circle(center=Point(1, 2), radius=5)))
    print(process_data(Rectangle(top_left=Point(0, 0), bottom_right=Point(5, 10))))
    print(process_data(Rectangle(top_left=Point(10, 10), bottom_right=Point(5, 5))))
    print(
        process_data(
            {
                "command": "create",
                "type": "user",
                "data": {"name": "Charlie", "email": "charlie@example.com"},
            }
        )
    )
    print(
        process_data(
            {
                "command": "update",
                "id": "12345",
                "changes": {"status": "active", "last_login": "2023-01-01"},
            }
        )
    )
    print(process_data({"command": "delete", "id": "67890"}))
    print(
        process_data(
            [
                {"name": "item1", "value": 100},
                {"name": "item2", "value": 200},
                {"name": "item3", "value": 300},
            ]
        )
    )
    print(process_data({"error": "Connection failed"}))
    print(process_data("Unrecognized format"))


if __name__ == "__main__":
    main()
