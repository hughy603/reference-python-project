"""Check available moto mock decorators."""

import inspect

import moto

# Print available mocks
print("Available mock decorators in moto:")
mock_modules = [name for name in dir(moto) if name.startswith("mock_")]
for mock in mock_modules:
    print(f"- {mock}")

# Print implementation details of mock_aws
print("\nMock AWS implementation details:")
print(inspect.getsource(moto.mock_aws))

# Try to inspect services
try:
    from moto.core import mock_backends

    print("\nMock backends:")
    for backend in mock_backends:
        print(f"- {backend}")
except (ImportError, AttributeError) as e:
    print(f"\nError inspecting backends: {e}")
