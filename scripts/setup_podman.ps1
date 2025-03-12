#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Setup script for Podman on Windows 11
.DESCRIPTION
    This script helps set up Podman as a Docker Desktop alternative for Windows 11 users.
    It installs Podman, configures it to work with WSL, and sets up the environment.
.NOTES
    Run this script as Administrator in PowerShell
#>

$ErrorActionPreference = "Stop"
$VerbosePreference = "Continue"

Write-Host "======================================================="
Write-Host "  Podman Setup for Windows 11"
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
    Write-Host "WSL not found. Please run the windows_setup.ps1 script first." -ForegroundColor Yellow
    exit 1
}
else {
    Write-Host "WSL is already installed." -ForegroundColor Green
}

# Install Podman for Windows
Write-Host "Checking for Podman..." -ForegroundColor Cyan
if (!(Check-Command podman)) {
    Write-Host "Podman not found. Installing..." -ForegroundColor Yellow
    try {
        if (Check-Command winget) {
            winget install -e --id=RedHat.Podman

            # Need to refresh environment to recognize podman
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

            Write-Host "Podman installation completed. You may need to restart your PowerShell session." -ForegroundColor Green
        }
        else {
            Write-Host "Winget not found. Please install Podman manually from: https://github.com/containers/podman/releases" -ForegroundColor Yellow
            exit 1
        }
    }
    catch {
        Write-Error "Failed to install Podman: $_"
        exit 1
    }
}
else {
    Write-Host "Podman is already installed." -ForegroundColor Green
}

# Initialize Podman Machine if not already done
Write-Host "Initializing Podman machine..." -ForegroundColor Cyan
try {
    $podmanMachineList = podman machine list
    if ($podmanMachineList -notmatch "podman-machine-default.*running") {
        podman machine init
        podman machine start
        Write-Host "Podman machine initialized and started." -ForegroundColor Green
    }
    else {
        Write-Host "Podman machine is already running." -ForegroundColor Green
    }
}
catch {
    Write-Error "Failed to initialize Podman machine: $_"
    exit 1
}

# Configure aliases to make podman compatible with docker commands
Write-Host "Setting up docker command compatibility..." -ForegroundColor Cyan
try {
    # Create or update PowerShell profile
    if (-not (Test-Path $PROFILE)) {
        New-Item -Path $PROFILE -ItemType File -Force | Out-Null
    }

    $profileContent = Get-Content $PROFILE -ErrorAction SilentlyContinue
    $aliasLine = "Set-Alias -Name docker -Value podman"

    if ($profileContent -notcontains $aliasLine) {
        Add-Content -Path $PROFILE -Value "`n# Alias docker to podman for Docker compatibility"
        Add-Content -Path $PROFILE -Value $aliasLine
        Write-Host "Added docker alias to PowerShell profile at: $PROFILE" -ForegroundColor Green
        Write-Host "Restart your PowerShell session or run '. `$PROFILE' to apply changes." -ForegroundColor Yellow
    }
    else {
        Write-Host "Docker alias already configured in PowerShell profile." -ForegroundColor Green
    }
}
catch {
    Write-Error "Failed to set up Docker compatibility: $_"
    exit 1
}

# Verify installation by testing a simple container
Write-Host "Testing Podman installation..." -ForegroundColor Cyan
try {
    podman run --rm hello-world
    Write-Host "Podman test successful!" -ForegroundColor Green
}
catch {
    Write-Error "Podman test failed: $_"
    exit 1
}

# Setup complete
Write-Host ""
Write-Host "======================================================="
Write-Host "Podman setup completed!" -ForegroundColor Green
Write-Host "======================================================="
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Restart your PowerShell session to use the docker alias"
Write-Host "2. Test running containers with: podman run --rm hello-world"
Write-Host "3. Build images with: podman build -t myapp:latest ."
Write-Host "4. For a GUI, consider installing Podman Desktop: https://podman-desktop.io/"
Write-Host ""
Write-Host "For more details, see CONTAINER_GUIDE.md"
