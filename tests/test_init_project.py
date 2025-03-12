import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

# Add the scripts directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from init_project import (
    initialize_project_with_config,
    load_config_file,
)


class TestInitProject(unittest.TestCase):
    """Test cases for the project initialization script."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            "project_name": "test-project",
            "package_name": "test_project",
            "description": "A test project",
            "author": "Test Author",
            "email": "test@example.com",
            "version": "0.1.0",
        }

        # Create a mock args object
        self.args = MagicMock()
        self.args.config = None
        self.args.verbose = False
        self.args.skip_env = True
        self.args.keep_git = True

    @patch("init_project.load_config_file")
    @patch("init_project.rename_packages")
    @patch("init_project.initialize_git")
    @patch("init_project.print_success")
    def test_initialize_project_with_default_config(
        self, mock_print_success, mock_initialize_git, mock_rename_packages, mock_load_config
    ):
        """Test project initialization with default configuration."""
        # Configure mocks
        mock_load_config.return_value = self.test_config

        # Call the function
        result = initialize_project_with_config(self.args)

        # Assertions
        self.assertTrue(result)
        mock_print_success.assert_called_once_with("Project initialization complete!")

        # Since keep_git is True, initialize_git should not be called
        mock_initialize_git.assert_not_called()

        # rename_packages should be called with the package name from the config
        mock_rename_packages.assert_called_once()

    @patch("init_project.load_config_file")
    @patch("init_project.rename_packages")
    @patch("init_project.initialize_git")
    @patch("init_project.print_success")
    @patch("init_project.print_error")
    def test_initialize_project_with_custom_config(
        self,
        mock_print_error,
        mock_print_success,
        mock_initialize_git,
        mock_rename_packages,
        mock_load_config,
    ):
        """Test project initialization with custom configuration."""
        # Configure mocks
        mock_load_config.return_value = self.test_config
        self.args.config = "custom_config.yml"
        self.args.keep_git = False

        # Call the function
        result = initialize_project_with_config(self.args)

        # Assertions
        self.assertTrue(result)
        mock_print_success.assert_called_once_with("Project initialization complete!")

        # Since keep_git is False, initialize_git should be called
        mock_initialize_git.assert_called_once()

        # rename_packages should be called with the package name from the config
        mock_rename_packages.assert_called_once()

        # Error print should not be called
        mock_print_error.assert_not_called()

    @patch("init_project.load_config_file")
    @patch("init_project.print_error")
    def test_initialize_project_with_exception(self, mock_print_error, mock_load_config):
        """Test project initialization with an exception."""
        # Configure mocks to raise an exception
        mock_load_config.side_effect = Exception("Test exception")

        # Call the function
        result = initialize_project_with_config(self.args)

        # Assertions
        self.assertFalse(result)
        mock_print_error.assert_called_once_with("Project initialization failed: Test exception")

    @patch("builtins.open", new_callable=mock_open, read_data='{"project_name": "test-project"}')
    def test_load_config_file_json(self, mock_file):
        """Test loading a JSON configuration file."""
        config = load_config_file("test_config.json")
        self.assertEqual(config["project_name"], "test-project")
        mock_file.assert_called_once_with("test_config.json", "r", encoding="utf-8")

    @patch("yaml.safe_load")
    @patch("builtins.open", new_callable=mock_open, read_data="project_name: test-project")
    def test_load_config_file_yaml(self, mock_file, mock_yaml_load):
        """Test loading a YAML configuration file."""
        mock_yaml_load.return_value = {"project_name": "test-project"}
        config = load_config_file("test_config.yml")
        self.assertEqual(config["project_name"], "test-project")
        mock_file.assert_called_once_with("test_config.yml", "r", encoding="utf-8")
        mock_yaml_load.assert_called_once()


if __name__ == "__main__":
    unittest.main()
