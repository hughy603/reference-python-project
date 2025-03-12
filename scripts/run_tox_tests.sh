#!/usr/bin/env bash
# Bash script to run tox tests on multiple Python versions
# This script helps manage multi-version testing with tox

set -e

# Default values
ENVIRONMENT=""
PARALLEL=false
LIST_ENVS=false
RECREATE=false
ADDITIONAL_ARGS=()

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -l|--list|--list-envs)
            LIST_ENVS=true
            shift
            ;;
        -r|--recreate)
            RECREATE=true
            shift
            ;;
        *)
            ADDITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done

# Check if tox is installed
if ! command -v tox &> /dev/null; then
    echo "Error: Tox is not installed. Please install it with: pip install tox"
    exit 1
fi

# List available environments if requested
if $LIST_ENVS; then
    echo "Available tox environments:"
    tox list
    exit 0
fi

# Build the command
TOX_ARGS=()

# Add environment if specified
if [[ -n "$ENVIRONMENT" ]]; then
    TOX_ARGS+=("-e" "$ENVIRONMENT")
fi

# Add parallel flag if requested
if $PARALLEL; then
    TOX_ARGS+=("--parallel")
fi

# Add recreate flag if requested
if $RECREATE; then
    TOX_ARGS+=("--recreate")
fi

# Add any additional arguments
if [[ ${#ADDITIONAL_ARGS[@]} -gt 0 ]]; then
    TOX_ARGS+=("${ADDITIONAL_ARGS[@]}")
fi

# Display the command being run
echo -e "\033[36mRunning: tox ${TOX_ARGS[*]}\033[0m"

# Run tox with all specified arguments
tox "${TOX_ARGS[@]}"

# Check return code
if [[ $? -ne 0 ]]; then
    echo -e "\033[31mTox tests failed with exit code $?\033[0m"
    exit $?
else
    echo -e "\033[32mTox tests completed successfully!\033[0m"
fi
