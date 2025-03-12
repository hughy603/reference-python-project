#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Setup script for Windows 11 development environment
.DESCRIPTION
    This script helps set up a Windows 11 development environment for the reference Python project
    without requiring Docker Desktop. It installs and configures WSL, Python, and development tools.
.NOTES
    Run this script as Administrator in PowerShell
#>

$ErrorActionPreference = "Stop"
$VerbosePreference = "Continue"

Write-Host "======================================================="
Write-Host "  Windows 11 Development Environment Setup"
Write-Host "======================================================="
Write-Host ""

function Check-Command {
    param (
        [string]$CommandName
    )
    return (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script must be run as Administrator. Right-click PowerShell and select 'Run as Administrator'."
    exit 1
}

# Check for WSL
Write-Host "Checking for Windows Subsystem for Linux..." -ForegroundColor Cyan
if (!(Check-Command wsl)) {
    Write-Host "WSL not found. Installing..." -ForegroundColor Yellow
    try {
        Write-Host "Installing WSL..."
        wsl --install
        Write-Host "WSL installation initiated. Your system will need to restart." -ForegroundColor Green
        Write-Host "After restart, continue setup by running this script again." -ForegroundColor Green
        exit 0
    }
    catch {
        Write-Error "Failed to install WSL: $_"
        exit 1
    }
}
else {
    Write-Host "WSL is already installed." -ForegroundColor Green
}

# Check Ubuntu installation
Write-Host "Checking for Ubuntu distribution..." -ForegroundColor Cyan
$hasUbuntu = wsl --list | Select-String -Pattern "Ubuntu" -Quiet
if (-not $hasUbuntu) {
    Write-Host "Ubuntu not found. Installing..." -ForegroundColor Yellow
    try {
        wsl --install -d Ubuntu
        Write-Host "Ubuntu installation initiated. Please complete the setup in the Ubuntu window that opens." -ForegroundColor Green
        Write-Host "After setting up Ubuntu, run this script again." -ForegroundColor Green
        exit 0
    }
    catch {
        Write-Error "Failed to install Ubuntu: $_"
        exit 1
    }
}
else {
    Write-Host "Ubuntu is already installed." -ForegroundColor Green
}

# Check for VS Code
Write-Host "Checking for Visual Studio Code..." -ForegroundColor Cyan
if (!(Check-Command code)) {
    Write-Host "Visual Studio Code not found. Installing..." -ForegroundColor Yellow
    try {
        # Using winget to install VSCode
        if (Check-Command winget) {
            winget install Microsoft.VisualStudioCode
        }
        else {
            Write-Error "Winget not found. Please install Visual Studio Code manually."
            exit 1
        }
    }
    catch {
        Write-Error "Failed to install Visual Studio Code: $_"
        exit 1
    }
}
else {
    Write-Host "Visual Studio Code is already installed." -ForegroundColor Green
}

# Install VS Code WSL Extension
Write-Host "Installing VS Code WSL Extension..." -ForegroundColor Cyan
code --install-extension ms-vscode-remote.remote-wsl

# Install Git if not already installed
Write-Host "Checking for Git..." -ForegroundColor Cyan
if (!(Check-Command git)) {
    Write-Host "Git not found. Installing..." -ForegroundColor Yellow
    try {
        # Using winget to install Git
        if (Check-Command winget) {
            winget install Git.Git
        }
        else {
            Write-Error "Winget not found. Please install Git manually."
            exit 1
        }
    }
    catch {
        Write-Error "Failed to install Git: $_"
        exit 1
    }
}
else {
    Write-Host "Git is already installed." -ForegroundColor Green
}

# Setup WSL environment
Write-Host "Setting up WSL environment..." -ForegroundColor Cyan
try {
    wsl -d Ubuntu -e bash -c "sudo apt update && sudo apt upgrade -y"
    wsl -d Ubuntu -e bash -c "sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip git curl"
    wsl -d Ubuntu -e bash -c "sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1"
    wsl -d Ubuntu -e bash -c "sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1"
    wsl -d Ubuntu -e bash -c "pip install --user hatch pre-commit"
}
catch {
    Write-Error "Failed to set up WSL environment: $_"
    Write-Host "You may need to manually complete the setup using the instructions in WINDOWS_SETUP.md" -ForegroundColor Yellow
}

# Setup complete
Write-Host ""
Write-Host "======================================================="
Write-Host "Development environment setup completed!" -ForegroundColor Green
Write-Host "======================================================="
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Open WSL terminal: wsl"
Write-Host "2. Navigate to your project directory"
Write-Host "3. Open with VS Code: code ."
Write-Host "4. Follow the remaining instructions in WINDOWS_SETUP.md"
Write-Host ""
Write-Host "For more details, see WINDOWS_SETUP.md"
