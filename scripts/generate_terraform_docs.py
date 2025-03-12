#!/usr/bin/env python
"""
Script to generate documentation for Terraform modules.

This script uses terraform-docs to generate documentation for each Terraform
module in the infrastructure/terraform directory and compiles them into a single
reference document.
"""

import subprocess
import sys
from pathlib import Path

# Output directory for generated docs
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "reference"
TERRAFORM_ROOT = Path(__file__).parent.parent / "infrastructure" / "terraform"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def check_terraform_docs():
    """Check if terraform-docs is installed."""
    try:
        subprocess.run(
            ["terraform-docs", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: terraform-docs is not installed or not in PATH")
        print("Please install terraform-docs from https://terraform-docs.io/")
        return False


def find_terraform_modules():
    """Find all Terraform modules in the infrastructure directory."""
    if not TERRAFORM_ROOT.exists():
        print(f"Error: Terraform directory {TERRAFORM_ROOT} does not exist")
        return []

    modules = []

    # Look for directories containing *.tf files
    for item in TERRAFORM_ROOT.iterdir():
        if item.is_dir():
            tf_files = list(item.glob("*.tf"))
            if tf_files:
                modules.append(item)

    return modules


def generate_module_doc(module_path: Path) -> str:
    """Generate Markdown documentation for a Terraform module."""
    module_name = module_path.name

    # Run terraform-docs to generate documentation
    try:
        result = subprocess.run(
            ["terraform-docs", "markdown", str(module_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        doc = result.stdout

        # Add module name as title if not present
        if not doc.startswith(f"# {module_name}"):
            doc = f"# {module_name}\n\n{doc}"

        return doc

    except subprocess.CalledProcessError as e:
        print(f"Error generating documentation for {module_name}: {e}")
        print(f"stderr: {e.stderr}")
        return f"# {module_name}\n\nError generating documentation for this module.\n"


def generate_modules_index(modules: list) -> str:
    """Generate an index file for all Terraform modules."""
    doc = "# Terraform Modules Reference\n\n"
    doc += "This section provides documentation for the Terraform modules included in this project.\n\n"
    doc += "## Available Modules\n\n"

    for module in sorted(modules, key=lambda m: m.name):
        module_name = module.name
        doc += f"- [{module_name}](terraform/{module_name}.md)\n"

    return doc


def main():
    """Main entry point for the script."""
    print("Generating Terraform module documentation...")

    # Check terraform-docs is installed
    if not check_terraform_docs():
        sys.exit(1)

    # Find all Terraform modules
    modules = find_terraform_modules()
    if not modules:
        print("No Terraform modules found")
        return

    print(f"Found {len(modules)} Terraform modules")

    # Generate the index file
    index_path = OUTPUT_DIR / "terraform_modules.md"
    with open(index_path, "w") as f:
        f.write(generate_modules_index(modules))

    print(f"Generated modules index at {index_path}")

    # Create terraform subdirectory
    terraform_dir = OUTPUT_DIR / "terraform"
    terraform_dir.mkdir(exist_ok=True)

    # Generate documentation for each module
    for module in modules:
        output_path = terraform_dir / f"{module.name}.md"

        # Generate and write documentation
        with open(output_path, "w") as f:
            f.write(generate_module_doc(module))

        print(f"Generated documentation for {module.name} at {output_path}")

    print("Terraform documentation generation complete!")


if __name__ == "__main__":
    main()
