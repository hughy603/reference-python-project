#!/usr/bin/env python3
"""
Tests for the init_project module.

This module contains unit tests for the project initialization functionality,
which is used to set up new projects from the template.
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
import init_project


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file for testing."""
    config = {
        "project_name": "test-project",
        "package_name": "test_project",
        "description": "A test project",
        "author": "Test Author",
        "email": "test@example.com",
        "organization": "Test Org",
        "version": "0.1.0",
        "components": {
            "aws": True,
            "terraform": True,
            "cloudformation": False,
            "docker": True,
            "documentation": True,
            "testing": True,
            "ci_cd": True,
            "data_pipelines": False,
            "api": False,
            "ml": False,
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as temp_file:
        yaml.dump(config, temp_file)
        temp_path = temp_file.name

    yield temp_path

    # Clean up the temp file
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestConfiguration:
    """Tests for configuration functionality."""

    def test_default_config(self):
        """Test the default configuration."""
        assert isinstance(init_project.DEFAULT_CONFIG, dict)
        assert "project_name" in init_project.DEFAULT_CONFIG
        assert "components" in init_project.DEFAULT_CONFIG

    def test_presets_exist(self):
        """Test that presets are defined."""
        assert isinstance(init_project.PRESETS, dict)
        assert "data_engineering" in init_project.PRESETS
        assert "web_api" in init_project.PRESETS

    def test_load_config_file(self, temp_config_file):
        """Test loading configuration from a file."""
        # Create a minimal ArgumentParser-like object with a required attribute
        args_mock = mock.MagicMock()
        args_mock.config = temp_config_file

        with mock.patch.object(init_project, "print"):  # Suppress print statements
            config = init_project.load_config_file(args_mock)

            assert config["project_name"] == "test-project"
            assert config["package_name"] == "test_project"
            assert config["components"]["aws"] is True
            assert config["components"]["cloudformation"] is False

    def test_load_config_file_not_found(self):
        """Test loading from a non-existent configuration file."""
        args_mock = mock.MagicMock()
        args_mock.config = "non_existent_file.yml"

        with pytest.raises(FileNotFoundError), mock.patch.object(init_project, "print"):
            init_project.load_config_file(args_mock)


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_prompt_for_value(self):
        """Test prompting for a value with a default."""
        with mock.patch("builtins.input", return_value=""):
            # Empty input should return the default
            value = init_project.prompt_for_value("Test", "default")
            assert value == "default"

        with mock.patch("builtins.input", return_value="user input"):
            # User input should be returned
            value = init_project.prompt_for_value("Test", "default")
            assert value == "user input"

    def test_slugify(self):
        """Test converting a string to a slug."""
        assert init_project.slugify("Hello World") == "hello-world"
        assert init_project.slugify("Hello_World") == "hello-world"
        assert init_project.slugify("hello-world") == "hello-world"
        assert init_project.slugify("HELLO WORLD") == "hello-world"
        assert init_project.slugify("Hello World!") == "hello-world"

    def test_snake_case(self):
        """Test converting a string to snake_case."""
        assert init_project.snake_case("Hello World") == "hello_world"
        assert init_project.snake_case("Hello-World") == "hello_world"
        assert init_project.snake_case("hello_world") == "hello_world"
        assert init_project.snake_case("HELLO WORLD") == "hello_world"
        assert init_project.snake_case("Hello World!") == "hello_world"


class TestProjectFunctions:
    """Tests for project initialization functions."""

    @mock.patch("subprocess.run")
    def test_initialize_git(self, mock_run):
        """Test initializing a Git repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            init_project.initialize_git(project_root)

            # Verify git init was called
            git_calls = [call for call in mock_run.call_args_list if "git" in str(call)]
            assert len(git_calls) > 0, "git command was not called"

    @mock.patch("os.rename")
    @mock.patch("os.path.exists", return_value=True)
    def test_rename_packages(self, mock_exists, mock_rename):
        """Test renaming the package directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            src_dir = project_root / "src"
            src_dir.mkdir()

            original_package = src_dir / "reference_python_project"
            original_package.mkdir()

            enterprise_dir = src_dir / "enterprise_data_engineering"
            enterprise_dir.mkdir()

            # Test with package_name parameter
            init_project.rename_packages(project_root, "new_package")

            # Check that both packages would be renamed
            assert mock_rename.call_count == 2

    @mock.patch("subprocess.run")
    def test_setup_venv(self, mock_run):
        """Test setting up a virtual environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # Set a mock for platform.system to return "Linux"
            with mock.patch("platform.system", return_value="Linux"):
                init_project.setup_venv(project_root)

            # Check that the venv creation command was called
            assert mock_run.call_count > 0

    @mock.patch(
        "builtins.open",
        new_callable=mock.mock_open,
        read_data='[project]\nname = "{{ PROJECT_NAME }}"',
    )
    @mock.patch("glob.glob", return_value=["pyproject.toml"])
    def test_substitute_variables(self, mock_glob, mock_open):
        """Test substituting variables in files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "project_name": "test-project",
                "package_name": "test_package",
                "description": "Test description",
                "author": "Test Author",
                "email": "test@example.com",
                "version": "0.1.0",
            }

            init_project.substitute_variables(Path(temp_dir), config)

            # Check that the file was opened for reading and writing
            assert mock_open.call_count >= 2

            # Verify that the correct content was written
            handle = mock_open()
            handle.write.assert_called()


class TestEndToEnd:
    """End-to-end tests for project initialization."""

    @mock.patch("init_project.initialize_git")
    @mock.patch("init_project.setup_venv")
    @mock.patch("init_project.rename_packages")
    @mock.patch("init_project.substitute_variables")
    @mock.patch("init_project.TemplateProcessor")
    def test_initialize_project_with_config(
        self, mock_processor_class, mock_substitute, mock_rename, mock_setup_venv, mock_git
    ):
        """Test initializing a project with a configuration file."""
        # Set up a mock for the processor
        mock_processor = mock.MagicMock()
        mock_processor.process_template.return_value = True
        mock_processor_class.return_value = mock_processor

        # Create a temp config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml") as config_file:
            # Write a minimal configuration
            config = {
                "project_name": "test-project",
                "package_name": "test_package",
                "components": {"aws": True, "terraform": True},
            }
            yaml.dump(config, config_file)
            config_file.flush()

            # Create mock args
            args = mock.MagicMock()
            args.config = config_file.name
            args.non_interactive = True
            args.skip_env = False
            args.keep_git = False

            # Call initialize_project
            with mock.patch.object(init_project, "print"):  # Suppress prints
                result = init_project.initialize_project_with_config(args)

                # Check that the initialization was successful
                assert result is True

                # Verify that the key functions were called
                mock_processor_class.assert_called_once()
                mock_processor.process_template.assert_called_once()
                mock_substitute.assert_called_once()
                mock_rename.assert_called_once()
                mock_setup_venv.assert_called_once()
                mock_git.assert_called_once()
