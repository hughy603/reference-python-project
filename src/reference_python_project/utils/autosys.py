"""
Utilities for working with Autosys Jobs and JIL (Job Information Language).

This module provides functions for:
1. Generating Autosys JIL definitions programmatically
2. Parsing JIL files
3. Converting between different job scheduling formats
4. Validation of job definitions
"""

import os
import re
import shlex
import subprocess
from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar

# Define a type variable for kwargs
KwargsT = TypeVar("KwargsT", bound=Mapping[str, Any])


class JobType(str, Enum):
    """Supported Autosys job types."""

    COMMAND = "cmd"
    BOX = "box"
    FILE_WATCHER = "fw"
    FILE_TRIGGER = "ft"


class JobStatus(str, Enum):
    """Common Autosys job status values."""

    ACTIVATED = "ACTIVATED"
    INACTIVE = "INACTIVE"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    TERMINATED = "TERMINATED"
    ON_ICE = "ON_ICE"
    ON_HOLD = "ON_HOLD"


class Condition(str, Enum):
    """Job condition types for dependencies."""

    SUCCESS = "success"
    FAILURE = "failure"
    DONE = "done"
    NOTRUNNING = "notrunning"
    TERMINATED = "terminated"


class NotificationMethod(str, Enum):
    """Supported notification methods."""

    EMAIL = "email"
    ALERT = "alert"
    SNMP = "snmp"
    JMS = "jms"


def jil_escape(value: str) -> str:
    """
    Escape special characters in JIL values.

    Args:
        value: The string value to escape

    Returns:
        Escaped string suitable for JIL
    """
    # Escape backslashes first
    value = value.replace("\\", "\\\\")

    # Escape double quotes
    value = value.replace('"', '\\"')

    # Handle special characters
    if any(c in value for c in "{}[]():;,"):
        value = f'"{value}"'

    return value


def create_jil_definition(
    job_name: str,
    command: str | None = None,
    job_type: JobType = JobType.COMMAND,
    machine: str = "",
    description: str = "",
    calendar: str | None = None,
    start_times: list[str] | None = None,
    condition: str | None = None,
    std_out_file: str | None = None,
    std_err_file: str | None = None,
    owner: str | None = None,
    box_name: str | None = None,
    max_run_alarm: int | None = None,
    alarm_if_fail: bool = True,
    timezone: str | None = None,
    notification_emails: list[str] | None = None,
    notification_method: NotificationMethod = NotificationMethod.EMAIL,
    run_windows: list[str] | None = None,
    additional_attributes: dict[str, Any] | None = None,
) -> str:
    """
    Create a JIL job definition for Autosys.

    Args:
        job_name: Name of the Autosys job
        command: Command to run (for command jobs)
        job_type: Type of job (command, box, etc.)
        machine: Machine or group to run the job on
        description: Job description
        calendar: Calendar to use for scheduling
        start_times: List of start times (HH:MM)
        condition: Job dependency condition
        std_out_file: Path to redirect stdout
        std_err_file: Path to redirect stderr
        owner: Job owner
        box_name: Name of containing box job
        max_run_alarm: Maximum runtime in minutes
        alarm_if_fail: Send alarm if job fails
        timezone: Job timezone
        notification_emails: List of emails for notifications
        notification_method: Method for sending notifications
        run_windows: List of run windows in format "hh:mm-hh:mm"
        additional_attributes: Any additional JIL attributes

    Returns:
        JIL definition as a string
    """
    if job_type == JobType.COMMAND and not command:
        raise ValueError("Command must be specified for command jobs")

    if job_type == JobType.BOX and command:
        raise ValueError("Box jobs cannot have commands")

    # Start with the insert statement
    jil = [f"insert_job: {jil_escape(job_name)} job_type: {job_type}"]

    # Add basic attributes
    if machine:
        jil.append(f"machine: {jil_escape(machine)}")

    if box_name:
        jil.append(f"box_name: {jil_escape(box_name)}")

    if command and job_type == JobType.COMMAND:
        jil.append(f"command: {jil_escape(command)}")

    if description:
        jil.append(f"description: {jil_escape(description)}")

    if owner:
        jil.append(f"owner: {jil_escape(owner)}")

    # Add scheduling attributes
    if calendar:
        jil.append("date_conditions: 1")
        jil.append(f"run_calendar: {jil_escape(calendar)}")

    if start_times:
        jil.append(f"start_times: {','.join(start_times)}")

    if timezone:
        jil.append(f"timezone: {jil_escape(timezone)}")

    if condition:
        jil.append(f"condition: {jil_escape(condition)}")

    # Add run control attributes
    if max_run_alarm:
        jil.append(f"max_run_alarm: {max_run_alarm}")

    if std_out_file:
        jil.append(f"std_out_file: {jil_escape(std_out_file)}")

    if std_err_file:
        jil.append(f"std_err_file: {jil_escape(std_err_file)}")

    # Add notification attributes
    if alarm_if_fail:
        jil.append("alarm_if_fail: 1")
    else:
        jil.append("alarm_if_fail: 0")

    if notification_emails:
        notification_line = f"notification: {notification_method}"
        if notification_method == NotificationMethod.EMAIL:
            notification_line += f", {','.join(notification_emails)}"
        jil.append(notification_line)

    # Add run windows
    if run_windows:
        jil.append(f"run_window: {','.join(run_windows)}")

    # Add any additional attributes
    if additional_attributes:
        for key, value in additional_attributes.items():
            if isinstance(value, bool):
                value = 1 if value else 0
            elif isinstance(value, (list, tuple)):
                value = ",".join(str(v) for v in value)
            jil.append(f"{key}: {jil_escape(str(value))}")

    return "\n".join(jil) + "\n"


def parse_jil_file(file_path: str | Path) -> list[dict[str, Any]]:
    """
    Parse a JIL file and extract job definitions.

    Args:
        file_path: Path to JIL file

    Returns:
        List of job definitions as dictionaries
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"JIL file not found: {file_path}")

    with open(file_path) as f:
        content = f.read()

    # Split the content into job definitions
    job_blocks = re.split(r"^\s*insert_job:", content, flags=re.MULTILINE)[1:]

    jobs = []
    for block in job_blocks:
        job_def = {}

        # Process the first line which has the job name and type
        first_line = block.split("\n", 1)[0].strip()
        first_line_parts = first_line.split()

        if len(first_line_parts) >= 3 and first_line_parts[-2] == "job_type:":
            job_def["job_name"] = first_line_parts[0].rstrip()
            job_def["job_type"] = first_line_parts[-1]

        # Process the remaining attributes
        lines = block.split("\n")
        for line in lines[1:]:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if ":" in line:
                key, value = line.split(":", 1)
                job_def[key.strip()] = value.strip()

        jobs.append(job_def)

    return jobs


def generate_autosys_cli_command(
    job_name: str,
    action: str = "auto_sysval",
    instance: str | None = None,
    options: dict[str, Any] | None = None,
) -> str:
    """
    Generate an Autosys CLI command for job management.

    Args:
        job_name: Name of the job to manage
        action: Autosys action (e.g., auto_sysval, auto_hold, etc.)
        instance: Autosys instance name
        options: Additional command options

    Returns:
        Autosys CLI command as a string
    """
    cmd_parts = [action]

    if instance:
        cmd_parts.extend(["-S", instance])

    if options:
        for key, value in options.items():
            if len(key) == 1:
                cmd_parts.append(f"-{key}")
            else:
                cmd_parts.append(f"--{key}")

            if value is not True:
                cmd_parts.append(str(value))

    cmd_parts.append(job_name)

    return " ".join(cmd_parts)


def run_autosys_command(
    command: str | list[str], check: bool = True, capture_output: bool = True
) -> subprocess.CompletedProcess[str]:
    """Run an Autosys command and return the result.

    Args:
        command: Command to run, either as a string or list of arguments
        check: Whether to check the return code
        capture_output: Whether to capture stdout/stderr

    Returns:
        CompletedProcess instance with results
    """
    # If command is a string, split it into a list for safer execution
    cmd_args = command if isinstance(command, list) else shlex.split(command)

    result = subprocess.run(
        cmd_args, shell=False, check=check, capture_output=capture_output, text=True
    )
    return result


def generate_python_job(
    job_name: str,
    script_path: str,
    arguments: list[str] | None = None,
    environment: dict[str, str] | None = None,
    virtual_env: str | None = None,
    **kwargs: Any,
) -> str:
    """
    Generate a JIL definition for a Python job.

    Args:
        job_name: Name of the Autosys job
        script_path: Path to Python script
        arguments: Command line arguments for the script
        environment: Environment variables for the job
        virtual_env: Virtual environment path
        **kwargs: Additional arguments for create_jil_definition

    Returns:
        JIL definition as a string
    """
    # Build the command
    if virtual_env:
        # Windows-friendly venv activation
        if os.name == "nt":
            activate_path = os.path.join(virtual_env, "Scripts", "activate")
            command = f'cmd.exe /c "call {activate_path} && python {script_path}'
        else:
            activate_path = os.path.join(virtual_env, "bin", "activate")
            command = f". {activate_path} && python {script_path}"
    else:
        command = f"python {script_path}"

    # Add arguments
    if arguments:
        command += " " + " ".join(arguments)

    # Close command quote if using venv on Windows
    if virtual_env and os.name == "nt":
        command += '"'

    # Build environment setup
    if environment:
        env_setup = ""
        for key, value in environment.items():
            if os.name == "nt":
                env_setup += f"set {key}={value} && "
            else:
                env_setup += f'export {key}="{value}" && '
        command = env_setup + command

    # Generate the JIL definition
    return create_jil_definition(
        job_name=job_name, command=command, job_type=JobType.COMMAND, **kwargs
    )


def create_dependency_chain(job_names: list[str], **kwargs: Any) -> list[str]:
    """
    Create a chain of dependent jobs where each job depends on the success
    of the previous job.

    Args:
        job_names: List of job names in the chain
        **kwargs: Additional arguments for create_jil_definition

    Returns:
        List of JIL definitions
    """
    if len(job_names) < 2:
        raise ValueError("At least two jobs are needed for a dependency chain")

    jil_defs = []

    # Create the first job with no conditions
    jil_defs.append(create_jil_definition(job_name=job_names[0], **kwargs))

    # Create the remaining jobs with dependencies
    for i in range(1, len(job_names)):
        condition = f"success({job_names[i - 1]})"
        jil_defs.append(create_jil_definition(job_name=job_names[i], condition=condition, **kwargs))

    return jil_defs


def create_job_box(
    box_name: str,
    job_names: list[str],
    start_times: list[str] | None = None,
    calendar: str | None = None,
    **kwargs: Any,
) -> list[str]:
    """
    Create a job box containing multiple jobs.

    Args:
        box_name: Name of the box job
        job_names: Names of jobs to include in the box
        start_times: Start times for the box
        calendar: Calendar for the box
        **kwargs: Additional arguments for create_jil_definition

    Returns:
        List of JIL definitions including the box and its jobs
    """
    jil_defs = []

    # Create the box job
    jil_defs.append(
        create_jil_definition(
            job_name=box_name,
            job_type=JobType.BOX,
            start_times=start_times,
            calendar=calendar,
            **kwargs,
        )
    )

    # Create the jobs inside the box
    for job_name in job_names:
        jil_defs.append(create_jil_definition(job_name=job_name, box_name=box_name, **kwargs))

    return jil_defs


def create_daily_job(
    job_name: str,
    command: str,
    start_time: str,
    days_of_week: list[str] | None = None,
    **kwargs: Any,
) -> str:
    """
    Create a job that runs daily at a specific time.

    Args:
        job_name: Name of the job
        command: Command to run
        start_time: Time to start the job (HH:MM)
        days_of_week: List of days to run (mon, tue, wed, thu, fri, sat, sun)
        **kwargs: Additional arguments for create_jil_definition

    Returns:
        JIL definition as a string
    """
    additional_attributes = kwargs.pop("additional_attributes", {})

    if days_of_week:
        valid_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        days = [day.lower() for day in days_of_week]
        invalid_days = [day for day in days if day not in valid_days]

        if invalid_days:
            raise ValueError(f"Invalid days of week: {', '.join(invalid_days)}")

        for day in valid_days:
            additional_attributes[f"run_{day}"] = day in days

    return create_jil_definition(
        job_name=job_name,
        command=command,
        start_times=[start_time],
        additional_attributes=additional_attributes,
        **kwargs,
    )
