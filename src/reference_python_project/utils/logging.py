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
        super().__init__()
        self.job_id_env = job_id_env
        self.execution_id_env = execution_id_env

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add job tracking IDs if they exist in environment
        job_id = os.environ.get(self.job_id_env)
        if job_id:
            log_data["job_id"] = job_id

        execution_id = os.environ.get(self.execution_id_env)
        if execution_id:
            log_data["execution_id"] = execution_id

        # Add any exception info
        if record.exc_info:
            exc_type = record.exc_info[0]
            if exc_type is not None:
                log_data["exception"] = {
                    "type": exc_type.__name__,
                    "message": str(record.exc_info[1]),
                }

        # Add any extra attributes that were passed to the logger
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
    Configure application logging with options for automation environments.

    Args:
        level: The logging level (default: INFO)
        json_format: Whether to output logs in JSON format (default: False)
        log_file: Optional file path to write logs to
        automation_mode: Enable features specific to automation systems (default: False)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplication
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create handlers
    handlers = []

    # Always add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    handlers.append(console_handler)

    # Add file handler if specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            handlers.append(file_handler)
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not create log file {log_file}: {e}", file=sys.stderr)

    # Configure formatter
    if automation_mode or json_format:
        formatter = AutomationFriendlyJsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
        )

    # Apply formatter to all handlers
    for handler in handlers:
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    # Set excepthook to ensure uncaught exceptions are logged
    def exception_handler(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: types.TracebackType | None,
    ) -> None:
        root_logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        # In automation mode, reraise to ensure proper exit code
        if automation_mode:
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = exception_handler
