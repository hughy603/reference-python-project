#!/usr/bin/env python3
"""
Tests for the TemplateProcessor class.

This module contains unit tests for the template processor functionality
which is used during project initialization to process template components
and variables.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest
import yaml

# Add the scripts directory to the path to import the module
sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))
from template_processor import TemplateProcessor


@pytest.fixture
def sample_manifest():
    """Create a sample manifest dictionary for testing."""
    return {
        "template": {
            "name": "Test Template",
            "version": "1.0.0",
            "description": "A test template manifest",
        },
        "components": [
            {
                "name": "core",
                "description": "Core components",
                "required": True,
                "files": ["src/*", "tests/*", "pyproject.toml"],
            },
            {
                "name": "aws",
                "description": "AWS components",
                "required": False,
                "files": ["src/*/aws/*"],
                "dependencies": [],
            },
            {
                "name": "terraform",
                "description": "Terraform components",
                "required": False,
                "files": ["infrastructure/terraform/*"],
                "dependencies": [],
            },
            {
                "name": "api",
                "description": "API components",
                "required": False,
                "files": ["src/*/api/*"],
                "dependencies": ["aws"],
            },
        ],
        "variables": [
            {
                "name": "PROJECT_NAME",
                "description": "Name of the project",
                "default": "test-project",
                "files": ["README.md", "pyproject.toml"],
            },
            {
                "name": "PACKAGE_NAME",
                "description": "Python package name",
                "default": "test_package",
                "files": ["src/*/__init__.py"],
            },
        ],
    }


@pytest.fixture
def temp_manifest_file(sample_manifest):
    """Create a temporary manifest file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as temp_file:
        yaml.dump(sample_manifest, temp_file)
        temp_path = temp_file.name

    yield temp_path

    # Clean up the temp file
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_project_structure():
    """Create a mock project structure for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create directory structure
        path = Path(temp_dir)
        (path / "src").mkdir()
        (path / "tests").mkdir()
        (path / "infrastructure" / "terraform").mkdir(parents=True)
        (path / "src" / "test_package").mkdir()
        (path / "src" / "test_package" / "aws").mkdir()
        (path / "src" / "test_package" / "api").mkdir()

        # Create some test files
        (path / "README.md").write_text("# Project: {{ PROJECT_NAME }}")
        (path / "pyproject.toml").write_text('[project]\nname = "{{ PROJECT_NAME }}"')
        (path / "src" / "test_package" / "__init__.py").write_text(
            '"""{{ PACKAGE_NAME }} package."""'
        )

        # Create files for aws component
        aws_file = path / "src" / "test_package" / "aws" / "utils.py"
        aws_file.write_text('"""AWS utilities."""')

        yield path


class TestTemplateProcessor:
    """Tests for the TemplateProcessor class."""

    def test_init_with_valid_manifest(self, temp_manifest_file):
        """Test initializing with a valid manifest file."""
        processor = TemplateProcessor(temp_manifest_file)
        assert processor.manifest is not None
        assert processor.manifest["template"]["name"] == "Test Template"

    def test_load_manifest_file_not_found(self):
        """Test loading a non-existent manifest file."""
        with pytest.raises(FileNotFoundError):
            TemplateProcessor("non_existent_file.yml")

    def test_get_component_by_name(self, temp_manifest_file):
        """Test retrieving a component by name."""
        processor = TemplateProcessor(temp_manifest_file)
        component = processor.get_component_by_name("aws")
        assert component is not None
        assert component["name"] == "aws"
        assert component["description"] == "AWS components"

    def test_get_nonexistent_component(self, temp_manifest_file):
        """Test retrieving a non-existent component."""
        processor = TemplateProcessor(temp_manifest_file)
        component = processor.get_component_by_name("nonexistent")
        assert component is None

    def test_resolve_dependencies(self, temp_manifest_file):
        """Test resolving component dependencies."""
        processor = TemplateProcessor(temp_manifest_file)
        config = {"components": {"api": True}}
        enabled_components = processor.resolve_dependencies(config)
        assert "api" in enabled_components
        assert "aws" in enabled_components  # aws is a dependency of api

    def test_process_variables(self, temp_manifest_file, mock_project_structure):
        """Test processing template variables in files."""
        processor = TemplateProcessor(temp_manifest_file)
        config = {
            "project_name": "custom-project",
            "package_name": "custom_package",
        }

        with mock.patch.object(processor, "project_root", mock_project_structure):
            processor.process_variables(config)

            # Check if files were properly updated
            readme_content = (mock_project_structure / "README.md").read_text()
            assert "# Project: custom-project" in readme_content

            pyproject_content = (mock_project_structure / "pyproject.toml").read_text()
            assert 'name = "custom-project"' in pyproject_content

    def test_get_files_for_component(self, temp_manifest_file, mock_project_structure):
        """Test getting files for a specific component."""
        processor = TemplateProcessor(temp_manifest_file)

        with mock.patch.object(processor, "project_root", mock_project_structure):
            # Create additional test files for this specific test
            aws_dir = mock_project_structure / "src" / "test_package" / "aws"
            test_file = aws_dir / "test_file.py"
            test_file.write_text("# Test AWS file")

            files = processor.get_files_for_component("aws")
            # Check that at least one file with "aws" in the path is found
            assert any("aws" in str(f) for f in files), f"No AWS files found in: {files}"

    def test_process_template(self, temp_manifest_file, mock_project_structure):
        """Test the full template processing workflow."""
        processor = TemplateProcessor(temp_manifest_file)
        config = {
            "project_name": "custom-project",
            "package_name": "custom_package",
            "components": {
                "core": True,
                "aws": True,
                "terraform": False,
                "api": False,
            },
        }

        with mock.patch.object(processor, "project_root", mock_project_structure):
            # Mock the methods that would perform file operations
            with (
                mock.patch.object(processor, "process_variables"),
                mock.patch.object(processor, "cleanup_unused_components"),
            ):
                result = processor.process_template(config)
                assert result is True

                # Verify that the right components were enabled
                # Note: order doesn't matter, so use set comparison
                assert set(processor.enabled_components) == {"core", "aws"}
