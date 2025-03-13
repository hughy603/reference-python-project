"""
Unit tests for the CLI module.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

from enterprise_data_engineering.cli import (
    app,
    build_docs,
    callback,
    data_app,
    dev_app,
    dev_setup,
    docs_app,
    info,
    run_lint,
    run_tests,
    serve_docs,
    validate_pipeline,
)


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing the Typer app."""
    return CliRunner()


def test_callback():
    """Test the callback function does not raise exceptions."""
    # This function doesn't do anything, but we test it for coverage
    callback()


@patch("enterprise_data_engineering.cli.console.print")
@patch("enterprise_data_engineering.cli.Table")
@patch("enterprise_data_engineering.cli.sys")
@patch("enterprise_data_engineering.cli.os")
def test_info(mock_os, mock_sys, mock_table, mock_print):
    """Test the info command displays environment information."""
    # Setup mocks
    mock_table_instance = mock_table.return_value
    mock_os.getcwd.return_value = "/test/path"
    mock_os.environ = {"PYTHONPATH": "/test/pythonpath", "VIRTUAL_ENV": "/test/venv"}
    mock_sys.version = "3.11.0 (main, Oct 24 2022, 18:26:48) [GCC 11.2.0]"

    # Call the function
    info()

    # Assertions
    assert mock_table.called
    assert mock_table_instance.add_column.call_count == 2
    assert mock_table_instance.add_row.call_count >= 4
    assert mock_print.called


@patch("enterprise_data_engineering.cli.subprocess.run")
@patch("enterprise_data_engineering.cli.rprint")
@patch("enterprise_data_engineering.cli.console")
def test_dev_setup(mock_console, mock_rprint, mock_subprocess_run):
    """Test the dev setup command installs dependencies and pre-commit hooks."""
    # Setup mock
    mock_console.status.return_value.__enter__.return_value = mock_console

    # Call with default options (install hooks)
    dev_setup(skip_hooks=False)

    # Assertions for default options
    assert mock_subprocess_run.call_count == 2
    mock_subprocess_run.assert_any_call(["pip", "install", "-e", "."], check=True)
    mock_subprocess_run.assert_any_call(["pre-commit", "install"], check=True)

    # Reset mocks
    mock_subprocess_run.reset_mock()

    # Call with skip_hooks=True
    dev_setup(skip_hooks=True)

    # Assertions for skip_hooks=True
    assert mock_subprocess_run.call_count == 1
    mock_subprocess_run.assert_called_once_with(["pip", "install", "-e", "."], check=True)


@patch("enterprise_data_engineering.cli.subprocess.run")
@patch("enterprise_data_engineering.cli.console")
def test_run_lint(mock_console, mock_subprocess_run):
    """Test the lint command runs linting checks."""
    # Setup mock
    mock_console.status.return_value.__enter__.return_value = mock_console
    mock_subprocess_result = MagicMock()
    mock_subprocess_result.returncode = 0
    mock_subprocess_run.return_value = mock_subprocess_result

    # Call without fix option
    run_lint(fix=False)

    # Assertions for default options
    mock_subprocess_run.assert_called_once_with(
        ["hatch", "run", "-e", "lint", "style"], capture_output=True, text=True, check=False
    )

    # Reset mocks
    mock_subprocess_run.reset_mock()

    # Call with fix=True
    run_lint(fix=True)

    # Assertions for fix=True
    mock_subprocess_run.assert_called_once_with(
        ["hatch", "run", "-e", "lint", "fmt"], capture_output=True, text=True, check=False
    )

    # Test failure case
    mock_subprocess_run.reset_mock()
    mock_subprocess_result.returncode = 1
    mock_subprocess_run.return_value = mock_subprocess_result

    run_lint(fix=False)
    assert mock_console.print.call_count >= 3  # Error messages should be printed


@patch("enterprise_data_engineering.cli.subprocess.run")
@patch("enterprise_data_engineering.cli.console")
def test_run_tests(mock_console, mock_subprocess_run):
    """Test the test command runs the test suite."""
    # Setup mock
    mock_console.status.return_value.__enter__.return_value = mock_console

    # Call with default options
    run_tests()

    # Assertions for default options
    mock_subprocess_run.assert_called_once_with(["hatch", "run", "-e", "test"], check=False)

    # Reset mocks
    mock_subprocess_run.reset_mock()

    # Call with test_path and verbose options
    run_tests(test_path="tests/test_specific.py", verbose=True)

    # Assertions for specified options
    mock_subprocess_run.assert_called_once_with(
        ["hatch", "run", "-e", "test", "tests/test_specific.py", "-v"], check=False
    )


@patch("enterprise_data_engineering.cli.subprocess.run")
@patch("enterprise_data_engineering.cli.console")
def test_build_docs(mock_console, mock_subprocess_run):
    """Test the build docs command builds documentation."""
    # Setup mock
    mock_console.status.return_value.__enter__.return_value = mock_console

    # Call the function
    build_docs()

    # Assertions
    assert mock_subprocess_run.call_count == 2
    mock_subprocess_run.assert_any_call(["hatch", "run", "-e", "docs", "generate"], check=False)
    mock_subprocess_run.assert_any_call(["hatch", "run", "-e", "docs", "build"], check=False)


@patch("enterprise_data_engineering.cli.subprocess.run")
@patch("enterprise_data_engineering.cli.console")
def test_serve_docs(mock_console, mock_subprocess_run):
    """Test the serve docs command serves documentation locally."""
    # Call with default port
    serve_docs()

    # Assertions for default port
    mock_subprocess_run.assert_called_once_with(
        ["hatch", "run", "-e", "docs", "mkdocs", "serve", "-a", "localhost:8000"], check=False
    )

    # Reset mocks
    mock_subprocess_run.reset_mock()

    # Call with custom port
    serve_docs(port=9000)

    # Assertions for custom port
    mock_subprocess_run.assert_called_once_with(
        ["hatch", "run", "-e", "docs", "mkdocs", "serve", "-a", "localhost:9000"], check=False
    )


@patch("enterprise_data_engineering.cli.console")
def test_validate_pipeline_file_exists(mock_console, tmp_path):
    """Test the validate pipeline command when file exists."""
    # Create a temporary pipeline file
    pipeline_file = tmp_path / "test_pipeline.yml"
    pipeline_file.write_text("version: 1.0")

    # Setup mock
    mock_console.status.return_value.__enter__.return_value = mock_console

    # Call the function
    validate_pipeline(pipeline_file)

    # Assertions
    mock_console.print.assert_called_once()


@patch("enterprise_data_engineering.cli.console")
def test_validate_pipeline_file_not_exists(mock_console):
    """Test the validate pipeline command when file does not exist."""
    # Use a non-existent file path
    pipeline_file = Path("/non/existent/pipeline.yml")

    # Call the function and expect it to raise an exception
    with pytest.raises(typer.Exit):
        validate_pipeline(pipeline_file)

    # Assertions
    mock_console.print.assert_called_once()


def test_cli_app_integration(cli_runner):
    """Test CLI app and command structure integration."""
    # Test that the app has the required command groups
    assert "dev" in [cmd.name for cmd in app.registered_commands]
    assert "docs" in [cmd.name for cmd in app.registered_commands]
    assert "data" in [cmd.name for cmd in app.registered_commands]

    # Test that the subcommands are registered
    assert "setup" in [cmd.name for cmd in dev_app.registered_commands]
    assert "lint" in [cmd.name for cmd in dev_app.registered_commands]
    assert "test" in [cmd.name for cmd in dev_app.registered_commands]

    assert "build" in [cmd.name for cmd in docs_app.registered_commands]
    assert "serve" in [cmd.name for cmd in docs_app.registered_commands]

    assert "validate" in [cmd.name for cmd in data_app.registered_commands]
