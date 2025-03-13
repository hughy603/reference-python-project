"""
Unit tests for logging_utils module.
"""

import json
import logging
import sys
from io import StringIO

import pytest

from enterprise_data_engineering.common_utils.logging_utils import (
    AutomationFriendlyJsonFormatter,
    configure_logging,
)


class TestAutomationFriendlyJsonFormatter:
    """Tests for the AutomationFriendlyJsonFormatter class."""

    def test_basic_formatting(self):
        """Test basic JSON log formatting with a simple message."""
        # Create formatter
        formatter = AutomationFriendlyJsonFormatter()

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Format the record
        formatted = formatter.format(record)
        parsed = json.loads(formatted)

        # Check basic fields
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "Test message"
        assert parsed["logger"] == "test_logger"
        assert "timestamp" in parsed
        assert "line_number" in parsed
        assert parsed["line_number"] == 42
        assert "file" in parsed
        assert parsed["file"] == "test_path.py"

    def test_with_exception_info(self):
        """Test JSON formatting with exception information."""
        formatter = AutomationFriendlyJsonFormatter()

        # Create exception info
        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = sys.exc_info()

        # Create a log record with exception info
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test_path.py",
            lineno=42,
            msg="Exception occurred",
            args=(),
            exc_info=exc_info,
        )

        # Format the record
        formatted = formatter.format(record)
        parsed = json.loads(formatted)

        # Check exception fields
        assert parsed["level"] == "ERROR"
        assert parsed["message"] == "Exception occurred"
        assert "exception" in parsed
        assert "ValueError: Test exception" in parsed["exception"]
        assert "traceback" in parsed

    def test_with_extra_fields(self):
        """Test JSON formatting with extra fields added to the record."""
        formatter = AutomationFriendlyJsonFormatter()

        # Create a log record with extra fields
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_path.py",
            lineno=42,
            msg="Test message with extras",
            args=(),
            exc_info=None,
        )

        # Add extra fields
        record.extra_field1 = "value1"
        record.extra_field2 = 42

        # Format the record
        formatted = formatter.format(record)
        parsed = json.loads(formatted)

        # Check extra fields
        assert parsed["extra_field1"] == "value1"
        assert parsed["extra_field2"] == 42

    def test_with_job_ids(self, monkeypatch):
        """Test JSON formatting with job and execution IDs from environment."""
        # Set environment variables
        monkeypatch.setenv("AUTOSYS_JOB_ID", "job-123")
        monkeypatch.setenv("AUTOSYS_EXECUTION_ID", "exec-456")

        formatter = AutomationFriendlyJsonFormatter()

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_path.py",
            lineno=42,
            msg="Test message with job IDs",
            args=(),
            exc_info=None,
        )

        # Format the record
        formatted = formatter.format(record)
        parsed = json.loads(formatted)

        # Check job ID fields
        assert parsed["job_id"] == "job-123"
        assert parsed["execution_id"] == "exec-456"

    def test_with_custom_env_variables(self, monkeypatch):
        """Test JSON formatting with custom environment variable names."""
        # Set environment variables
        monkeypatch.setenv("CUSTOM_JOB_ID", "custom-job-123")
        monkeypatch.setenv("CUSTOM_EXEC_ID", "custom-exec-456")

        formatter = AutomationFriendlyJsonFormatter(
            job_id_env="CUSTOM_JOB_ID", execution_id_env="CUSTOM_EXEC_ID"
        )

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_path.py",
            lineno=42,
            msg="Test message with custom job IDs",
            args=(),
            exc_info=None,
        )

        # Format the record
        formatted = formatter.format(record)
        parsed = json.loads(formatted)

        # Check job ID fields
        assert parsed["job_id"] == "custom-job-123"
        assert parsed["execution_id"] == "custom-exec-456"


class TestConfigureLogging:
    """Tests for the configure_logging function."""

    @pytest.fixture(autouse=True)
    def reset_logging(self):
        """Reset logging configuration before and after each test."""
        # Store original loggers and handlers
        root_handlers = list(logging.root.handlers)

        # Yield control to the test
        yield

        # Cleanup - reset to original state
        logging.root.handlers = root_handlers
        logging.root.setLevel(logging.WARNING)

    def test_basic_configuration(self):
        """Test basic logging configuration."""
        # Configure logging
        configure_logging(level=logging.INFO)

        # Check root logger level
        assert logging.root.level == logging.INFO

        # Should have at least one handler
        assert len(logging.root.handlers) > 0

        # First handler should be a StreamHandler
        assert isinstance(logging.root.handlers[0], logging.StreamHandler)

        # StreamHandler should use a standard formatter (not JSON)
        handler = logging.root.handlers[0]
        formatter = handler.formatter
        assert not isinstance(formatter, AutomationFriendlyJsonFormatter)

    def test_json_formatting(self):
        """Test logging configuration with JSON formatting."""
        # Configure logging with JSON format
        configure_logging(level=logging.DEBUG, json_format=True)

        # Check that handlers use JSON formatter
        assert len(logging.root.handlers) > 0

        # First handler should use JSON formatter
        handler = logging.root.handlers[0]
        assert isinstance(handler.formatter, AutomationFriendlyJsonFormatter)

    def test_with_log_file(self, tmp_path):
        """Test logging configuration with a log file."""
        # Create log file path
        log_file = str(tmp_path / "test.log")

        # Configure logging with a log file
        configure_logging(level=logging.INFO, log_file=log_file)

        # Should have at least two handlers (console and file)
        assert len(logging.root.handlers) >= 2

        # Check that one of the handlers is a FileHandler
        file_handlers = [h for h in logging.root.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) == 1

        # FileHandler should point to our log file
        assert file_handlers[0].baseFilename == log_file

    def test_automation_mode(self):
        """Test logging configuration in automation mode."""
        # Configure logging in automation mode
        configure_logging(level=logging.INFO, automation_mode=True)

        # Check that all handlers use JSON formatter
        assert len(logging.root.handlers) > 0

        for handler in logging.root.handlers:
            assert isinstance(handler.formatter, AutomationFriendlyJsonFormatter)

    def test_uncaught_exception_handler(self):
        """Test that the uncaught exception handler is set properly."""
        # Store original excepthook
        original_excepthook = sys.excepthook

        try:
            # Configure logging
            configure_logging()

            # Check that excepthook has been changed
            assert sys.excepthook != original_excepthook
        finally:
            # Restore original excepthook
            sys.excepthook = original_excepthook


# Capture logs for testing
class LogCapture:
    """Helper class to capture log messages for testing."""

    def __init__(self):
        """Initialize log capture."""
        self.log_stream = StringIO()
        self.handler = logging.StreamHandler(self.log_stream)
        self.logger = logging.getLogger("test_capture")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.handler)
        self.logger.propagate = False

    def get_logs(self) -> str:
        """Get captured log messages."""
        return self.log_stream.getvalue()

    def clear(self):
        """Clear captured logs."""
        self.log_stream = StringIO()
        self.handler.setStream(self.log_stream)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.logger.removeHandler(self.handler)
        self.handler.close()


def test_end_to_end_logging():
    """Test end-to-end logging with different configurations."""
    # Test with regular logging
    with LogCapture() as regular_capture:
        # Set root logger to use our capture
        configure_logging(level=logging.INFO)
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers
        root_logger.handlers = [regular_capture.handler]

        # Log messages
        root_logger.info("Test info message")
        root_logger.error("Test error message")

        # Restore original handlers
        root_logger.handlers = original_handlers

        # Check logs
        logs = regular_capture.get_logs()
        assert "Test info message" in logs
        assert "Test error message" in logs

    # Test with JSON logging
    with LogCapture() as json_capture:
        # Configure with JSON format
        configure_logging(level=logging.INFO, json_format=True)
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers

        # Create a handler with JSON formatter
        json_handler = logging.StreamHandler(json_capture.log_stream)
        json_handler.setFormatter(AutomationFriendlyJsonFormatter())
        root_logger.handlers = [json_handler]

        # Log messages
        root_logger.info("JSON info message")
        root_logger.error("JSON error message")

        # Restore original handlers
        root_logger.handlers = original_handlers

        # Check logs
        logs = json_capture.get_logs()

        # Each line should be valid JSON
        for line in logs.splitlines():
            if line.strip():
                parsed = json.loads(line)
                assert isinstance(parsed, dict)
                assert "message" in parsed
                assert "level" in parsed
                assert "timestamp" in parsed
