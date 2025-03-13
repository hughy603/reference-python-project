# Test Structure

This directory contains tests for the Enterprise Data Engineering project. The tests are organized
into the following directories:

## Directory Structure

- `test_enterprise_data_engineering/`: Tests for the core enterprise data engineering functionality
- `test_aws/`: Tests for AWS-related functionality, including mocking examples
- `test_wizards/`: Tests for project initialization and wizard functionality
- `common_utils/`: Test implementations of common utilities and helpers
- `shared/`: Shared test fixtures, conftest.py, and other test utilities

## Running Tests

To run all tests:

```bash
hatch run test:run
```

To run tests with coverage:

```bash
hatch run test:cov
```

To run a specific test directory:

```bash
hatch run test:run tests/test_aws
```

## Test Markers

The following markers are available for pytest:

- `slow`: marks tests as slow (deselect with `-m "not slow"`)
- `integration`: marks tests as integration tests (deselect with `-m "not integration"`)
- `aws`: marks tests that use AWS resources (deselect with `-m "not aws"`)

Example:

```bash
hatch run pytest -m "not aws" tests/
```
