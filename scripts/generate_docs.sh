#!/bin/bash
# Script to generate all documentation for the project

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Create assets directory structure
mkdir -p "${REPO_ROOT}/docs/assets/images"

# Echo with color
info() {
    echo -e "\033[0;36m$1\033[0m"
}

success() {
    echo -e "\033[0;32m$1\033[0m"
}

warn() {
    echo -e "\033[0;33m$1\033[0m"
}

error() {
    echo -e "\033[0;31m$1\033[0m"
}

info "Generating documentation for Enterprise Data Engineering Reference Project"
info "=====================================================================\n"

# Check if Hatch is installed
if ! command -v hatch &> /dev/null; then
    error "Error: Hatch is not installed. Please install it using 'pip install hatch'"
    exit 1
fi

# Check if terraform-docs is installed
if ! command -v terraform-docs &> /dev/null; then
    warn "Warning: terraform-docs is not installed. Terraform documentation will not be generated."
    warn "Install terraform-docs from https://terraform-docs.io/\n"
fi

# Create reference directory if it doesn't exist
mkdir -p "${REPO_ROOT}/docs/reference/terraform"

# Generate Python API documentation
info "Generating Python API documentation..."
if [ -d "${REPO_ROOT}/src" ]; then
    python "${REPO_ROOT}/scripts/generate_api_docs.py"
    success "Python API documentation generated\n"
else
    warn "Warning: src directory not found. Skipping Python API documentation\n"
fi

# Generate Terraform documentation
info "Generating Terraform documentation..."
if [ -d "${REPO_ROOT}/infrastructure/terraform" ]; then
    python "${REPO_ROOT}/scripts/generate_terraform_docs.py"
    success "Terraform documentation generated\n"
else
    warn "Warning: infrastructure/terraform directory not found. Skipping Terraform documentation\n"
fi

# Build the documentation site
info "Building documentation site with MkDocs..."
cd "${REPO_ROOT}"
hatch -e docs run mkdocs build
success "Documentation site built successfully\n"

# Instructions for serving documentation locally
info "Documentation generation complete!"
info "To serve the documentation locally, run:"
info "  hatch -e docs run mkdocs serve"
info ""
info "To deploy to GitHub Pages, run:"
info "  hatch -e docs run mkdocs gh-deploy --force"
