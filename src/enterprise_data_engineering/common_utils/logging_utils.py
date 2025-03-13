"""
Logging utilities for enterprise data engineering applications.

This module provides structured logging capabilities with support for both
console and file output, as well as JSON formatting for machine parsing.
"""

import json
import logging
import os
import sys
import types
from datetime import UTC, datetime
from typing import Any


class AutomationFriendlyJsonFormatter(logging.Formatter):
    """
    JSON formatter designed for automation systems like Autosys.

    Produces structured logs that can be easily parsed by log aggregation tools.
    Includes job_id and execution_id fields useful for job scheduling systems.
    """

    def __init__(
        self, job_id_env: str = "AUTOSYS_JOB_ID", execution_id_env: str = "AUTOSYS_EXECUTION_ID"
    ):
        """
        Initialize the formatter with environment variable names for job tracking.

        Args:
            job_id_env: Environment variable name for the job ID
            execution_id_env: Environment variable name for the execution ID
        """
        super().__init__()
        self.job_id_env = job_id_env
        self.execution_id_env = execution_id_env

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as a JSON string.

        Args:
            record: The log record to format

        Returns:
            A JSON string representation of the log record
        """
        # Get basic log record attributes
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        # Add source location
        log_data["file"] = record.pathname
        log_data["line"] = record.lineno
        log_data["function"] = record.funcName

        # Add exception info if present
        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            if exc_type is not None:
                log_data["exception"] = {
                    "type": exc_type.__name__,
                    "message": str(exc_value),
                    "traceback": self.formatException(record.exc_info),
                }

        # Add job tracking info if available
        job_id = os.environ.get(self.job_id_env)
        if job_id:
            log_data["job_id"] = job_id

        execution_id = os.environ.get(self.execution_id_env)
        if execution_id:
            log_data["execution_id"] = execution_id

        # Add any extra attributes from the record
        for key, value in record.__dict__.items():
            if key not in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "id",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            }:
                log_data[key] = value

        return json.dumps(log_data)


def configure_logging(
    level: int = logging.INFO,
    json_format: bool = False,
    log_file: str | None = None,
    automation_mode: bool = False,
) -> None:
    """
    Configure logging for the application.

    Args:
        level: The logging level (default: INFO)
        json_format: Whether to use JSON formatting (default: False)
        log_file: Path to a log file, if desired (default: None)
        automation_mode: Whether to configure for automation systems (default: False)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create handlers
    handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    handlers.append(console_handler)

    # File handler (if requested)
    if log_file:
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        handlers.append(file_handler)

    # Configure formatters
    if json_format or automation_mode:
        formatter = AutomationFriendlyJsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Apply formatter to all handlers
    for handler in handlers:
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    # Set up exception handling to log unhandled exceptions
    def exception_handler(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: types.TracebackType | None,
    ) -> None:
        """
        Log unhandled exceptions.

        Args:
            exc_type: The exception type
            exc_value: The exception value
            exc_traceback: The exception traceback
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't log keyboard interrupts
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        root_logger.critical(
            "Unhandled exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

    sys.excepthook = exception_handler

    # Log the configuration
    root_logger.debug(
        f"Logging configured: level={logging.getLevelName(level)}, "
        f"json_format={json_format}, log_file={log_file}, "
        f"automation_mode={automation_mode}"
    )
