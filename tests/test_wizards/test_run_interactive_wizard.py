#!/usr/bin/env python3
"""
Unit tests for the interactive wizard runner script.

These tests validate the functionality of the script that checks for dependencies
and launches the interactive wizard.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the scripts directory to the path to import the runner module
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.append(str(SCRIPT_DIR))

# Import the runner module
import run_interactive_wizard

# Tests for dependency checking


def test_check_dependency_found():
    """Test checking for a dependency that exists."""
    # Use a module that definitely exists
    result = run_interactive_wizard.check_dependency("sys")
    assert result is True


def test_check_dependency_not_found():
    """Test checking for a dependency that doesn't exist."""
    # Use a module that definitely doesn't exist
    result = run_interactive_wizard.check_dependency("nonexistent_module_12345")
    assert result is False


# Tests for package installation


def test_install_package_success():
    """Test successful package installation."""
    # Mock subprocess.check_call to simulate successful installation
    with patch("subprocess.check_call") as mock_check_call:
        mock_check_call.return_value = 0
        result = run_interactive_wizard.install_package("test-package")

    assert result is True
    mock_check_call.assert_called_once()
    # Verify that pip install was called with the package name
    args, _ = mock_check_call.call_args
    assert "install" in args[0]
    assert "test-package" in args[0]


def test_install_package_failure():
    """Test failed package installation."""
    # Mock subprocess.check_call to simulate failed installation
    with patch("subprocess.check_call") as mock_check_call:
        mock_check_call.side_effect = Exception("Installation failed")
        result = run_interactive_wizard.install_package("test-package")

    assert result is False


# Tests for argument parsing


def test_parse_arguments_default():
    """Test parsing command line arguments with defaults."""
    # Mock sys.argv to simulate command line arguments
    with patch("sys.argv", ["run_interactive_wizard.py"]):
        args = run_interactive_wizard.parse_arguments()

    assert args.no_install is False


def test_parse_arguments_no_install():
    """Test parsing command line arguments with --no-install."""
    # Mock sys.argv to simulate command line arguments
    with patch("sys.argv", ["run_interactive_wizard.py", "--no-install"]):
        args = run_interactive_wizard.parse_arguments()

    assert args.no_install is True


# Tests for the main function


def test_main_all_dependencies_present():
    """Test main function when all dependencies are present."""
    # Mock dependency checking and wizard import
    with (
        patch("run_interactive_wizard.check_dependency", return_value=True),
        patch("run_interactive_wizard.importlib.import_module") as mock_import,
        patch("sys.argv", ["run_interactive_wizard.py"]),
    ):
        # Mock the imported wizard module
        mock_wizard = MagicMock()
        mock_import.return_value = mock_wizard

        # Run the main function
        run_interactive_wizard.main()

        # Verify that the wizard's main function was called
        assert mock_wizard.main.called


def test_main_missing_rich_dependency():
    """Test main function when the rich dependency is missing."""

    # Mock dependency checking to return False for rich, True for yaml
    def mock_check_dependency(package):
        return package != "rich"

    # Mock arguments, installation, and wizard import
    with (
        patch("run_interactive_wizard.check_dependency", side_effect=mock_check_dependency),
        patch("run_interactive_wizard.install_package", return_value=True) as mock_install,
        patch("run_interactive_wizard.importlib.import_module") as mock_import,
        patch("sys.argv", ["run_interactive_wizard.py"]),
    ):
        # Mock the imported wizard module
        mock_wizard = MagicMock()
        mock_import.return_value = mock_wizard

        # Run the main function
        run_interactive_wizard.main()

        # Verify that install_package was called for rich
        mock_install.assert_called_with("rich")

        # Verify that the wizard's main function was called
        assert mock_wizard.main.called


def test_main_missing_yaml_dependency():
    """Test main function when the yaml dependency is missing."""

    # Mock dependency checking to return False for yaml, True for rich
    def mock_check_dependency(package):
        return package != "yaml"

    # Mock arguments, installation, and wizard import
    with (
        patch("run_interactive_wizard.check_dependency", side_effect=mock_check_dependency),
        patch("run_interactive_wizard.install_package", return_value=True) as mock_install,
        patch("run_interactive_wizard.importlib.import_module") as mock_import,
        patch("sys.argv", ["run_interactive_wizard.py"]),
    ):
        # Mock the imported wizard module
        mock_wizard = MagicMock()
        mock_import.return_value = mock_wizard

        # Run the main function
        run_interactive_wizard.main()

        # Verify that install_package was called for PyYAML
        mock_install.assert_called_with("PyYAML")

        # Verify that the wizard's main function was called
        assert mock_wizard.main.called


def test_main_failed_installation_rich():
    """Test main function when rich installation fails."""

    # Mock dependency checking to return False for rich
    def mock_check_dependency(package):
        return package != "rich"

    # Mock installation to fail for rich
    def mock_install_package(package):
        return package != "rich"

    # Mock arguments, installation, and wizard import
    with (
        patch("run_interactive_wizard.check_dependency", side_effect=mock_check_dependency),
        patch("run_interactive_wizard.install_package", side_effect=mock_install_package),
        patch("run_interactive_wizard.importlib.import_module") as mock_import,
        patch("sys.stdout") as mock_stdout,
        patch("sys.argv", ["run_interactive_wizard.py"]),
    ):
        # Mock the imported wizard module
        mock_wizard = MagicMock()
        mock_import.return_value = mock_wizard

        # Run the main function
        run_interactive_wizard.main()

        # Verify that the wizard's main function was called despite failing to install rich
        assert mock_wizard.main.called


def test_main_failed_installation_yaml():
    """Test main function when PyYAML installation fails."""

    # Mock dependency checking to return False for yaml
    def mock_check_dependency(package):
        return package != "yaml"

    # Mock installation to fail for PyYAML
    def mock_install_package(package):
        return package != "PyYAML"

    # Mock arguments, installation, and wizard import
    with (
        patch("run_interactive_wizard.check_dependency", side_effect=mock_check_dependency),
        patch("run_interactive_wizard.install_package", side_effect=mock_install_package),
        patch("run_interactive_wizard.importlib.import_module") as mock_import,
        patch("sys.stdout"),
        patch("sys.exit") as mock_exit,
        patch("sys.argv", ["run_interactive_wizard.py"]),
    ):
        # Run the main function
        run_interactive_wizard.main()

        # Verify that sys.exit was called because PyYAML is required
        mock_exit.assert_called_once_with(1)


def test_main_wizard_import_error():
    """Test main function when there's an error importing the wizard."""
    # Mock dependency checking and wizard import
    with (
        patch("run_interactive_wizard.check_dependency", return_value=True),
        patch(
            "run_interactive_wizard.importlib.import_module",
            side_effect=ImportError("Module not found"),
        ),
        patch("sys.stdout"),
        patch("sys.exit") as mock_exit,
        patch("sys.argv", ["run_interactive_wizard.py"]),
    ):
        # Run the main function
        run_interactive_wizard.main()

        # Verify that sys.exit was called with error code 1
        mock_exit.assert_called_once_with(1)


def test_main_wizard_runtime_error():
    """Test main function when there's a runtime error in the wizard."""
    # Mock dependency checking and wizard import
    with (
        patch("run_interactive_wizard.check_dependency", return_value=True),
        patch("run_interactive_wizard.importlib.import_module") as mock_import,
        patch("sys.stdout"),
        patch("sys.exit") as mock_exit,
        patch("sys.argv", ["run_interactive_wizard.py"]),
    ):
        # Mock the imported wizard module to raise an exception when main is called
        mock_wizard = MagicMock()
        mock_wizard.main.side_effect = Exception("Runtime error")
        mock_import.return_value = mock_wizard

        # Run the main function
        run_interactive_wizard.main()

        # Verify that sys.exit was called with error code 1
        mock_exit.assert_called_once_with(1)


def test_main_with_no_install_flag():
    """Test main function with --no-install flag when dependencies are missing."""

    # Mock dependency checking to return False for rich
    def mock_check_dependency(package):
        return package != "rich"

    # Mock arguments, installation, and wizard import
    with (
        patch("run_interactive_wizard.check_dependency", side_effect=mock_check_dependency),
        patch("run_interactive_wizard.install_package") as mock_install,
        patch("run_interactive_wizard.importlib.import_module") as mock_import,
        patch("sys.argv", ["run_interactive_wizard.py", "--no-install"]),
    ):
        # Mock the imported wizard module
        mock_wizard = MagicMock()
        mock_import.return_value = mock_wizard

        # Run the main function
        run_interactive_wizard.main()

        # Verify that install_package was not called
        mock_install.assert_not_called()

        # Verify that the wizard's main function was called
        assert mock_wizard.main.called
