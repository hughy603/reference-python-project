# AWS Mocking Examples with Moto

This directory contains examples of how to use Moto's latest `mock_aws` decorator syntax to mock AWS
services in unit tests.

## Overview

[Moto](https://github.com/getmoto/moto) is a library that allows you to mock AWS services in your
Python tests. It provides a way to test your AWS integrations without making actual AWS API calls,
making your tests faster, more reliable, and cost-effective.

## Examples Included

1. **S3 Operations (`test_s3_operations.py`)**

   - Basic bucket operations (create, list)
   - Object operations (put, get, delete)
   - Advanced features (versioning, tagging, presigned URLs)
   - Error handling
   - Using fixtures with Moto

1. **DynamoDB Operations (`test_dynamodb_operations.py`)**

   - Table operations (create, describe)
   - Item operations (put, get, update, delete)
   - Batch write operations
   - Query and scan with filters
   - Conditional operations
   - Handling decimal types
   - Repository pattern example

1. **Multiple Services (`test_aws_integration.py`)**

   - Combined S3 and DynamoDB operations
   - Managing context with fixtures
   - Real-world data processing example

## Usage Patterns

The examples demonstrate several patterns for using Moto:

### 1. Class-level Decorator

```python
@mock_aws
def test_something():
    # Your test code here
```

### 2. Context Manager

```python
def test_something():
    with mock_aws():
        # Your test code here
```

### 3. Pytest Fixtures

```python
@pytest.fixture
def s3_client():
    with mock_aws():
        yield boto3.client('s3', region_name='us-east-1')

def test_with_fixture(s3_client):
    # Test using the mocked client
```

## Key Features Demonstrated

- New `mock_aws` syntax (preferred over legacy service-specific decorators)
- Type hints for improved code quality
- Proper test structure (Arrange-Act-Assert)
- Error handling and edge cases
- Business logic testing patterns
- Repository pattern implementation
- Integration testing of multiple services

## Best Practices

1. Always specify a region when creating AWS clients
1. Use fixture teardown to clean up resources
1. Structure tests in the Arrange-Act-Assert pattern
1. Test error conditions and edge cases
1. Create higher-level abstractions (like repositories) for cleaner code

## Running the Tests

```bash
# Run all AWS mocking examples
pytest tests/unit/aws_mocking_examples

# Run S3 tests only
pytest tests/unit/aws_mocking_examples/test_s3_operations.py

# Run DynamoDB tests only
pytest tests/unit/aws_mocking_examples/test_dynamodb_operations.py

# Run integration tests only
pytest tests/unit/aws_mocking_examples/test_aws_integration.py
```

## Dependencies

These examples require:

- boto3
- moto>=4.2.0
- pytest
- pytest-mock
