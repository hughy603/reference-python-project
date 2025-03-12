#!/usr/bin/env python
"""
Script to generate API documentation from Python source code.

This script analyzes the Python source code and generates Markdown documentation
for the API reference section of the documentation site.
"""

import importlib
import inspect
import sys
from pathlib import Path
from typing import Any

# Add src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Output directory for generated API docs
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "reference"
PACKAGE_NAME = "enterprise_data_engineering"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_module_members(module: Any) -> dict[str, Any]:
    """Get all relevant members from a module."""
    return {
        name: member
        for name, member in inspect.getmembers(module)
        if not name.startswith("_") and not inspect.isbuiltin(member)
    }


def import_module(module_path: str) -> Any | None:
    """Import a module and return it, or None if it fails."""
    try:
        return importlib.import_module(module_path)
    except (ImportError, AttributeError) as e:
        print(f"Error importing {module_path}: {e}")
        return None


def find_modules(package_path: str) -> list[str]:
    """Recursively find all modules in a package."""
    module_paths = []
    package = import_module(package_path)

    if package is None:
        return module_paths

    # Add the package itself
    module_paths.append(package_path)

    # Get the package directory
    if hasattr(package, "__path__"):
        package_dir = Path(package.__path__[0])
        # Find all Python files in the package
        for item in package_dir.glob("**/*.py"):
            if item.name.startswith("_"):
                continue

            # Convert file path to module path
            rel_path = item.relative_to(package_dir)
            module_name = ".".join(
                [package_path] + [p.stem for p in rel_path.parents if p.stem][::-1] + [item.stem]
            )

            # Avoid duplicate modules
            if module_name not in module_paths:
                module_paths.append(module_name)

    return module_paths


def generate_module_doc(module_path: str) -> str:
    """Generate documentation for a module."""
    module = import_module(module_path)
    if module is None:
        return f"# {module_path}\n\nFailed to import module.\n"

    # Module title
    doc = f"# {module_path}\n\n"

    # Module docstring
    if module.__doc__:
        doc += f"{inspect.getdoc(module)}\n\n"

    # Get members of the module
    members = get_module_members(module)

    # Process classes
    classes = {name: obj for name, obj in members.items() if inspect.isclass(obj)}
    if classes:
        doc += "## Classes\n\n"
        for name, cls in sorted(classes.items()):
            doc += f"### {name}\n\n"
            if cls.__doc__:
                doc += f"{inspect.getdoc(cls)}\n\n"

            # Class attributes
            attributes = {
                attr: value
                for attr, value in cls.__dict__.items()
                if not attr.startswith("_")
                and not inspect.isfunction(value)
                and not inspect.ismethod(value)
            }
            if attributes:
                doc += "#### Attributes\n\n"
                for attr, value in sorted(attributes.items()):
                    doc += f"- `{attr}`"
                    if hasattr(value, "__doc__") and value.__doc__:
                        doc += f": {inspect.getdoc(value)}"
                    doc += "\n"
                doc += "\n"

            # Class methods
            methods = {
                attr: value
                for attr, value in cls.__dict__.items()
                if not attr.startswith("_")
                and (inspect.isfunction(value) or inspect.ismethod(value))
            }
            if methods:
                doc += "#### Methods\n\n"
                for method_name, method in sorted(methods.items()):
                    signature = inspect.signature(method)
                    doc += f"- `{method_name}{signature}`\n"
                    if method.__doc__:
                        doc += f"  {inspect.getdoc(method)}\n"
                doc += "\n"

    # Process functions
    functions = {name: obj for name, obj in members.items() if inspect.isfunction(obj)}
    if functions:
        doc += "## Functions\n\n"
        for name, func in sorted(functions.items()):
            signature = inspect.signature(func)
            doc += f"### `{name}{signature}`\n\n"
            if func.__doc__:
                doc += f"{inspect.getdoc(func)}\n\n"

    # Process variables
    variables = {
        name: obj
        for name, obj in members.items()
        if not inspect.ismodule(obj) and not inspect.isclass(obj) and not inspect.isfunction(obj)
    }
    if variables:
        doc += "## Variables\n\n"
        for name, var in sorted(variables.items()):
            doc += f"- `{name}`"
            if hasattr(var, "__doc__") and var.__doc__:
                doc += f": {inspect.getdoc(var)}"
            else:
                doc += f": `{type(var).__name__}`"
            doc += "\n"
        doc += "\n"

    return doc


def generate_package_index(modules: list[str]) -> str:
    """Generate an index of all modules."""
    doc = f"# {PACKAGE_NAME} API Reference\n\n"
    doc += "This section provides detailed API documentation for all modules in the package.\n\n"

    # Organize modules by hierarchy
    module_tree = {}
    for module in modules:
        parts = module.split(".")
        current = module_tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]

    # Generate tree structure for top-level
    doc += "## Modules\n\n"

    # Group modules by prefix (e.g., cli, common_utils, etc.)
    prefixes = {}
    for module in modules:
        if module.count(".") == 0:
            continue  # Skip the base package

        prefix = module.split(".")[1]  # First component after the package name
        if prefix not in prefixes:
            prefixes[prefix] = []
        prefixes[prefix].append(module)

    # Generate documentation links for each group
    for prefix, submodules in sorted(prefixes.items()):
        doc += f"### {prefix}\n\n"

        for module in sorted(submodules):
            module_name = module.split(".")[-1]
            relative_path = module.replace(PACKAGE_NAME + ".", "").replace(".", "/")
            doc += f"- [{module_name}]({relative_path}.md)\n"

        doc += "\n"

    return doc


def main():
    """Main entry point for the script."""
    print(f"Generating API documentation for {PACKAGE_NAME}...")

    # Find all modules in the package
    modules = find_modules(PACKAGE_NAME)
    if not modules:
        print(f"No modules found in {PACKAGE_NAME}")
        return

    print(f"Found {len(modules)} modules")

    # Generate the index file
    index_path = OUTPUT_DIR / "python_api.md"
    with open(index_path, "w") as f:
        f.write(generate_package_index(modules))

    print(f"Generated API index at {index_path}")

    # Generate documentation for each module
    for module in modules:
        # Create output directory
        rel_path = module.replace(PACKAGE_NAME + ".", "").replace(".", "/")
        output_path = OUTPUT_DIR / f"{rel_path}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate and write documentation
        with open(output_path, "w") as f:
            f.write(generate_module_doc(module))

        print(f"Generated documentation for {module} at {output_path}")

    print("Documentation generation complete!")


if __name__ == "__main__":
    main()
