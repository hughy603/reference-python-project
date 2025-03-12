# PowerShell script to run tox tests on multiple Python versions
# This script helps manage multi-version testing with tox

param(
    [Parameter()]
    [string]$Environment = "",

    [Parameter()]
    [switch]$Parallel,

    [Parameter()]
    [switch]$ListEnvs,

    [Parameter()]
    [switch]$Recreate,

    [Parameter()]
    [string[]]$AdditionalArgs
)

# Check if tox is installed
try {
    tox --version | Out-Null
}
catch {
    Write-Error "Tox is not installed. Please install it with: pip install tox"
    exit 1
}

# List available environments if requested
if ($ListEnvs) {
    Write-Host "Available tox environments:"
    tox list
    exit 0
}

# Build the command
$toxArgs = @()

# Add environment if specified
if ($Environment) {
    $toxArgs += "-e", $Environment
}

# Add parallel flag if requested
if ($Parallel) {
    $toxArgs += "--parallel"
}

# Add recreate flag if requested
if ($Recreate) {
    $toxArgs += "--recreate"
}

# Add any additional arguments
if ($AdditionalArgs) {
    $toxArgs += $AdditionalArgs
}

# Display the command being run
$cmdDisplay = "tox $($toxArgs -join ' ')"
Write-Host "Running: $cmdDisplay" -ForegroundColor Cyan

# Run tox with all specified arguments
tox $toxArgs

# Check return code
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tox tests failed with exit code $LASTEXITCODE" -ForegroundColor Red
}
else {
    Write-Host "Tox tests completed successfully!" -ForegroundColor Green
}

exit $LASTEXITCODE
