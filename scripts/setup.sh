#!/bin/bash
# Cross-platform setup script for Enterprise Data Engineering
# This script detects the platform and runs the setup script

# Colors for console output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project root directory (parent of the scripts directory)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Python executable based on platform
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    PYTHON="python"
else
    PYTHON="python3"
fi

# Check if Python is installed
if ! command -v $PYTHON &> /dev/null; then
    echo -e "${RED}Error: $PYTHON is not installed or not in PATH${NC}"
    echo "Please install Python 3.11 or newer and try again."
    exit 1
fi

# Run the setup script
cd "$PROJECT_ROOT"
echo -e "${GREEN}Running setup script...${NC}"
$PYTHON setup.py

# Final status check
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Setup completed successfully!${NC}"
    exit 0
else
    echo -e "${RED}Setup encountered errors.${NC}"
    echo "Please check the output above for error messages."
    exit 1
fi
