# PowerShell script to run Python 3.12 with optimizations
# This script can be used to run Python scripts with various optimization levels

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$ScriptPath,

    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ScriptArgs,

    [Parameter()]
    [ValidateSet(0, 1, 2)]
    [int]$OptimizationLevel = 0,

    [Parameter()]
    [switch]$Benchmark,

    [Parameter()]
    [int]$Iterations = 5
)

function CheckPythonVersion {
    # Check if Python is available and its version
    try {
        $pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"

        if ($pythonVersion -lt "3.12") {
            Write-Warning "This script is designed for Python 3.12 or newer."
            Write-Warning "Current Python version: $pythonVersion"
            return $false
        }

        return $true
    }
    catch {
        Write-Error "Python is not available in the PATH."
        return $false
    }
}

function RunScript {
    param(
        [string]$ScriptPath,
        [string[]]$ScriptArgs,
        [int]$OptimizationLevel
    )

    $cmd = "python"

    # Add optimization flags
    if ($OptimizationLevel -ge 1) {
        $cmd += " -O"  # Skip assert statements
    }
    if ($OptimizationLevel -ge 2) {
        $cmd += " -O"  # Second -O skips docstrings too
    }

    $cmd += " `"$ScriptPath`""

    # Add script arguments
    foreach ($arg in $ScriptArgs) {
        $cmd += " `"$arg`""
    }

    Write-Host "Running: $cmd"
    Write-Host "Optimization level: $OptimizationLevel"

    # Set environment variable for optimization
    $env:PYTHONOPTIMIZE = $OptimizationLevel

    # Measure execution time
    $startTime = Get-Date

    # Run the script
    Invoke-Expression $cmd
    $returnCode = $LASTEXITCODE

    $elapsedTime = (Get-Date) - $startTime
    Write-Host "Script completed in $($elapsedTime.TotalSeconds) seconds with return code $returnCode"

    return @{
        ReturnCode = $returnCode
        ElapsedTime = $elapsedTime.TotalSeconds
    }
}

function BenchmarkScript {
    param(
        [string]$ScriptPath,
        [string[]]$ScriptArgs,
        [int]$OptimizationLevel,
        [int]$Iterations
    )

    Write-Host "Benchmarking with $Iterations iterations..."

    $times = @()

    for ($i = 0; $i -lt $Iterations; $i++) {
        Write-Host "Run $($i+1)/$Iterations: " -NoNewline
        $result = RunScript -ScriptPath $ScriptPath -ScriptArgs $ScriptArgs -OptimizationLevel $OptimizationLevel
        $times += $result.ElapsedTime
        Write-Host "$($result.ElapsedTime) seconds"
    }

    $avgTime = ($times | Measure-Object -Average).Average
    $minTime = ($times | Measure-Object -Minimum).Minimum
    $maxTime = ($times | Measure-Object -Maximum).Maximum
    $totalTime = ($times | Measure-Object -Sum).Sum

    Write-Host "`nBenchmark Results:"
    Write-Host "  Average time: $avgTime seconds"
    Write-Host "  Minimum time: $minTime seconds"
    Write-Host "  Maximum time: $maxTime seconds"
    Write-Host "  Total time:   $totalTime seconds"
}

# Main script execution
if (-not (CheckPythonVersion)) {
    exit 1
}

if (-not (Test-Path $ScriptPath)) {
    Write-Error "Script file not found: $ScriptPath"
    exit 1
}

if ($Benchmark) {
    BenchmarkScript -ScriptPath $ScriptPath -ScriptArgs $ScriptArgs -OptimizationLevel $OptimizationLevel -Iterations $Iterations
}
else {
    $result = RunScript -ScriptPath $ScriptPath -ScriptArgs $ScriptArgs -OptimizationLevel $OptimizationLevel
    exit $result.ReturnCode
}
