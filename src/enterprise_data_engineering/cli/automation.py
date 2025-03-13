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
import logging
import os
import sys
import time
from enum import IntEnum
from typing import Annotated, Any

import typer

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
    """Get value from environment variable or return default."""
    return os.getenv(key, default)


def write_status_file(status: dict[str, Any], file_path: str | None = None) -> None:
    """
    Write job status information to a file.

    Args:
        status: Dictionary containing status information
        file_path: Path to write status file (defaults to job_status.json in current directory)
    """
    if file_path is None:
        file_path = "job_status.json"

    try:
        with open(file_path, "w") as f:
            json.dump(status, f, indent=2)
        logger = logging.getLogger(__name__)
        logger.info(f"Status information written to {file_path}")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to write status file: {e}")


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
    Run a scheduled job with features optimized for automation systems.

    This command handles common automation system requirements like:
    - Job status reporting
    - Timeout handling
    - Standardized exit codes
    - Parameter parsing

    Examples:
        Run a simple job:
        $ ede automation run-job daily-data-load

        Run with config and parameters:
        $ ede automation run-job monthly-report --config=configs/report.json --param="date=2023-01-01"
    """
    # Configure logging with appropriate level
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Initialize status tracking
    status = {
        "job_name": job_name,
        "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "parameters": {},
        "status": "RUNNING",
        "exit_code": None,
    }

    # Process parameters into a dictionary
    if parameters:
        for param in parameters:
            if "=" in param:
                key, value = param.split("=", 1)
                status["parameters"][key.strip()] = value.strip()
            else:
                logger.warning(f"Ignoring malformed parameter (missing '='): {param}")

    try:
        logger.info(f"Starting job: {job_name}")
        if config_file and not os.path.exists(config_file):
            logger.error(f"Config file not found: {config_file}")
            status["status"] = "FAILED"
            status["error"] = f"Config file not found: {config_file}"
            status["exit_code"] = AutomationExitCode.CONFIG_ERROR
            sys.exit(AutomationExitCode.CONFIG_ERROR)

        # Here you would implement the actual job execution logic based on job_name
        # For demo purposes, we'll just simulate a successful job
        logger.info(f"Job {job_name} is executing...")

        # Simulate some processing time
        time.sleep(2)

        # Generate sample output based on the requested format
        if output_format == "json":
            result = {"result": "success", "job_name": job_name, "records_processed": 42}
            print(json.dumps(result, indent=2))
        elif output_format == "csv":
            print("job_name,status,records_processed")
            print(f"{job_name},success,42")
        else:  # default to text
            print(f"Job {job_name} completed successfully. Processed 42 records.")

        # Update status to reflect successful completion
        status["status"] = "COMPLETED"
        status["exit_code"] = AutomationExitCode.SUCCESS
        status["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")

        # Write status file if requested
        if status_file:
            write_status_file(status, status_file)

        logger.info(f"Job {job_name} completed successfully")
        sys.exit(AutomationExitCode.SUCCESS)

    except Exception as e:
        logger.exception(f"Job {job_name} failed with error: {e}")

        # Update status to reflect failure
        status["status"] = "FAILED"
        status["error"] = str(e)
        status["exit_code"] = AutomationExitCode.RUNTIME_ERROR
        status["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")

        # Write status file if requested
        if status_file:
            write_status_file(status, status_file)

        sys.exit(AutomationExitCode.RUNTIME_ERROR)


@app.command()
def check_dependencies(
    job_name: Annotated[str, typer.Argument(help="Name of the job to check dependencies for")],
    output_format: Annotated[
        str, typer.Option("--output-format", "-o", help="Output format (text, json)")
    ] = "text",
) -> None:
    """
    Check if all dependencies for a job are available.

    This is useful for validating that a job can run successfully before triggering it.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Checking dependencies for job: {job_name}")

    # In a real implementation, you'd check for actual dependencies
    # This is a simplified example
    dependencies = [
        {"name": "database", "status": "available"},
        {"name": "storage", "status": "available"},
        {"name": "api", "status": "available"},
    ]

    if output_format == "json":
        result = {
            "job_name": job_name,
            "dependencies": dependencies,
            "all_available": all(dep["status"] == "available" for dep in dependencies),
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"Dependency check for job '{job_name}':")
        for dep in dependencies:
            print(f"  - {dep['name']}: {dep['status']}")

        all_available = all(dep["status"] == "available" for dep in dependencies)
        print(f"\nAll dependencies available: {all_available}")

    # Exit with appropriate code
    if all(dep["status"] == "available" for dep in dependencies):
        sys.exit(AutomationExitCode.SUCCESS)
    else:
        sys.exit(AutomationExitCode.DEPENDENCY_ERROR)


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
    Report on the status of a previously run job.

    This can be used by orchestration systems to check job completion status.
    """
    logger = logging.getLogger(__name__)

    # Determine which status file to use
    if status_file is None:
        status_file = "job_status.json"

    try:
        # Try to read the status file
        if not os.path.exists(status_file):
            logger.error(f"Status file not found: {status_file}")
            if output_format == "json":
                print(json.dumps({"error": f"Status file not found: {status_file}"}))
            else:
                print(f"Error: Status file not found: {status_file}")
            sys.exit(AutomationExitCode.CONFIG_ERROR)

        with open(status_file) as f:
            status = json.load(f)

        # Report status in requested format
        if output_format == "json":
            print(json.dumps(status, indent=2))
        else:
            print(f"Job: {status.get('job_name', 'unknown')}")
            print(f"Status: {status.get('status', 'unknown')}")
            print(f"Started: {status.get('start_time', 'unknown')}")
            print(f"Ended: {status.get('end_time', 'unknown')}")

            if "error" in status:
                print(f"Error: {status['error']}")

            if status.get("parameters"):
                print("\nParameters:")
                for key, value in status["parameters"].items():
                    print(f"  {key}: {value}")

        # Set exit code based on job status
        if status.get("exit_code") is not None:
            sys.exit(int(status["exit_code"]))
        elif status.get("status") == "COMPLETED":
            sys.exit(AutomationExitCode.SUCCESS)
        else:
            sys.exit(AutomationExitCode.UNKNOWN_ERROR)

    except Exception as e:
        logger.exception(f"Error reporting status: {e}")
        if output_format == "json":
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error reporting status: {e}")
        sys.exit(AutomationExitCode.RUNTIME_ERROR)
