# Interactive Project Initialization Wizard Runner for Windows
# This script runs the interactive wizard with proper error handling
# and environment detection.

# Enable strict mode
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Determine script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Function to display formatted messages
function Write-ColorMessage {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter(Mandatory = $true)]
        [ValidateSet("Info", "Success", "Error", "Warning")]
        [string]$Type
    )

    $color = switch ($Type) {
        "Info" { "Cyan" }
        "Success" { "Green" }
        "Error" { "Red" }
        "Warning" { "Yellow" }
    }

    Write-Host "[$Type]: " -ForegroundColor $color -NoNewline
    Write-Host $Message
}

try {
    # Change to project root
    Set-Location $ProjectRoot

    # Check for Python
    $pythonCmd = $null
    if (Get-Command "python" -ErrorAction SilentlyContinue) {
        $pythonCmd = "python"
    } elseif (Get-Command "python3" -ErrorAction SilentlyContinue) {
        $pythonCmd = "python3"
    } elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
        $pythonCmd = "py"
    } else {
        Write-ColorMessage "Python is not installed or not in PATH" "Error"
        exit 1
    }

    # Check Python version
    $pythonVersion = & $pythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    $versionParts = $pythonVersion.Split('.')
    if ([int]$versionParts[0] -lt 3 -or ([int]$versionParts[0] -eq 3 -and [int]$versionParts[1] -lt 8)) {
        Write-ColorMessage "Python 3.8 or newer is required (found $pythonVersion)" "Error"
        exit 1
    }

    Write-ColorMessage "Python $pythonVersion detected" "Info"

    # Check for virtual environment
    if (Test-Path ".venv") {
        Write-ColorMessage "Found virtual environment at .venv" "Info"
        if (Test-Path ".venv\Scripts\Activate.ps1") {
            Write-ColorMessage "Activating virtual environment" "Info"
            & ".venv\Scripts\Activate.ps1"
        } else {
            Write-ColorMessage "Could not activate virtual environment, continuing anyway" "Warning"
        }
    }

    # Run the interactive wizard
    Write-ColorMessage "Starting interactive wizard..." "Info"

    # Check if WIZARD_SCRIPT environment variable is set (for testing)
    if ($env:WIZARD_SCRIPT) {
        Write-ColorMessage "Using custom wizard script: $env:WIZARD_SCRIPT" "Info"
        & $pythonCmd "$env:WIZARD_SCRIPT" $args
    } else {
        & $pythonCmd "$ScriptDir\run_interactive_wizard.py" $args
    }

    if ($LASTEXITCODE -eq 0) {
        Write-ColorMessage "Wizard completed successfully!" "Success"
    } else {
        Write-ColorMessage "Wizard failed with exit code $LASTEXITCODE" "Error"
        exit $LASTEXITCODE
    }
} catch {
    Write-ColorMessage "An error occurred: $_" "Error"
    exit 1
}
