#!/usr/bin/env python3
"""
Integration tests for the wizard shell scripts.

These tests validate that the wizard.sh and wizard.ps1 scripts
correctly handle environment detection and launch the wizard.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

import pytest

# Determine if running on Windows
IS_WINDOWS = platform.system() == "Windows"

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = PROJECT_ROOT / "scripts"

# Paths to the wizard scripts
SHELL_SCRIPT = SCRIPT_DIR / "wizard.sh"
POWERSHELL_SCRIPT = SCRIPT_DIR / "wizard.ps1"


@pytest.fixture
def mock_python_executable():
    """Fixture to mock the Python executable."""
    original_executable = sys.executable
    return original_executable


# Test the shell script (wizard.sh)
@pytest.mark.skipif(IS_WINDOWS, reason="Shell script tests only run on Unix systems")
def test_shell_script_help_flag(mock_python_executable):
    """Test that the shell script passes the --help flag to the wizard."""
    # Create a mock script that prints the command line arguments
    mock_script = SCRIPT_DIR / "mock_wizard.py"
    with open(mock_script, "w") as f:
        f.write("""#!/usr/bin/env python3
import sys
print("MOCK_WIZARD_CALLED")
print("ARGS:", " ".join(sys.argv[1:]))
sys.exit(0)
""")

    try:
        # Make the mock script executable
        os.chmod(mock_script, 0o755)

        # Patch the environment to use the mock script
        env = os.environ.copy()
        env["WIZARD_SCRIPT"] = str(mock_script)

        # Run the shell script with the --help flag
        result = subprocess.run(
            ["bash", str(SHELL_SCRIPT), "--help"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        # Check that the script ran successfully
        assert result.returncode == 0

        # Check that the mock wizard was called with the correct arguments
        assert "MOCK_WIZARD_CALLED" in result.stdout
        assert "ARGS: --help" in result.stdout
    finally:
        # Clean up the mock script
        if mock_script.exists():
            mock_script.unlink()


@pytest.mark.skipif(IS_WINDOWS, reason="Shell script tests only run on Unix systems")
def test_shell_script_error_handling(mock_python_executable):
    """Test that the shell script handles errors from the wizard."""
    # Create a mock script that exits with an error
    mock_script = SCRIPT_DIR / "mock_wizard.py"
    with open(mock_script, "w") as f:
        f.write("""#!/usr/bin/env python3
import sys
print("MOCK_WIZARD_ERROR")
sys.exit(1)
""")

    try:
        # Make the mock script executable
        os.chmod(mock_script, 0o755)

        # Patch the environment to use the mock script
        env = os.environ.copy()
        env["WIZARD_SCRIPT"] = str(mock_script)

        # Run the shell script
        result = subprocess.run(
            ["bash", str(SHELL_SCRIPT)], env=env, capture_output=True, text=True, check=False
        )

        # Check that the script propagates the error code
        assert result.returncode == 1

        # Check that the error message was printed
        assert "MOCK_WIZARD_ERROR" in result.stdout
        assert "Error" in result.stderr
    finally:
        # Clean up the mock script
        if mock_script.exists():
            mock_script.unlink()


# Test the PowerShell script (wizard.ps1)
@pytest.mark.skipif(not IS_WINDOWS, reason="PowerShell script tests only run on Windows")
def test_powershell_script_help_flag(mock_python_executable):
    """Test that the PowerShell script passes the --help flag to the wizard."""
    # Skip if PowerShell is not available
    try:
        subprocess.run(["powershell", "-Command", "Get-Command"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("PowerShell is not available")

    # Create a mock script that prints the command line arguments
    mock_script = SCRIPT_DIR / "mock_wizard.py"
    with open(mock_script, "w") as f:
        f.write("""#!/usr/bin/env python3
import sys
print("MOCK_WIZARD_CALLED")
print("ARGS:", " ".join(sys.argv[1:]))
sys.exit(0)
""")

    try:
        # Patch the environment to use the mock script
        env = os.environ.copy()
        env["WIZARD_SCRIPT"] = str(mock_script)

        # Run the PowerShell script with the --help flag
        result = subprocess.run(
            ["powershell", "-File", str(POWERSHELL_SCRIPT), "--help"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        # Check that the script ran successfully
        assert result.returncode == 0

        # Check that the mock wizard was called with the correct arguments
        assert "MOCK_WIZARD_CALLED" in result.stdout
        assert "ARGS: --help" in result.stdout
    finally:
        # Clean up the mock script
        if mock_script.exists():
            mock_script.unlink()


@pytest.mark.skipif(not IS_WINDOWS, reason="PowerShell script tests only run on Windows")
def test_powershell_script_error_handling(mock_python_executable):
    """Test that the PowerShell script handles errors from the wizard."""
    # Skip if PowerShell is not available
    try:
        subprocess.run(["powershell", "-Command", "Get-Command"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("PowerShell is not available")

    # Create a mock script that exits with an error
    mock_script = SCRIPT_DIR / "mock_wizard.py"
    with open(mock_script, "w") as f:
        f.write("""#!/usr/bin/env python3
import sys
print("MOCK_WIZARD_ERROR")
sys.exit(1)
""")

    try:
        # Patch the environment to use the mock script
        env = os.environ.copy()
        env["WIZARD_SCRIPT"] = str(mock_script)

        # Run the PowerShell script
        result = subprocess.run(
            ["powershell", "-File", str(POWERSHELL_SCRIPT)],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        # Check that the script propagates the error code
        assert result.returncode == 1

        # Check that the error message was printed
        assert "MOCK_WIZARD_ERROR" in result.stdout
        assert "Error" in result.stdout
    finally:
        # Clean up the mock script
        if mock_script.exists():
            mock_script.unlink()


# Test wizard.sh modifications to handle mock script
@pytest.mark.skipif(IS_WINDOWS, reason="Shell script tests only run on Unix systems")
def test_patch_shell_script():
    """Test patching wizard.sh to use a mock script for testing."""
    # Create a backup of the wizard.sh script
    script_content = SHELL_SCRIPT.read_text()
    backup_file = SHELL_SCRIPT.with_suffix(".sh.bak")

    try:
        # Create the backup
        SHELL_SCRIPT.write_text(script_content)

        # Patch the script to use the mock script
        patched_content = script_content.replace(
            '$PY_CMD "$SCRIPT_DIR/run_interactive_wizard.py" "$@"',
            'if [ -n "$WIZARD_SCRIPT" ]; then\n  $PY_CMD "$WIZARD_SCRIPT" "$@"\nelse\n  $PY_CMD "$SCRIPT_DIR/run_interactive_wizard.py" "$@"\nfi',
        )
        SHELL_SCRIPT.write_text(patched_content)

        # Verify that the script was patched correctly
        assert "WIZARD_SCRIPT" in SHELL_SCRIPT.read_text()

    finally:
        # Restore the original script from backup
        if backup_file.exists():
            SHELL_SCRIPT.write_text(backup_file.read_text())
            backup_file.unlink()
        else:
            SHELL_SCRIPT.write_text(script_content)


# Test wizard.ps1 modifications to handle mock script
@pytest.mark.skipif(not IS_WINDOWS, reason="PowerShell script tests only run on Windows")
def test_patch_powershell_script():
    """Test patching wizard.ps1 to use a mock script for testing."""
    # Create a backup of the wizard.ps1 script
    script_content = POWERSHELL_SCRIPT.read_text()
    backup_file = POWERSHELL_SCRIPT.with_suffix(".ps1.bak")

    try:
        # Create the backup
        POWERSHELL_SCRIPT.write_text(script_content)

        # Patch the script to use the mock script
        patched_content = script_content.replace(
            '& $pythonCmd "$ScriptDir\\run_interactive_wizard.py" $args',
            'if ($env:WIZARD_SCRIPT) {\n    & $pythonCmd "$env:WIZARD_SCRIPT" $args\n} else {\n    & $pythonCmd "$ScriptDir\\run_interactive_wizard.py" $args\n}',
        )
        POWERSHELL_SCRIPT.write_text(patched_content)

        # Verify that the script was patched correctly
        assert "WIZARD_SCRIPT" in POWERSHELL_SCRIPT.read_text()

    finally:
        # Restore the original script from backup
        if backup_file.exists():
            POWERSHELL_SCRIPT.write_text(backup_file.read_text())
            backup_file.unlink()
        else:
            POWERSHELL_SCRIPT.write_text(script_content)
