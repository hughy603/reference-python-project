# Source Code Structure

This directory contains the source code for the Enterprise Data Engineering project following the
src-layout pattern.

## Directory Structure

- `enterprise_data_engineering/`: Main package directory

  - `common_utils/`: Common utilities and shared code
  - `data_pipelines/`: Data pipeline implementation code
  - `compat/`: Compatibility layer for different Python versions
  - `spark/`: Apache Spark utilities and transformations
  - `examples/`: Example code and usage patterns

## Package Organization Standards

The project follows these standards for package organization:

1. **src-layout**: All Python packages are inside the `src/` directory
1. **Namespace packages**: Using proper namespacing to avoid conflicts
1. **Flat imports**: Public API is importable directly from the main package
1. **Separation of concerns**:
   - Core domain logic in dedicated modules
   - Infrastructure/platform code separated from business logic
   - CLI interfaces separate from application logic

## Benefits of src Layout

Using the src layout provides several benefits:

- Ensures the package is installed properly during development
- Prevents import confusion during testing
- Validates that the package is importable as it would be after installation
- Encourages proper package structure and namespacing

## Development

When working with this codebase, you should install it in development mode:

```bash
pip install -e .
```

This ensures that imports work correctly while allowing you to modify the code without reinstalling.
