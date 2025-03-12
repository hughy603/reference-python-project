"""
Module Template

This template provides a basic structure for creating new modules in the
Enterprise Data Engineering project. Use this as a starting point for
your own modules.

Usage:
    1. Copy this file to a new location in the project
    2. Rename the file to match your module's purpose
    3. Customize the functions and classes as needed
    4. Update the docstrings and type hints

Example:
    from enterprise_data_engineering.examples.module_template import example_function

    result = example_function("test")
    print(result)
"""

from typing import Any


def example_function(input_string: str) -> str:
    """
    Example function demonstrating proper docstring format.

    Args:
        input_string: A string input to process

    Returns:
        A processed string output

    Raises:
        ValueError: If input_string is empty
    """
    if not input_string:
        raise ValueError("Input string cannot be empty")

    return f"Processed: {input_string}"


class ExampleClass:
    """
    Example class demonstrating proper structure and docstrings.

    This class shows how to structure a class with proper typing,
    docstrings, and method organization.

    Attributes:
        name: The name of the example instance
        value: The value associated with this instance
    """

    def __init__(self, name: str, value: int | None = None):
        """
        Initialize the ExampleClass.

        Args:
            name: The name for this instance
            value: An optional value for this instance
        """
        self.name = name
        self.value = value or 0
        self._private_value = "internal"

    def process_data(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Process the given data and return results.

        Args:
            data: A list of dictionaries containing data to process

        Returns:
            A dictionary with processed results
        """
        result: dict[str, Any] = {"name": self.name, "value": self.value, "data_count": len(data)}

        # This is just an example - customize with your actual processing logic
        if data:
            result["first_item"] = data[0]
            result["keys_found"] = list(set().union(*(d.keys() for d in data)))

        return result

    @property
    def summary(self) -> str:
        """Get a summary of this instance."""
        return f"ExampleClass(name='{self.name}', value={self.value})"

    @classmethod
    def create_default(cls) -> "ExampleClass":
        """Create an instance with default values."""
        return cls("default", 0)


# Example async function for modern Python applications
async def async_example(timeout: float = 1.0) -> dict[str, Any]:
    """
    Example of an async function.

    Args:
        timeout: Time to wait in seconds

    Returns:
        A dictionary with result information
    """
    # This shows how you might use async/await
    import asyncio

    await asyncio.sleep(timeout)

    return {"status": "complete", "waited": timeout}


# If the module can be run directly, provide an example usage
if __name__ == "__main__":
    # Example usage of the function
    print(example_function("Hello World"))

    # Example usage of the class
    example = ExampleClass("test_instance", 42)
    sample_data = [{"a": 1, "b": 2}, {"b": 3, "c": 4}]
    result = example.process_data(sample_data)
    print(result)
    print(example.summary)

    # Note: Async functions need to be run in an event loop
    # This shows how you would typically run an async function
    import asyncio

    async_result = asyncio.run(async_example(0.1))
    print(async_result)
