#!/bin/bash
# Documentation management script

set -e  # Exit on error

# Change to the project root directory (adjust if needed)
cd "$(dirname "$0")/.."

# Define colors for prettier output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function print_header() {
    echo -e "\n${BLUE}=================================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=================================================================================${NC}\n"
}

function print_step() {
    echo -e "${GREEN}==>${NC} $1"
}

function print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

function print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

function check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is required but not installed. Please install it first."
        exit 1
    fi
}

# Check if required commands are available
check_command python
check_command pip

function show_help() {
    echo "Documentation Management Script"
    echo ""
    echo "Usage:"
    echo "  $0 [command]"
    echo ""
    echo "Commands:"
    echo "  fix       Fix documentation issues (create missing files, fix broken links)"
    echo "  build     Build the documentation"
    echo "  serve     Build and serve the documentation locally"
    echo "  all       Fix, build, and serve the documentation"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 fix     # Fix documentation issues"
    echo "  $0 build   # Build the documentation"
    echo "  $0 serve   # Serve the documentation locally"
    echo "  $0 all     # Fix, build, and serve the documentation"
}

function fix_docs() {
    print_header "Fixing Documentation Issues"

    # Install required dependencies if needed
    if ! python -c "import yaml" &> /dev/null; then
        print_step "Installing PyYAML..."
        pip install pyyaml
    fi

    print_step "Running documentation fixer script..."
    python scripts/fix_documentation.py
}

function build_docs() {
    print_header "Building Documentation"

    # Check if hatch is installed
    if command -v hatch &> /dev/null; then
        print_step "Building documentation with Hatch..."
        hatch -e docs run generate
        hatch -e docs run build
    else
        # Fallback to using mkdocs directly
        print_step "Hatch not found, using mkdocs directly..."

        # Make sure mkdocs is installed
        if ! command -v mkdocs &> /dev/null; then
            print_step "Installing mkdocs and required packages..."
            pip install mkdocs mkdocs-material mkdocstrings[python] pymdown-extensions
        fi

        # Run mkdocs build
        mkdocs build
    fi

    print_step "Documentation built successfully!"
}

function serve_docs() {
    print_header "Serving Documentation"

    # Check if hatch is installed
    if command -v hatch &> /dev/null; then
        print_step "Serving documentation with Hatch..."
        hatch -e docs run serve
    else
        # Fallback to using mkdocs directly
        print_step "Hatch not found, using mkdocs directly..."

        # Make sure mkdocs is installed
        if ! command -v mkdocs &> /dev/null; then
            print_step "Installing mkdocs and required packages..."
            pip install mkdocs mkdocs-material mkdocstrings[python] pymdown-extensions
        fi

        # Run mkdocs serve
        mkdocs serve
    fi
}

# Check command line arguments
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

# Process command line arguments
case "$1" in
    fix)
        fix_docs
        ;;
    build)
        build_docs
        ;;
    serve)
        serve_docs
        ;;
    all)
        fix_docs
        build_docs
        serve_docs
        ;;
    help)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac

exit 0
