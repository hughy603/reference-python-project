#!/bin/bash
# Interactive Project Initialization Wizard Runner
# This script runs the interactive wizard with proper error handling
# and environment detection.

# Set strict error handling
set -e

# Determine script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Function to display error message and exit
error_exit() {
  echo -e "\e[31mError:\e[0m $1" >&2
  exit 1
}

# Function to display success message
success_message() {
  echo -e "\e[32mSuccess:\e[0m $1"
}

# Function to display info message
info_message() {
  echo -e "\e[34mInfo:\e[0m $1"
}

# Change to project root
cd "$PROJECT_ROOT" || error_exit "Could not change to project root directory"

# Check for Python
if ! command_exists python3; then
  if command_exists python; then
    PY_CMD="python"
  else
    error_exit "Python is not installed or not in PATH"
  fi
else
  PY_CMD="python3"
fi

# Check Python version
PY_VERSION=$($PY_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ "$(echo "$PY_VERSION" | cut -d. -f1)" -lt 3 ]] || [[ "$(echo "$PY_VERSION" | cut -d. -f1)" -eq 3 && "$(echo "$PY_VERSION" | cut -d. -f2)" -lt 8 ]]; then
  error_exit "Python 3.8 or newer is required (found $PY_VERSION)"
fi

info_message "Python $PY_VERSION detected"

# Check for virtual environment
if [[ -d ".venv" ]]; then
  info_message "Found virtual environment at .venv"
  if [[ -f ".venv/bin/activate" ]]; then
    info_message "Activating virtual environment"
    # shellcheck disable=SC1091
    source ".venv/bin/activate"
  elif [[ -f ".venv/Scripts/activate" ]]; then
    info_message "Activating virtual environment (Windows)"
    # shellcheck disable=SC1091
    source ".venv/Scripts/activate"
  else
    info_message "Could not activate virtual environment, continuing anyway"
  fi
fi

# Check if running in a terminal
if [ -t 1 ]; then
  # Run in interactive mode
  info_message "Starting interactive wizard..."

  # Check if WIZARD_SCRIPT environment variable is set (for testing)
  if [ -n "$WIZARD_SCRIPT" ]; then
    info_message "Using custom wizard script: $WIZARD_SCRIPT"
    $PY_CMD "$WIZARD_SCRIPT" "$@"
    exit_code=$?
  else
    $PY_CMD "$SCRIPT_DIR/run_interactive_wizard.py" "$@"
    exit_code=$?
  fi
else
  # Not a terminal, warn and use non-interactive mode
  info_message "Not running in a terminal, using non-interactive mode"

  # Check if WIZARD_SCRIPT environment variable is set (for testing)
  if [ -n "$WIZARD_SCRIPT" ]; then
    info_message "Using custom wizard script: $WIZARD_SCRIPT"
    $PY_CMD "$WIZARD_SCRIPT" --no-install "$@"
    exit_code=$?
  else
    $PY_CMD "$SCRIPT_DIR/run_interactive_wizard.py" --no-install "$@"
    exit_code=$?
  fi
fi

# Check exit code
if [ $exit_code -eq 0 ]; then
  success_message "Wizard completed successfully!"
else
  error_exit "Wizard failed with exit code $exit_code"
fi
