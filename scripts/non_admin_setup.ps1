<#
.SYNOPSIS
    Non-administrative setup script for Windows AWS development environment
.DESCRIPTION
    This script sets up an AWS development environment on Windows without
    requiring administrative privileges. It installs tools and configures
    the environment for AWS development using portable installations.
.NOTES
    Run this script from PowerShell
#>

$ErrorActionPreference = "Stop"
$VerbosePreference = "Continue"

Write-Host "======================================================="
Write-Host "  Non-Administrative AWS Development Environment Setup"
Write-Host "======================================================="
Write-Host ""

function Check-Command {
    param (
        [string]$CommandName
    )
    return (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

# Create portable apps directory
$portableAppsDir = Join-Path $env:USERPROFILE "portable-apps"
if (-not (Test-Path $portableAppsDir)) {
    Write-Host "Creating portable apps directory..." -ForegroundColor Cyan
    New-Item -Path $portableAppsDir -ItemType Directory -Force | Out-Null
}

# Add portable apps to user PATH
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$portableAppsDir*") {
    Write-Host "Adding portable apps to PATH..." -ForegroundColor Cyan
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$portableAppsDir", "User")
    # Update current session path
    $env:Path = "$env:Path;$portableAppsDir"
}

# Check for existing WSL
$hasWSL = $false
if (Check-Command wsl) {
    Write-Host "WSL is already installed." -ForegroundColor Green
    $hasWSL = $true
} else {
    Write-Host "WSL is not installed." -ForegroundColor Yellow
    Write-Host "This script will use portable tools that don't require WSL." -ForegroundColor Yellow
    Write-Host "If you want to use WSL, please ask your administrator to install it." -ForegroundColor Yellow
}

# Install AWS CLI (portable)
$awsCliPortablePath = Join-Path $portableAppsDir "aws-cli"
if (-not (Test-Path (Join-Path $awsCliPortablePath "aws.exe"))) {
    Write-Host "Installing AWS CLI (portable version)..." -ForegroundColor Cyan

    # Create temporary directory for download
    $tempDir = Join-Path $env:TEMP "aws-cli-temp"
    if (-not (Test-Path $tempDir)) {
        New-Item -Path $tempDir -ItemType Directory -Force | Out-Null
    }

    # Download AWS CLI
    $awsCliUrl = "https://awscli.amazonaws.com/AWSCLIV2.zip"
    $zipFile = Join-Path $tempDir "AWSCLIV2.zip"

    try {
        Invoke-WebRequest -Uri $awsCliUrl -OutFile $zipFile

        # Extract to portable directory
        Expand-Archive -Path $zipFile -DestinationPath $tempDir -Force

        # Create AWS CLI portable directory
        if (-not (Test-Path $awsCliPortablePath)) {
            New-Item -Path $awsCliPortablePath -ItemType Directory -Force | Out-Null
        }

        # Copy necessary files (AWS CLI portable mode)
        Copy-Item -Path "$tempDir\aws\dist\*" -Destination $awsCliPortablePath -Recurse -Force

        # Create aws.cmd wrapper
        $cmdWrapper = @"
@echo off
SET SCRIPT_DIR=%~dp0
"%SCRIPT_DIR%\aws.exe" %*
"@
        Set-Content -Path (Join-Path $portableAppsDir "aws.cmd") -Value $cmdWrapper

        # Clean up temp directory
        Remove-Item -Path $tempDir -Recurse -Force

        Write-Host "AWS CLI installed in portable mode." -ForegroundColor Green
    } catch {
        Write-Error "Failed to install AWS CLI: $_"
    }
} else {
    Write-Host "AWS CLI is already installed." -ForegroundColor Green
}

# Install Python if not available
if (-not (Check-Command python)) {
    Write-Host "Installing Python (portable version)..." -ForegroundColor Cyan

    $pythonPortablePath = Join-Path $portableAppsDir "python"
    $pythonUrl = "https://www.python.org/ftp/python/3.13.0/python-3.13.0-embed-amd64.zip"
    $zipFile = Join-Path $env:TEMP "python-portable.zip"

    try {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $zipFile

        # Extract to portable directory
        if (-not (Test-Path $pythonPortablePath)) {
            New-Item -Path $pythonPortablePath -ItemType Directory -Force | Out-Null
        }

        Expand-Archive -Path $zipFile -DestinationPath $pythonPortablePath -Force

        # Configure python to use pip
        $pthFile = Get-ChildItem -Path $pythonPortablePath -Filter "python*._pth" | Select-Object -First 1
        if ($pthFile) {
            $pthContent = Get-Content -Path $pthFile.FullName
            if ($pthContent -notcontains "import site") {
                Add-Content -Path $pthFile.FullName -Value "import site"
            }
        }

        # Get pip
        $getPipUrl = "https://bootstrap.pypa.io/get-pip.py"
        $getPipFile = Join-Path $env:TEMP "get-pip.py"
        Invoke-WebRequest -Uri $getPipUrl -OutFile $getPipFile

        # Install pip
        & "$pythonPortablePath\python.exe" $getPipFile

        # Create wrapper scripts
        $pythonCmd = @"
@echo off
"%~dp0\python\python.exe" %*
"@
        Set-Content -Path (Join-Path $portableAppsDir "python.cmd") -Value $pythonCmd

        $pipCmd = @"
@echo off
"%~dp0\python\python.exe" -m pip %*
"@
        Set-Content -Path (Join-Path $portableAppsDir "pip.cmd") -Value $pipCmd

        # Clean up
        Remove-Item -Path $zipFile -Force
        Remove-Item -Path $getPipFile -Force

        Write-Host "Python installed in portable mode." -ForegroundColor Green
    } catch {
        Write-Error "Failed to install Python: $_"
    }
} else {
    Write-Host "Python is already available." -ForegroundColor Green
}

# Install AWS CDK if not available
if (-not (Check-Command cdk)) {
    Write-Host "Installing AWS CDK..." -ForegroundColor Cyan
    try {
        & pip install --user aws-cdk-lib
        $cdkCmd = @"
@echo off
"%USERPROFILE%\AppData\Roaming\Python\Python310\Scripts\cdk.exe" %*
"@
        Set-Content -Path (Join-Path $portableAppsDir "cdk.cmd") -Value $cdkCmd
        Write-Host "AWS CDK installed." -ForegroundColor Green
    } catch {
        Write-Error "Failed to install AWS CDK: $_"
    }
} else {
    Write-Host "AWS CDK is already available." -ForegroundColor Green
}

# Install Node.js (portable version) if not available
if (-not (Check-Command node)) {
    Write-Host "Installing Node.js (portable version)..." -ForegroundColor Cyan

    $nodePortablePath = Join-Path $portableAppsDir "nodejs"
    $nodeUrl = "https://nodejs.org/dist/v18.16.1/node-v18.16.1-win-x64.zip"
    $zipFile = Join-Path $env:TEMP "node-portable.zip"

    try {
        Invoke-WebRequest -Uri $nodeUrl -OutFile $zipFile

        # Extract to portable directory
        if (-not (Test-Path $nodePortablePath)) {
            New-Item -Path $nodePortablePath -ItemType Directory -Force | Out-Null
        }

        Expand-Archive -Path $zipFile -DestinationPath $portableAppsDir -Force
        $extractedFolder = Get-ChildItem -Path $portableAppsDir -Filter "node-v*-win-x64" | Select-Object -First 1
        if ($extractedFolder) {
            Move-Item -Path $extractedFolder.FullName -Destination $nodePortablePath -Force
        }

        # Create wrapper scripts
        $nodeCmd = @"
@echo off
"%~dp0\nodejs\node.exe" %*
"@
        Set-Content -Path (Join-Path $portableAppsDir "node.cmd") -Value $nodeCmd

        $npmCmd = @"
@echo off
"%~dp0\nodejs\npm.cmd" %*
"@
        Set-Content -Path (Join-Path $portableAppsDir "npm.cmd") -Value $npmCmd

        # Clean up
        Remove-Item -Path $zipFile -Force

        Write-Host "Node.js installed in portable mode." -ForegroundColor Green
    } catch {
        Write-Error "Failed to install Node.js: $_"
    }
} else {
    Write-Host "Node.js is already available." -ForegroundColor Green
}

# Install Terraform (portable version) if not available
if (-not (Check-Command terraform)) {
    Write-Host "Installing Terraform (portable version)..." -ForegroundColor Cyan

    $terraformPath = Join-Path $portableAppsDir "terraform.exe"
    $terraformUrl = "https://releases.hashicorp.com/terraform/1.5.7/terraform_1.5.7_windows_amd64.zip"
    $zipFile = Join-Path $env:TEMP "terraform.zip"

    try {
        Invoke-WebRequest -Uri $terraformUrl -OutFile $zipFile

        # Extract terraform.exe to portable directory
        Expand-Archive -Path $zipFile -DestinationPath $portableAppsDir -Force

        # Clean up
        Remove-Item -Path $zipFile -Force

        Write-Host "Terraform installed in portable mode." -ForegroundColor Green
    } catch {
        Write-Error "Failed to install Terraform: $_"
    }
} else {
    Write-Host "Terraform is already available." -ForegroundColor Green
}

# Install Git (portable version) if not available
if (-not (Check-Command git)) {
    Write-Host "Consider installing Git for Windows (portable edition):" -ForegroundColor Yellow
    Write-Host "Download from: https://github.com/git-for-windows/git/releases" -ForegroundColor Yellow
    Write-Host "Choose the portable version (e.g., PortableGit-*.exe)" -ForegroundColor Yellow
    Write-Host "Extract to: $portableAppsDir\git" -ForegroundColor Yellow
    Write-Host "Then add the bin directory to your PATH manually" -ForegroundColor Yellow
} else {
    Write-Host "Git is already available." -ForegroundColor Green
}

# Configure AWS CLI
if (Check-Command aws) {
    Write-Host "Do you want to configure AWS CLI? (y/n)" -ForegroundColor Cyan
    $configureAws = Read-Host
    if ($configureAws -eq "y") {
        # Configure AWS CLI
        Write-Host "Configuring AWS CLI..." -ForegroundColor Cyan
        aws configure
        Write-Host "AWS CLI configured." -ForegroundColor Green
    }
}

# Setup SAM CLI (portable option)
Write-Host "AWS SAM CLI requires administrator privileges to install." -ForegroundColor Yellow
Write-Host "Consider using AWS Cloud9 or AWS CloudShell as alternatives." -ForegroundColor Yellow

# Create a user-level VSCode workspace configuration
$vsCodeWorkspacesDir = Join-Path $env:USERPROFILE "aws-workspaces"
if (-not (Test-Path $vsCodeWorkspacesDir)) {
    Write-Host "Creating VSCode workspaces directory..." -ForegroundColor Cyan
    New-Item -Path $vsCodeWorkspacesDir -ItemType Directory -Force | Out-Null
}

# Complete setup
Write-Host ""
Write-Host "======================================================="
Write-Host "AWS Development Environment Setup Completed!" -ForegroundColor Green
Write-Host "======================================================="
Write-Host ""
Write-Host "Tools installed in: $portableAppsDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "AWS Tools Available:" -ForegroundColor Cyan
Write-Host "- AWS CLI: aws --version" -ForegroundColor White
if (Check-Command cdk) { Write-Host "- AWS CDK: cdk --version" -ForegroundColor White }
if (Check-Command terraform) { Write-Host "- Terraform: terraform --version" -ForegroundColor White }
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart your terminal to ensure PATH changes take effect" -ForegroundColor White
Write-Host "2. Run 'aws configure' if you haven't already" -ForegroundColor White
Write-Host "3. See AWS_DEVELOPMENT.md for more information" -ForegroundColor White
Write-Host ""
