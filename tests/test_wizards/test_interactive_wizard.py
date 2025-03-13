#!/usr/bin/env python3
"""
Unit tests for the interactive project initialization wizard.

These tests validate the functionality of the interactive wizard,
including component selection, configuration handling, and project initialization.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

# Add the scripts directory to the path to import the wizard module
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.append(str(SCRIPT_DIR))

# Import the wizard module
import interactive_wizard

# Fixtures


@pytest.fixture
def mock_console():
    """Fixture for mocking the rich console."""
    with patch("interactive_wizard.console") as mock:
        yield mock


@pytest.fixture
def mock_rich_available():
    """Fixture for setting RICH_AVAILABLE to True."""
    with patch("interactive_wizard.RICH_AVAILABLE", True):
        yield


@pytest.fixture
def mock_rich_unavailable():
    """Fixture for setting RICH_AVAILABLE to False."""
    with patch("interactive_wizard.RICH_AVAILABLE", False):
        yield


@pytest.fixture
def sample_manifest():
    """Fixture for a sample template manifest."""
    return {
        "template": {
            "name": "Test Template",
            "version": "1.0.0",
            "description": "A test template for unit testing",
        },
        "components": [
            {
                "name": "core",
                "description": "Core Python project structure",
                "required": True,
                "files": [],
            },
            {
                "name": "aws",
                "description": "AWS integration",
                "required": False,
                "files": [],
                "dependencies": [],
            },
            {
                "name": "terraform",
                "description": "Terraform infrastructure",
                "required": False,
                "files": [],
                "dependencies": [],
            },
            {
                "name": "documentation",
                "description": "Project documentation",
                "required": False,
                "files": [],
                "dependencies": [],
            },
            {
                "name": "cloudformation",
                "description": "CloudFormation templates",
                "required": False,
                "files": [],
                "dependencies": ["aws"],
            },
        ],
    }


@pytest.fixture
def sample_config():
    """Fixture for a sample configuration."""
    return {
        "project_name": "test-project",
        "package_name": "test_project",
        "description": "A test project",
        "author": "Test Author",
        "email": "test@example.com",
        "organization": "Test Org",
        "version": "0.1.0",
        "components": {
            "core": True,
            "aws": True,
            "terraform": True,
            "documentation": False,
            "cloudformation": False,
        },
    }


# Tests for utility functions


def test_print_rich_panel_with_rich(mock_rich_available, mock_console):
    """Test print_rich_panel when rich is available."""
    from interactive_wizard import Panel, print_rich_panel

    print_rich_panel("Test Title", "Test Content", "green")

    mock_console.print.assert_called_once()
    args, _ = mock_console.print.call_args
    assert isinstance(args[0], Panel)
    assert args[0].title == "Test Title"


def test_print_rich_panel_without_rich(mock_rich_unavailable, capsys):
    """Test print_rich_panel when rich is not available."""
    interactive_wizard.print_rich_panel("Test Title", "Test Content", "green")

    captured = capsys.readouterr()
    assert "--- Test Title ---" in captured.out
    assert "Test Content" in captured.out


def test_print_rich_markdown_with_rich(mock_rich_available, mock_console):
    """Test print_rich_markdown when rich is available."""
    from interactive_wizard import Markdown, print_rich_markdown

    print_rich_markdown("# Test Markdown")

    mock_console.print.assert_called_once()
    args, _ = mock_console.print.call_args
    assert isinstance(args[0], Markdown)


def test_print_rich_markdown_without_rich(mock_rich_unavailable, capsys):
    """Test print_rich_markdown when rich is not available."""
    interactive_wizard.print_rich_markdown("# Test Markdown")

    captured = capsys.readouterr()
    assert "# Test Markdown" in captured.out


# Tests for component table creation


def test_create_component_table_with_rich(mock_rich_available):
    """Test creating a component table with rich."""
    components = [
        {"name": "core", "description": "Core", "required": True},
        {"name": "aws", "description": "AWS", "dependencies": []},
    ]
    selected = {"core": True, "aws": True}

    result = interactive_wizard.create_component_table(components, selected)

    assert isinstance(result, interactive_wizard.Table)
    # Check that it has the expected columns
    assert len(result.columns) == 4


def test_create_component_table_without_rich(mock_rich_unavailable):
    """Test creating a component table without rich."""
    components = [
        {"name": "core", "description": "Core", "required": True},
        {"name": "aws", "description": "AWS", "dependencies": []},
    ]
    selected = {"core": True, "aws": True}

    result = interactive_wizard.create_component_table(components, selected)

    assert isinstance(result, str)
    assert "Components:" in result
    assert "[x] aws - AWS" in result


# Tests for config summary creation


def test_create_config_summary_with_rich(mock_rich_available):
    """Test creating a config summary with rich."""
    config = {
        "project_name": "test-project",
        "package_name": "test_project",
        "components": {"aws": True, "terraform": False},
    }

    result = interactive_wizard.create_config_summary(config)

    assert isinstance(result, interactive_wizard.Panel)


def test_create_config_summary_without_rich(mock_rich_unavailable):
    """Test creating a config summary without rich."""
    config = {
        "project_name": "test-project",
        "package_name": "test_project",
        "components": {"aws": True, "terraform": False},
    }

    result = interactive_wizard.create_config_summary(config)

    assert isinstance(result, str)
    assert "Configuration Summary:" in result
    assert "- Project name: test-project" in result
    assert "- Components:" in result
    assert "  - aws" in result


# Tests for manifest loading


def test_load_manifest(tmp_path, sample_manifest):
    """Test loading a manifest file."""
    # Create a temporary manifest file
    manifest_path = tmp_path / "template_manifest.yml"
    with open(manifest_path, "w") as f:
        yaml.dump(sample_manifest, f)

    # Patch PROJECT_ROOT to point to the temporary directory
    with patch("interactive_wizard.PROJECT_ROOT", tmp_path):
        result = interactive_wizard.load_manifest()

    assert result == sample_manifest


def test_load_manifest_file_not_found():
    """Test loading a non-existent manifest file."""
    # Patch PROJECT_ROOT to point to a non-existent directory
    with patch("interactive_wizard.PROJECT_ROOT", Path("/non-existent")):
        with pytest.raises(SystemExit):
            interactive_wizard.load_manifest()


# Tests for welcome screen


def test_welcome_screen_with_rich(mock_rich_available, mock_console, sample_manifest):
    """Test the welcome screen with rich."""
    with patch("interactive_wizard.load_manifest", return_value=sample_manifest):
        interactive_wizard.welcome_screen()

    # Check that console.print was called multiple times
    assert mock_console.print.call_count > 0
    assert mock_console.clear.call_count == 1


def test_welcome_screen_without_rich(mock_rich_unavailable, capsys, sample_manifest):
    """Test the welcome screen without rich."""
    with patch("interactive_wizard.load_manifest", return_value=sample_manifest):
        interactive_wizard.welcome_screen()

    captured = capsys.readouterr()
    assert "=== Project Initialization Wizard ===" in captured.out
    assert "Test Template" in captured.out


# Tests for metadata prompting


def test_prompt_for_metadata_with_rich(mock_rich_available):
    """Test prompting for metadata with rich."""
    # Mock Prompt.ask to return predefined values
    with patch(
        "interactive_wizard.Prompt.ask",
        side_effect=[
            "test-project",  # project_name
            "test_project",  # package_name
            "A test project",  # description
            "Test Author",  # author
            "test@example.com",  # email
            "Test Org",  # organization
            "0.1.0",  # version
        ],
    ):
        result = interactive_wizard.prompt_for_metadata()

    assert result["project_name"] == "test-project"
    assert result["package_name"] == "test_project"
    assert result["description"] == "A test project"
    assert result["author"] == "Test Author"
    assert result["email"] == "test@example.com"
    assert result["organization"] == "Test Org"
    assert result["version"] == "0.1.0"


def test_prompt_for_metadata_without_rich(mock_rich_unavailable):
    """Test prompting for metadata without rich."""
    # Mock input to return predefined values
    with patch(
        "builtins.input",
        side_effect=[
            "test-project",  # project_name
            "test_project",  # package_name
            "A test project",  # description
            "Test Author",  # author
            "test@example.com",  # email
            "Test Org",  # organization
            "0.1.0",  # version
        ],
    ):
        result = interactive_wizard.prompt_for_metadata()

    assert result["project_name"] == "test-project"
    assert result["package_name"] == "test_project"
    assert result["description"] == "A test project"
    assert result["author"] == "Test Author"
    assert result["email"] == "test@example.com"
    assert result["organization"] == "Test Org"
    assert result["version"] == "0.1.0"


# Tests for component selection


def test_prompt_for_components_with_rich(mock_rich_available, mock_console, sample_manifest):
    """Test prompting for components with rich."""
    # Mock Confirm.ask to return predefined values
    with patch("interactive_wizard.Confirm.ask", side_effect=[True, False, True]):
        result = interactive_wizard.prompt_for_components(sample_manifest)

    assert result["core"] is True  # Required component
    assert result["aws"] is True  # First component, mocked as True
    assert result["terraform"] is False  # Second component, mocked as False
    assert result["documentation"] is True  # Third component, mocked as True
    # cloudformation depends on aws, which is True
    assert result["cloudformation"] is True


def test_prompt_for_components_without_rich(mock_rich_unavailable, sample_manifest):
    """Test prompting for components without rich."""
    # Mock input to return predefined values
    with patch("builtins.input", side_effect=["y", "n", "y"]):
        result = interactive_wizard.prompt_for_components(sample_manifest)

    assert result["core"] is True  # Required component
    assert result["aws"] is True  # First component, input "y"
    assert result["terraform"] is False  # Second component, input "n"
    assert result["documentation"] is True  # Third component, input "y"
    # cloudformation depends on aws, which is True
    assert result["cloudformation"] is True


def test_prompt_for_components_dependency_resolution(mock_rich_unavailable, sample_manifest):
    """Test component dependency resolution."""
    # Select cloudformation (which depends on aws) but not aws directly
    with patch("builtins.input", side_effect=["n", "n", "n", "y"]):
        result = interactive_wizard.prompt_for_components(sample_manifest)

    # aws should be included due to dependency
    assert result["aws"] is True
    assert result["cloudformation"] is True


# Tests for project initialization


def test_initialize_project_success(mock_rich_available, mock_console, sample_config, tmp_path):
    """Test successful project initialization."""
    # Patch subprocess to simulate successful execution
    mock_process = MagicMock()
    mock_process.poll.side_effect = [None, None, None, 0]
    mock_process.returncode = 0
    mock_process.communicate.return_value = ("Success", "")

    with (
        patch("interactive_wizard.PROJECT_ROOT", tmp_path),
        patch("interactive_wizard.subprocess.Popen", return_value=mock_process),
    ):
        # Create init_project.py in the temp directory
        (tmp_path / "scripts").mkdir(exist_ok=True)
        (tmp_path / "scripts" / "init_project.py").touch()

        result = interactive_wizard.initialize_project(sample_config)

    assert result is True
    # Verify that a temporary config file was created and then removed
    assert not (tmp_path / ".temp_init_config.yml").exists()


def test_initialize_project_failure(mock_rich_available, mock_console, sample_config, tmp_path):
    """Test failed project initialization."""
    # Patch subprocess to simulate failed execution
    mock_process = MagicMock()
    mock_process.poll.side_effect = [None, None, None, 1]
    mock_process.returncode = 1
    mock_process.communicate.return_value = ("", "Error message")

    with (
        patch("interactive_wizard.PROJECT_ROOT", tmp_path),
        patch("interactive_wizard.subprocess.Popen", return_value=mock_process),
    ):
        # Create init_project.py in the temp directory
        (tmp_path / "scripts").mkdir(exist_ok=True)
        (tmp_path / "scripts" / "init_project.py").touch()

        result = interactive_wizard.initialize_project(sample_config)

    assert result is False
    # Verify that a temporary config file was created and then removed
    assert not (tmp_path / ".temp_init_config.yml").exists()


def test_initialize_project_script_not_found(mock_rich_unavailable, sample_config, tmp_path):
    """Test initialization when the init script is not found."""
    with patch("interactive_wizard.PROJECT_ROOT", tmp_path):
        # Create scripts directory but not the init script
        (tmp_path / "scripts").mkdir(exist_ok=True)

        result = interactive_wizard.initialize_project(sample_config)

    assert result is False


# Tests for the main function


def test_main_success_flow(mock_rich_available, sample_manifest, sample_config):
    """Test the main function's success flow."""
    with (
        patch("interactive_wizard.welcome_screen") as mock_welcome,
        patch("interactive_wizard.load_manifest", return_value=sample_manifest) as mock_load,
        patch(
            "interactive_wizard.prompt_for_metadata", return_value=sample_config
        ) as mock_metadata,
        patch(
            "interactive_wizard.prompt_for_components", return_value=sample_config["components"]
        ) as mock_components,
        patch("interactive_wizard.create_config_summary") as mock_summary,
        patch("interactive_wizard.Confirm.ask", return_value=True) as mock_confirm,
        patch("interactive_wizard.initialize_project", return_value=True) as mock_init,
    ):
        interactive_wizard.main()

    # Verify that all expected functions were called
    mock_welcome.assert_called_once()
    mock_load.assert_called_once()
    mock_metadata.assert_called_once()
    mock_components.assert_called_once_with(sample_manifest)
    mock_summary.assert_called_once()
    mock_confirm.assert_called_once()
    mock_init.assert_called_once()


def test_main_cancelled_by_user(mock_rich_available, sample_manifest, sample_config):
    """Test the main function when the user cancels at confirmation."""
    with (
        patch("interactive_wizard.welcome_screen") as mock_welcome,
        patch("interactive_wizard.load_manifest", return_value=sample_manifest) as mock_load,
        patch(
            "interactive_wizard.prompt_for_metadata", return_value=sample_config
        ) as mock_metadata,
        patch(
            "interactive_wizard.prompt_for_components", return_value=sample_config["components"]
        ) as mock_components,
        patch("interactive_wizard.create_config_summary") as mock_summary,
        patch("interactive_wizard.Confirm.ask", return_value=False) as mock_confirm,
        patch("interactive_wizard.initialize_project") as mock_init,
    ):
        interactive_wizard.main()

    # Verify that initialization was not called
    mock_init.assert_not_called()


def test_main_keyboard_interrupt(mock_rich_available, mock_console):
    """Test the main function when interrupted by Ctrl+C."""
    with patch("interactive_wizard.welcome_screen", side_effect=KeyboardInterrupt):
        interactive_wizard.main()

    # Verify that the cancellation message was printed
    mock_console.print.assert_called_with("\n[yellow]Initialization cancelled by user.[/yellow]")


def test_main_exception(mock_rich_available, mock_console):
    """Test the main function when an exception occurs."""
    error_message = "Test error"
    with patch("interactive_wizard.welcome_screen", side_effect=ValueError(error_message)):
        interactive_wizard.main()

    # Verify that the error message was printed
    mock_console.print.assert_called_with(f"\n[bold red]Error: {error_message}[/bold red]")


# Integration test (simulated)


def test_integrated_workflow(mock_rich_available, sample_manifest, tmp_path):
    """Test an integrated workflow through the wizard."""
    # Setup mocks for all the steps
    with (
        patch("interactive_wizard.PROJECT_ROOT", tmp_path),
        patch("interactive_wizard.load_manifest", return_value=sample_manifest),
        patch(
            "interactive_wizard.Prompt.ask",
            side_effect=[
                "test-project",  # project_name
                "test_project",  # package_name
                "A test project",  # description
                "Test Author",  # author
                "test@example.com",  # email
                "Test Org",  # organization
                "0.1.0",  # version
            ],
        ),
        patch(
            "interactive_wizard.Confirm.ask",
            side_effect=[
                True,  # aws
                True,  # terraform
                False,  # documentation
                True,  # cloudformation
                True,  # proceed with initialization
            ],
        ),
        patch("interactive_wizard.initialize_project", return_value=True),
    ):
        # Create scripts directory with init script
        (tmp_path / "scripts").mkdir(exist_ok=True)
        (tmp_path / "scripts" / "init_project.py").touch()

        # Run the main function
        interactive_wizard.main()

    # No assertions needed here as the test will fail if any exceptions occur
    # during the patched function calls
