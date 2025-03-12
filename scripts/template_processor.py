#!/usr/bin/env python3
"""
Template Processor for Python & Terraform Template

This module handles the processing of the template manifest and provides
utilities for component management, template variable substitution, and
template updates.

The TemplateProcessor class processes a template manifest file (YAML format)
and implements the logic to:
1. Process project components based on user configuration
2. Resolve component dependencies automatically
3. Substitute template variables in files
4. Remove unused components and files
5. Generate dependency graphs and other visualizations

Example usage:
    ```python
    from template_processor import TemplateProcessor

    # Initialize the processor with the manifest file
    processor = TemplateProcessor("template_manifest.yml")

    # Configuration from the user
    config = {
        "project_name": "my-project",
        "package_name": "my_package",
        "components": {
            "aws": True,
            "terraform": True,
            "documentation": True,
        },
    }

    # Process the template with the configuration
    processor.process_template(config)
    ```
"""

import os
import re
import shutil
from pathlib import Path
from typing import Any, Optional, Union

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class TemplateProcessor:
    """
    Process the template based on manifest and configuration.

    This class is responsible for reading the template manifest,
    processing components, resolving dependencies, and handling
    template variables.

    Attributes:
        manifest_path (Path): Path to the template manifest file
        verbose (bool): Whether to print verbose output
        manifest (dict): The loaded manifest data
        project_root (Path): The root directory of the project
        enabled_components (list): List of enabled component names
    """

    def __init__(self, manifest_path: Union[str, Path], verbose: bool = False):
        """Initialize the template processor with the manifest file.

        Args:
            manifest_path: Path to the template manifest file (YAML format)
            verbose: Whether to print verbose output during processing

        Raises:
            FileNotFoundError: If the manifest file does not exist
            ImportError: If PyYAML is not installed
            ValueError: If the manifest file cannot be parsed

        Example:
            ```python
            processor = TemplateProcessor("template_manifest.yml", verbose=True)
            ```
        """
        self.manifest_path = Path(manifest_path)
        self.verbose = verbose
        self.manifest = self._load_manifest()
        self.project_root = Path(self.manifest_path).parent
        self.enabled_components: list[str] = []

    def _load_manifest(self) -> dict[str, Any]:
        """Load the template manifest file.

        Reads and parses the YAML manifest file, which defines the
        structure of the template.

        Returns:
            The parsed manifest data as a dictionary

        Raises:
            FileNotFoundError: If the manifest file does not exist
            ImportError: If PyYAML is not installed
            ValueError: If the manifest file cannot be parsed
        """
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {self.manifest_path}")

        if not YAML_AVAILABLE:
            raise ImportError("YAML support requires PyYAML. Install with: pip install pyyaml")

        try:
            with open(self.manifest_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Error loading manifest file: {e}")

    def process_template(self, config: dict[str, Any]) -> bool:
        """Process the template based on the manifest and configuration.

        This is the main entry point for template processing. It handles
        component selection, dependency resolution, variable substitution,
        and cleanup of unused components.

        Args:
            config: User configuration dictionary containing project metadata
                   and component selections

        Returns:
            bool: True if processing was successful, False otherwise

        Example:
            ```python
            config = {
                "project_name": "my-project",
                "package_name": "my_package",
                "components": {
                    "aws": True,
                    "terraform": True,
                    "documentation": True,
                },
            }
            success = processor.process_template(config)
            ```
        """
        try:
            # Step 1: Resolve component dependencies and determine enabled components
            self.enabled_components = self.resolve_dependencies(config)

            if self.verbose:
                print(f"Enabled components: {', '.join(self.enabled_components)}")

            # Step 2: Process template variables in files
            self.process_variables(config)

            # Step 3: Clean up unused components
            self.cleanup_unused_components(config)

            return True
        except Exception as e:
            if self.verbose:
                print(f"Error processing template: {e}")
            return False

    def get_component_by_name(self, name: str) -> Optional[dict[str, Any]]:
        """Get a component from the manifest by name.

        Args:
            name: Name of the component to retrieve

        Returns:
            The component dictionary, or None if not found
        """
        for component in self.manifest.get("components", []):
            if component.get("name") == name:
                return component
        return None

    def resolve_dependencies(self, config: dict[str, Any]) -> list[str]:
        """Resolve component dependencies based on configuration.

        This method determines which components should be enabled based on
        user selection and dependencies between components.

        Args:
            config: User configuration dictionary

        Returns:
            List of enabled component names after dependency resolution

        Example:
            ```python
            enabled_components = processor.resolve_dependencies(config)
            ```
        """
        # Start with an empty set of enabled components
        enabled: set[str] = set()

        # Add all required components
        for component in self.manifest.get("components", []):
            if component.get("required", False):
                enabled.add(component["name"])

        # Add user-selected components
        user_components = config.get("components", {})
        for name, is_enabled in user_components.items():
            if is_enabled:
                enabled.add(name)

        # Resolve dependencies recursively
        dependencies_added = True
        while dependencies_added:
            dependencies_added = False
            for name in list(enabled):
                component = self.get_component_by_name(name)
                if component and "dependencies" in component:
                    for dep in component["dependencies"]:
                        if dep not in enabled:
                            enabled.add(dep)
                            dependencies_added = True
                            if self.verbose:
                                print(f"Added dependency {dep} for component {name}")

        return list(enabled)

    def process_variables(self, config: dict[str, Any]) -> None:
        """Process template variables in files.

        Substitutes template variables in files with values from config.

        Args:
            config: User configuration dictionary

        Example:
            ```python
            processor.process_variables(config)
            ```
        """
        variables = self.manifest.get("variables", [])
        for variable in variables:
            var_name = variable["name"]
            var_value = config.get(var_name.lower(), variable.get("default", ""))

            # Skip empty values
            if not var_value:
                continue

            # Process each file that contains this variable
            for file_pattern in variable.get("files", []):
                for file_path in self.project_root.glob(file_pattern):
                    if not file_path.is_file():
                        continue

                    if self.verbose:
                        print(f"Processing variables in {file_path}")

                    # Read file content
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()
                    except Exception as e:
                        if self.verbose:
                            print(f"Error reading file {file_path}: {e}")
                        continue

                    # Replace Jinja-style variables: {{ VARIABLE_NAME }}
                    pattern_jinja = r"{{\s*" + var_name + r"\s*}}"
                    content = re.sub(pattern_jinja, str(var_value), content)

                    # Replace placeholder style variables: ___VARIABLE_NAME___
                    pattern_placeholder = r"___" + var_name + r"___"
                    content = re.sub(pattern_placeholder, str(var_value), content)

                    # Write updated content
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                    except Exception as e:
                        if self.verbose:
                            print(f"Error writing file {file_path}: {e}")

    def get_files_for_component(self, component_name: str) -> list[Path]:
        """Get list of files associated with a component.

        Args:
            component_name: Name of the component

        Returns:
            List of file paths associated with the component
        """
        component = self.get_component_by_name(component_name)
        if not component:
            return []

        files: list[Path] = []
        for pattern in component.get("files", []):
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    files.append(file_path)

        return files

    def cleanup_unused_components(self, config: dict[str, Any]) -> None:
        """Remove files for disabled components.

        Args:
            config: User configuration dictionary
        """
        # Determine which components are not enabled
        all_components = [comp["name"] for comp in self.manifest.get("components", [])]
        disabled_components = [
            name for name in all_components if name not in self.enabled_components
        ]

        if not disabled_components:
            return

        if self.verbose:
            print(f"Cleaning up disabled components: {', '.join(disabled_components)}")

        # Collect files to remove
        files_to_remove: list[Path] = []
        for component_name in disabled_components:
            component_files = self.get_files_for_component(component_name)
            files_to_remove.extend(component_files)

        # Remove files
        for file_path in files_to_remove:
            if self.verbose:
                print(f"Removing file: {file_path}")

            try:
                if file_path.is_file():
                    os.remove(file_path)
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
            except Exception as e:
                if self.verbose:
                    print(f"Error removing {file_path}: {e}")

    def generate_dependency_graph(self, output_file: Optional[str] = None) -> str:
        """Generate a dependency graph of components.

        Args:
            output_file: Optional file path to save the graph (as DOT or PNG)

        Returns:
            DOT format representation of the dependency graph
        """
        try:
            import graphviz

            has_graphviz = True
        except ImportError:
            has_graphviz = False

        # Build the graph representation
        dot_lines = ["digraph ComponentDependencies {"]
        dot_lines.append("  node [shape=box, style=filled, fillcolor=lightblue];")

        # Add nodes for all components
        for component in self.manifest.get("components", []):
            name = component["name"]
            label = f"{name}\\n{component.get('description', '')}"
            required = component.get("required", False)

            # Use different styling for required components
            if required:
                dot_lines.append(f'  "{name}" [label="{label}", fillcolor=lightgreen];')
            else:
                dot_lines.append(f'  "{name}" [label="{label}"];')

        # Add edges for dependencies
        for component in self.manifest.get("components", []):
            name = component["name"]
            for dep in component.get("dependencies", []):
                dot_lines.append(f'  "{dep}" -> "{name}";')

        dot_lines.append("}")
        dot_content = "\n".join(dot_lines)

        # Save to file if requested
        if output_file and has_graphviz:
            g = graphviz.Source(dot_content)
            g.render(output_file, format="png", cleanup=True)

        return dot_content

    def generate_component_graph(self) -> dict[str, Any]:
        """Generate a graph representation of component dependencies.

        Creates a graph structure showing components as nodes and
        dependencies as edges. This can be used to visualize the
        component relationships.

        Returns:
            A dictionary with "nodes" and "edges" keys representing the graph

        Example:
            ```python
            graph = processor.generate_component_graph()

            # Graph structure
            {
                "nodes": [
                    {"id": "core", "label": "core", "required": true},
                    {"id": "terraform", "label": "terraform", "required": false},
                ],
                "edges": [{"from": "data_pipelines", "to": "aws", "label": "requires"}],
            }
            ```

        Note:
            This graph can be visualized using libraries like D3.js or
            networkx + matplotlib in Python.
        """
        components = self.manifest.get("components", [])
        graph = {"nodes": [], "edges": []}

        # Add nodes for each component
        for component in components:
            name = component.get("name")
            graph["nodes"].append(
                {
                    "id": name,
                    "label": name,
                    "description": component.get("description", ""),
                    "required": component.get("required", False),
                }
            )

            # Add edges for dependencies
            for dependency in component.get("dependencies", []):
                graph["edges"].append({"from": name, "to": dependency, "label": "requires"})

        return graph

    def get_component_info(self, component_name: str) -> Optional[dict[str, Any]]:
        """Get information about a specific component.

        Retrieves the full definition of a component from the manifest.

        Args:
            component_name: Name of the component to retrieve

        Returns:
            Component definition dictionary or None if not found

        Example:
            ```python
            terraform_info = processor.get_component_info("terraform")
            print(terraform_info["description"])  # "Terraform infrastructure as code"
            ```
        """
        components = self.manifest.get("components", [])
        for component in components:
            if component.get("name") == component_name:
                return component
        return None

    def list_components(self) -> list[dict[str, Any]]:
        """List all available components.

        Returns:
            List of all component definitions from the manifest

        Example:
            ```python
            components = processor.list_components()
            for component in components:
                print(f"{component['name']}: {component['description']}")
            ```
        """
        return self.manifest.get("components", [])

    def get_template_info(self) -> dict[str, Any]:
        """Get template metadata.

        Returns:
            Dictionary containing template name, version, and description

        Example:
            ```python
            info = processor.get_template_info()
            print(f"Template: {info['name']} v{info['version']}")
            ```
        """
        return self.manifest.get("template", {})


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Template Processor Utility")
    parser.add_argument(
        "--manifest", default="template_manifest.yml", help="Path to template manifest"
    )
    parser.add_argument("--info", action="store_true", help="Show template information")
    parser.add_argument("--list-components", action="store_true", help="List available components")
    parser.add_argument("--component", help="Show information about a specific component")
    parser.add_argument("--graph", action="store_true", help="Generate component dependency graph")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")

    args = parser.parse_args()

    try:
        processor = TemplateProcessor(args.manifest, verbose=args.verbose)

        if args.info:
            info = processor.get_template_info()
            print(f"Template: {info.get('name')}")
            print(f"Version: {info.get('version')}")
            print(f"Description: {info.get('description')}")

        if args.list_components:
            print("\nAvailable Components:")
            for component in processor.list_components():
                name = component.get("name")
                required = " (required)" if component.get("required", False) else ""
                print(f"- {name}{required}: {component.get('description', '')}")

        if args.component:
            component = processor.get_component_info(args.component)
            if component:
                print(f"\nComponent: {component.get('name')}")
                print(f"Description: {component.get('description', '')}")
                print(f"Required: {component.get('required', False)}")
                print("\nFiles:")
                for file in component.get("files", []):
                    print(f"- {file}")
                if component.get("dependencies"):
                    print("\nDependencies:")
                    for dep in component.get("dependencies", []):
                        print(f"- {dep}")
            else:
                print(f"Component not found: {args.component}")

        if args.graph:
            graph = processor.generate_component_graph()
            print(json.dumps(graph, indent=2))

    except Exception as e:
        print(f"Error: {e}")
