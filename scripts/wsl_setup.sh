#!/bin/bash
# WSL Setup Script for reference-python-project
# This script sets up a WSL environment for development

set -e

echo "====================================================="
echo "  WSL Development Environment Setup"
echo "====================================================="
echo ""

# Make script output colorful
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display status messages
status() {
    echo -e "${CYAN}[STATUS] $1${NC}"
}

# Function to display success messages
success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

# Function to display warning messages
warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Function to display error messages
error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Check for necessary tools
check_deps() {
    status "Checking dependencies..."

    # Check for Python 3.11+
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed. Please install Python 3.11 or newer."
    fi

    python_version=$(python3 --version | cut -d' ' -f2)
    if [[ $(echo "$python_version" | cut -d. -f1,2 | sed 's/\.//') -lt 311 ]]; then
        warning "Python version $python_version detected. This project recommends Python 3.11 or newer."
    else
        success "Python $python_version detected."
    fi

    # Check for pip
    if ! command -v pip &> /dev/null; then
        error "pip is not installed. Please install pip for Python 3."
    else
        success "pip detected."
    fi

    # Check for git
    if ! command -v git &> /dev/null; then
        error "git is not installed. Please install git."
    else
        success "git detected."
    fi
}

# Update system packages
update_system() {
    status "Updating system packages..."

    sudo apt update || error "Failed to update apt repositories."
    sudo apt upgrade -y || warning "Failed to upgrade some packages."

    sudo apt install -y \
        python3.11 \
        python3.11-venv \
        python3.11-dev \
        python3-pip \
        git \
        curl \
        build-essential \
        libssl-dev \
        libffi-dev \
        || warning "Failed to install some packages."

    success "System packages updated."
}

# Set up Python environment
setup_python() {
    status "Setting up Python environment..."

    # Create virtual environment
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv || error "Failed to create virtual environment."
        success "Virtual environment created."
    else
        warning "Virtual environment already exists."
    fi

    # Source the virtual environment
    source .venv/bin/activate || error "Failed to activate virtual environment."

    # Install Hatch
    pip install --upgrade pip || warning "Failed to upgrade pip."
    pip install hatch || error "Failed to install Hatch."

    # Install pre-commit
    pip install pre-commit || error "Failed to install pre-commit."

    success "Python environment setup complete."
}

# Set up project
setup_project() {
    status "Setting up project..."

    # Install dependencies with Hatch
    hatch env create || warning "Hatch environment creation failed, trying alternate method."

    # Set up pre-commit hooks
    pre-commit install || warning "Failed to install pre-commit hooks."

    success "Project setup complete."
}

# Configure Git
configure_git() {
    status "Configuring Git..."

    # Check if Git is already configured
    if [ -z "$(git config --global user.name)" ]; then
        echo "Enter your Git username:"
        read git_name
        git config --global user.name "$git_name" || warning "Failed to set Git username."
    else
        warning "Git username already configured."
    fi

    if [ -z "$(git config --global user.email)" ]; then
        echo "Enter your Git email:"
        read git_email
        git config --global user.email "$git_email" || warning "Failed to set Git email."
    else
        warning "Git email already configured."
    fi

    # Set recommended Git settings
    git config --global core.autocrlf input || warning "Failed to set Git line ending behavior."
    git config --global pull.rebase true || warning "Failed to set Git pull behavior."

    success "Git configuration complete."
}

# Configure WSL specifics
configure_wsl() {
    status "Configuring WSL-specific settings..."

    # Create .wslconfig file template
    echo "# Recommended .wslconfig for Windows 11
# Place this file in %UserProfile%\.wslconfig on your Windows system

[wsl2]
memory=6GB
processors=4
swap=8GB
swapfile=C:\\Temp\\wsl-swap.vhdx
pageReporting=false
nestedVirtualization=true
networkingMode=mirrored
kernelCommandLine=quiet splash" > ~/wslconfig_example.txt

    success "Created wslconfig_example.txt in your home directory."
    echo "Please copy this file to your Windows user profile as .wslconfig"
    echo "On Windows, run: copy %USERPROFILE%\\wslconfig_example.txt %USERPROFILE%\\.wslconfig"
}

# Main execution
main() {
    check_deps
    update_system
    setup_python
    setup_project
    configure_git
    configure_wsl

    echo ""
    echo "====================================================="
    success "WSL Development Environment Setup Complete!"
    echo "====================================================="
    echo ""
    echo "To activate the virtual environment, run:"
    echo "  source .venv/bin/activate"
    echo ""
    echo "To use Hatch environments, run:"
    echo "  hatch shell"
    echo ""
}

# Run the main function
main
