"""
CLI components specifically designed for automation systems like Autosys.

This module provides commands and utilities optimized for scheduled job execution,
with features like:
- Stateless operation
- Structured output formats (JSON)
- Standardized exit codes
- Environment variable configuration
- Job status reporting
"""

import json
import os
import sys
import time
from enum import IntEnum
from typing import Annotated, Any

import typer

from reference_python_project.utils.logging import configure_logging

# Create Typer app for automation commands
app = typer.Typer(
    name="automation",
    help="Commands optimized for automation and job scheduling systems like Autosys",
    add_completion=False,
)


# Define exit codes that Autosys can understand
class AutomationExitCode(IntEnum):
    """
    Standardized exit codes for automation systems.

    These align with common Autosys expectations and can be used
    to determine job success, failure, or retry conditions.
    """

    SUCCESS = 0
    CONFIG_ERROR = 1
    RUNTIME_ERROR = 2
    DEPENDENCY_ERROR = 3
    PERMISSION_ERROR = 4
    NETWORK_ERROR = 5
    TIMEOUT_ERROR = 6
    RETRY_NEEDED = 7
    UNKNOWN_ERROR = 255


def get_env_or_default(key: str, default: Any) -> Any:
    """Get value from environment variable or use default."""
    return os.environ.get(key, default)


def write_status_file(status: dict[str, Any], file_path: str | None = None) -> None:
    """
    Write job status information to a file.

    Args:
        status: Status information to write
        file_path: Path to write status to (defaults to AUTOSYS_STATUS_FILE env var)
    """
    if file_path is None:
        file_path = os.environ.get("AUTOSYS_STATUS_FILE")
        if not file_path:
            return

    try:
        with open(file_path, "w") as f:
            json.dump(status, f, indent=2)
    except (OSError, PermissionError) as e:
        print(f"Failed to write status file: {e}", file=sys.stderr)


@app.command()
def run_job(
    job_name: Annotated[str, typer.Argument(help="Name of the job to run")],
    config_file: Annotated[
        str | None, typer.Option("--config", "-c", help="Path to configuration file")
    ] = None,
    timeout: Annotated[int, typer.Option("--timeout", "-t", help="Job timeout in seconds")] = 3600,
    parameters: Annotated[
        list[str] | None, typer.Option("--param", "-p", help="Job parameters in key=value format")
    ] = None,
    output_format: Annotated[
        str, typer.Option("--output-format", "-o", help="Output format (text, json, or csv)")
    ] = "text",
    status_file: Annotated[
        str | None, typer.Option("--status-file", help="File to write job status information")
    ] = None,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose logging")
    ] = False,
) -> None:
    """
    Run a job in a way optimized for automation systems like Autosys.

    This command handles common automation requirements:
    - Configurable via environment variables or parameters
    - Provides detailed exit codes for job control systems
    - Writes status to a file for job monitoring
    - Handles timeouts gracefully
    """
    # Configure automation-friendly logging
    log_level = os.environ.get("AUTOSYS_LOG_LEVEL", "INFO")
    numeric_level = getattr(sys.modules["logging"], log_level, 20)  # Default to INFO (20)

    log_file = os.environ.get("AUTOSYS_LOG_FILE")
    configure_logging(
        level=numeric_level,
        json_format=output_format == "json",
        log_file=log_file,
        automation_mode=True,
    )

    # Record start time for job duration tracking
    start_time = time.time()

    # Parse parameters
    param_dict = {}
    if parameters:
        for param in parameters:
            if "=" in param:
                key, value = param.split("=", 1)
                param_dict[key.strip()] = value.strip()

    # Create initial status
    status = {
        "job_name": job_name,
        "start_time": start_time,
        "status": "RUNNING",
        "parameters": param_dict,
    }

    # Write initial status
    write_status_file(status, status_file)

    try:
        # This is where you would implement actual job logic
        # For example:
        #   - Call specific business logic modules
        #   - Process files
        #   - Run data transformations
        #   - etc.

        # For demonstration, we'll just print job information
        if output_format == "json":
            result = {
                "job_name": job_name,
                "parameters": param_dict,
                "result": "Job execution successful",
                "duration": time.time() - start_time,
            }
            print(json.dumps(result, indent=2))
        else:
            typer.echo(f"Job '{job_name}' executed successfully")
            typer.echo(f"Parameters: {param_dict}")
            typer.echo(f"Duration: {time.time() - start_time:.2f} seconds")

        # Update status file
        status.update(
            {
                "status": "COMPLETED",
                "end_time": time.time(),
                "duration": time.time() - start_time,
            }
        )
        write_status_file(status, status_file)

        # Exit with success code
        raise typer.Exit(code=AutomationExitCode.SUCCESS)

    except Exception as e:
        # Update status file with error information
        status.update(
            {
                "status": "FAILED",
                "error": str(e),
                "end_time": time.time(),
                "duration": time.time() - start_time,
            }
        )
        write_status_file(status, status_file)

        # Determine appropriate exit code based on exception type
        if "timeout" in str(e).lower():
            exit_code = AutomationExitCode.TIMEOUT_ERROR
        elif "permission" in str(e).lower():
            exit_code = AutomationExitCode.PERMISSION_ERROR
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            exit_code = AutomationExitCode.NETWORK_ERROR
        elif "config" in str(e).lower() or "parameter" in str(e).lower():
            exit_code = AutomationExitCode.CONFIG_ERROR
        elif "dependency" in str(e).lower() or "required" in str(e).lower():
            exit_code = AutomationExitCode.DEPENDENCY_ERROR
        else:
            exit_code = AutomationExitCode.RUNTIME_ERROR

        # Print error and exit with appropriate code
        if output_format == "json":
            error_info = {
                "error": str(e),
                "exit_code": int(exit_code),
                "job_name": job_name,
            }
            print(json.dumps(error_info), file=sys.stderr)
        else:
            typer.echo(f"Error executing job '{job_name}': {e}", err=True)

        raise typer.Exit(code=exit_code)


@app.command()
def check_dependencies(
    job_name: Annotated[str, typer.Argument(help="Name of the job to check dependencies for")],
    output_format: Annotated[
        str, typer.Option("--output-format", "-o", help="Output format (text, json)")
    ] = "text",
) -> None:
    """
    Check if all dependencies for a job are met.

    This command verifies that all required external dependencies
    (files, services, other jobs) are available before starting the main job.
    """
    # In a real implementation, you would check actual dependencies
    # For example:
    #   - Check if input files exist
    #   - Verify database connections
    #   - Check if dependent jobs completed successfully

    # For demonstration, we'll just report success
    if output_format == "json":
        result = {
            "job_name": job_name,
            "dependencies_met": True,
            "details": {
                "files_available": True,
                "services_available": True,
                "dependent_jobs_completed": True,
            },
        }
        print(json.dumps(result, indent=2))
    else:
        typer.echo(f"All dependencies for job '{job_name}' are met.")

    raise typer.Exit(code=AutomationExitCode.SUCCESS)


@app.command()
def report_status(
    job_id: Annotated[str, typer.Argument(help="ID of the job to report status for")],
    status_file: Annotated[
        str | None, typer.Option("--status-file", help="File to read job status information from")
    ] = None,
    output_format: Annotated[
        str, typer.Option("--output-format", "-o", help="Output format (text, json)")
    ] = "text",
) -> None:
    """
    Report the current status of a job.

    This command reads the status file created by a running or completed job
    and outputs the information in the requested format.
    """
    status_path = status_file
    if not status_path:
        status_path = os.environ.get("AUTOSYS_STATUS_FILE")
        if not status_path:
            if output_format == "json":
                result = {
                    "error": "Status file not specified and AUTOSYS_STATUS_FILE not set",
                }
                print(json.dumps(result), file=sys.stderr)
            else:
                typer.echo(
                    "Error: Status file not specified and AUTOSYS_STATUS_FILE not set", err=True
                )
            raise typer.Exit(code=AutomationExitCode.CONFIG_ERROR)

    try:
        with open(status_path) as f:
            status = json.load(f)

        if output_format == "json":
            print(json.dumps(status, indent=2))
        else:
            typer.echo(f'Job: {status.get("job_name", "Unknown")}')
            typer.echo(f'Status: {status.get("status", "Unknown")}')
            typer.echo(f'Start Time: {status.get("start_time", "Unknown")}')
            if "end_time" in status:
                typer.echo(f'End Time: {status.get("end_time")}')
            if "duration" in status:
                typer.echo(f'Duration: {status.get("duration"):.2f} seconds')
            if "error" in status:
                typer.echo(f'Error: {status.get("error")}')

        # Exit with success
        raise typer.Exit(code=AutomationExitCode.SUCCESS)

    except (OSError, json.JSONDecodeError) as e:
        if output_format == "json":
            result = {
                "error": f"Failed to read status file: {e}",
            }
            print(json.dumps(result), file=sys.stderr)
        else:
            typer.echo(f"Error: Failed to read status file: {e}", err=True)
        raise typer.Exit(code=AutomationExitCode.RUNTIME_ERROR)


if __name__ == "__main__":
    app()
