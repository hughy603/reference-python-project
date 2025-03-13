"""
Common utility functions for enterprise data engineering projects.

This package provides reusable utility functions for data processing,
file handling, configuration management, and other common tasks.
"""

from .file_utils import (
    ensure_directory_exists,
    get_file_extension,
    list_files_with_extension,
    read_file_content,
    safe_file_write,
)

# Import config utilities conditionally to handle missing dependencies gracefully
try:
    from .config_utils import (
        get_env_config,
        load_config,
        merge_configs,
        validate_config,
    )

    has_config_utils = True
except ImportError:
    has_config_utils = False

# Import AWS utilities conditionally to handle missing dependencies gracefully
try:
    from .aws import (
        create_secret,
        delete_secret,
        get_aws_session,
        get_secret,
        list_s3_objects,
        list_secrets,
        rotate_secret_immediately,
        setup_secret_rotation,
        update_secret,
    )

    has_aws_utils = True
except ImportError:
    has_aws_utils = False

# Import logging utilities
try:
    from .logging_utils import (
        AutomationFriendlyJsonFormatter,
        configure_logging,
    )

    has_logging_utils = True
except ImportError:
    has_logging_utils = False

# Import autosys utilities
try:
    from .autosys import (
        Condition,
        JobStatus,
        JobType,
        NotificationMethod,
        create_daily_job,
        create_dependency_chain,
        create_jil_definition,
        create_job_box,
        generate_autosys_cli_command,
        generate_python_job,
        parse_jil_file,
        run_autosys_command,
    )

    has_autosys_utils = True
except ImportError:
    has_autosys_utils = False

__all__ = [
    # File utilities
    "ensure_directory_exists",
    "get_file_extension",
    "list_files_with_extension",
    "read_file_content",
    "safe_file_write",
]

# Add config utilities to __all__ if available
if has_config_utils:
    __all__.extend(
        [
            "get_env_config",
            "load_config",
            "merge_configs",
            "validate_config",
        ]
    )

# Add AWS utilities to __all__ if available
if has_aws_utils:
    __all__.extend(
        [
            "create_secret",
            "delete_secret",
            "get_aws_session",
            "get_secret",
            "list_s3_objects",
            "list_secrets",
            "rotate_secret_immediately",
            "setup_secret_rotation",
            "update_secret",
        ]
    )

# Add logging utilities to __all__ if available
if has_logging_utils:
    __all__.extend(
        [
            "AutomationFriendlyJsonFormatter",
            "configure_logging",
        ]
    )

# Add autosys utilities to __all__ if available
if has_autosys_utils:
    __all__.extend(
        [
            "Condition",
            "JobStatus",
            "JobType",
            "NotificationMethod",
            "create_daily_job",
            "create_dependency_chain",
            "create_jil_definition",
            "create_job_box",
            "generate_autosys_cli_command",
            "generate_python_job",
            "parse_jil_file",
            "run_autosys_command",
        ]
    )
