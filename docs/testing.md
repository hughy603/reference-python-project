# Testing Guide

This document outlines the testing approach, structure, and best practices for this project.

## Test Configuration

All testing configuration is consolidated in `pyproject.toml` under the `[tool.pytest]` section.
This includes:

- Test discovery patterns
- Test markers
- Coverage settings
- Plugin configurations

## Testing Framework

This project uses pytest for testing. To run tests:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run a specific test module
pytest tests/path/to/test_module.py

# Run tests with a specific marker
pytest -m "marker_name"
```

## Test Structure

The tests are organized into the following structure:

```
tests/
├── README.md                          # Overview of test structure and guidance
├── test_enterprise_data_engineering/  # Tests for the main package
├── test_aws/                          # AWS-specific tests
├── test_wizards/                      # Tests for initialization wizards
├── common_utils/                      # Shared test utilities
└── shared/                            # Shared fixtures and conftest.py
```

## Test Categories

The tests are organized into the following categories:

### Unit Tests

Unit tests focus on testing individual components in isolation. They should be:

- Fast: Execute in milliseconds
- Independent: No external dependencies or services
- Deterministic: Same results every time

Location: Tests are located in the appropriate module directory based on the component being tested.

### Integration Tests

Integration tests verify that different components work together correctly. They test:

- Component interactions
- Data flow between components
- API contracts

Integration tests may require:

- More setup and teardown
- Access to external resources (which can be mocked)

### Functional Tests

Functional tests verify that the system works as expected from the user's perspective. They test:

- End-to-end functionality
- User workflows
- System behavior

## Writing Tests

### Best Practices

1. **Use fixtures**: Utilize pytest fixtures for setup and teardown.
1. **Name tests descriptively**: Test names should clearly describe what they're testing.
1. **Follow the AAA pattern**:
   - **Arrange**: Set up test data and conditions
   - **Act**: Perform the action being tested
   - **Assert**: Verify the results
1. **Use markers appropriately**: Tag tests with markers for categorization.
1. **Keep tests independent**: Tests should not depend on each other.
1. **Test edge cases**: Include tests for boundary conditions and error cases.

### Example Test

```python
import pytest
from my_package import my_function

def test_my_function_normal_case():
    # Arrange
    input_data = {"key": "value"}

    # Act
    result = my_function(input_data)

    # Assert
    assert result == expected_output
    assert isinstance(result, dict)
```

## Test Coverage

We aim for high test coverage but prioritize quality over quantity. The goal is to cover:

- All public API methods
- Critical paths and error handling
- Edge cases and boundary conditions

To check coverage:

```bash
pytest --cov=src --cov-report=html
```

Then open `htmlcov/index.html` in your browser to view the coverage report.

## Mocking

For testing components with external dependencies, use pytest-mock or unittest.mock:

```python
def test_with_mocking(mocker):
    # Mock external service
    mock_service = mocker.patch('package.module.ExternalService')
    mock_service.return_value.method.return_value = expected_data

    # Test code that uses the external service
    result = function_under_test()

    # Assertions
    mock_service.assert_called_once()
    assert result == expected_output
```

## Continuous Integration

All tests are automatically run in CI when you push changes. The CI pipeline:

1. Runs all tests
1. Generates coverage reports
1. Fails the build if tests fail or coverage drops below thresholds

## Adding New Tests

When adding new functionality:

1. Create corresponding test files in the appropriate test directory
1. Include both happy path and error cases
1. Consider adding edge cases and boundary conditions
1. Ensure tests are isolated and repeatable
